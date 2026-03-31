"""Xiaoju Charging daily check-in task module."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from .config import ConfigError, HttpConfig, XiaojuConfig
from .http import AuthError, HttpClient, HttpClientError
from .task_base import TaskModule, TaskResult

TASK_TYPE = "api-driven"
PLATFORM = "xiaoju"
DESCRIPTION = "小桔充电每日签到"

SIGN_MAIN_PATH = "/am/marketing/api/member/charge/activity/sign/main"
SIGN_DO_SIGN_PATH = "/am/marketing/api/member/charge/activity/sign/doSign"
SIGN_RECORD_PATH = "/excitation/api/excitation/signRecord"

# signRecord API returns at most 30 records per page; queries beyond this window
# are silently truncated. Callers must not pass days > SIGN_RECORD_MAX_DAYS
# without implementing pagination.
SIGN_RECORD_MAX_DAYS = 30

logger = logging.getLogger(__name__)


class XiaojuCheckInTask(TaskModule):
    TASK_TYPE = TASK_TYPE
    PLATFORM = PLATFORM
    DESCRIPTION = DESCRIPTION

    def __init__(self, xiaoju_config: XiaojuConfig, http_client: HttpClient) -> None:
        self.cfg = xiaoju_config
        self.http = http_client

    @classmethod
    def from_env(cls) -> "XiaojuCheckInTask":
        return cls(
            xiaoju_config=XiaojuConfig.from_env(),
            http_client=HttpClient(HttpConfig.from_env()),
        )

    def execute(self, **kwargs: Any) -> TaskResult:
        verify_record = bool(kwargs.get("verify_record", False))
        record_days = int(kwargs.get("record_days", SIGN_RECORD_MAX_DAYS))
        if record_days > SIGN_RECORD_MAX_DAYS:
            logger.warning(
                "record_days=%d exceeds max supported page size (%d); results will be truncated",
                record_days,
                SIGN_RECORD_MAX_DAYS,
            )
            record_days = SIGN_RECORD_MAX_DAYS
        data: Dict[str, Any] = {"verify_record": verify_record, "record_days": record_days}
        try:
            main_before = self._call_sign_main()
            data["main_before"] = main_before

            if not self._is_success_payload(main_before, allow_status={10000}):
                detail = self._payload_error_detail(main_before)
                return self._fail("failed", f"sign/main returned non-success payload: {detail}", data)

            today = self._today_cn_date()
            already_signed = self._is_today_signed(main_before, today=today)
            data["today"] = today
            data["already_signed"] = already_signed
            data["excitation_id"] = self._extract_excitation_id(main_before)

            if already_signed:
                if verify_record:
                    data["record"] = self._safe_record(record_days)
                return TaskResult(
                    success=True,
                    status="already_signed",
                    message="今日已签到，无需重复执行",
                    platform=self.PLATFORM,
                    task="checkin",
                    data=data,
                )

            excitation_id = data.get("excitation_id")
            if not excitation_id:
                return self._fail("failed", "cannot extract excitationId from sign/main", data)

            do_sign = self._call_do_sign(str(excitation_id))
            data["do_sign"] = do_sign

            if not self._is_success_payload(do_sign, allow_status={10000}):
                detail = self._payload_error_detail(do_sign)
                logger.error(
                    "doSign API returned non-success payload: code=%s msg=%s",
                    do_sign.get("code"),
                    do_sign.get("msg") or do_sign.get("message"),
                )
                return self._fail(
                    "failed",
                    f"doSign rejected: {detail}",
                    data,
                )

            main_after = self._call_sign_main()
            data["main_after"] = main_after
            signed_after = self._is_today_signed(main_after, today=today)
            data["signed_after"] = signed_after

            if verify_record:
                data["record"] = self._safe_record(record_days)

            if signed_after:
                return TaskResult(
                    success=True,
                    status="signed",
                    message="签到执行成功",
                    platform=self.PLATFORM,
                    task="checkin",
                    data=data,
                )

            if self._msg_indicates_already_signed(do_sign):
                return TaskResult(
                    success=True,
                    status="already_signed",
                    message="平台提示已签到（复核未命中当日记录，建议后续人工抽查）",
                    platform=self.PLATFORM,
                    task="checkin",
                    data=data,
                )

            return self._fail("failed", "doSign executed but post-check did not confirm sign-in", data)
        except AuthError as exc:
            logger.error("authentication error during check-in: %s", exc)
            return self._fail("failed", f"authentication failed: {exc}", data)
        except (HttpClientError, ConfigError) as exc:
            logger.error("http/config error during check-in: %s", exc)
            return self._fail("failed", str(exc), data)
        except Exception as exc:  # noqa: BLE001
            logger.exception(
                "unexpected xiaoju check-in error; partial state: today=%s already_signed=%s excitation_id=%s",
                data.get("today"),
                data.get("already_signed"),
                data.get("excitation_id"),
            )
            return self._fail("failed", f"unexpected error: {exc}", data)

    def check_status(self, **kwargs: Any) -> TaskResult:
        data: Dict[str, Any] = {}
        try:
            main = self._call_sign_main()
            data["main"] = main
            if not self._is_success_payload(main, allow_status={10000}):
                detail = self._payload_error_detail(main)
                return self._fail("failed", f"sign/main returned non-success payload: {detail}", data)

            today = self._today_cn_date()
            today_signed = self._is_today_signed(main, today=today)
            data["today"] = today
            data["today_signed"] = today_signed
            data["excitation_id"] = self._extract_excitation_id(main)
            return TaskResult(
                success=True,
                status="status_ok",
                message="状态查询成功",
                platform=self.PLATFORM,
                task="checkin",
                data=data,
            )
        except AuthError as exc:
            logger.error("authentication error during status check: %s", exc)
            return self._fail("failed", f"authentication failed: {exc}", data)
        except (HttpClientError, ConfigError) as exc:
            logger.error("http/config error during status check: %s", exc)
            return self._fail("failed", str(exc), data)
        except Exception as exc:  # noqa: BLE001
            logger.exception(
                "unexpected xiaoju status error; partial state: today=%s",
                data.get("today"),
            )
            return self._fail("failed", f"unexpected error: {exc}", data)

    def _call_sign_main(self) -> Dict[str, Any]:
        url = self.cfg.base_url.rstrip("/") + SIGN_MAIN_PATH
        return self.http.post_json(
            url=url,
            body=self._base_body(),
            headers=self._base_headers(),
        ).data

    def _call_do_sign(self, excitation_id: str) -> Dict[str, Any]:
        url = self.cfg.base_url.rstrip("/") + SIGN_DO_SIGN_PATH
        body = self._base_body()
        body["excitationId"] = excitation_id
        return self.http.post_json(
            url=url,
            body=body,
            headers=self._base_headers(),
        ).data

    def _call_sign_record(self, days: int) -> Dict[str, Any]:
        end_ms = int(time.time() * 1000)
        start_ms = end_ms - max(days, 1) * 24 * 60 * 60 * 1000
        url = self.cfg.base_url.rstrip("/") + SIGN_RECORD_PATH
        body = self._base_body()
        body.update(
            {
                "pageNo": 1,
                "pageSize": SIGN_RECORD_MAX_DAYS,
                "startTime": start_ms,
                "endTime": end_ms,
            }
        )
        return self.http.post_json(
            url=url,
            body=body,
            headers=self._base_headers(),
        ).data

    def _safe_record(self, days: int) -> Dict[str, Any]:
        try:
            return self._call_sign_record(days)
        except AuthError as exc:
            logger.error(
                "signRecord fetch failed due to authentication error — credentials may be expired: %s",
                exc,
            )
            return {"_error": f"authentication failed: {exc}", "_error_type": "auth"}
        except HttpClientError as exc:
            logger.warning("signRecord fetch failed (network/HTTP): %s", exc)
            return {"_warning": f"signRecord fetch failed: {exc}", "_error_type": "http"}
        except Exception as exc:  # noqa: BLE001
            logger.exception("signRecord fetch failed unexpectedly")
            return {"_error": f"unexpected error: {exc}", "_error_type": "unexpected"}

    def _base_body(self) -> Dict[str, Any]:
        return {
            "ticket": self.cfg.ticket,
            "token": self.cfg.token,
            "tokenId": self.cfg.token_id,
            "appId": self.cfg.app_id,
            "amChannel": self.cfg.am_channel,
            "source": self.cfg.source,
            "ttid": self.cfg.ttid,
            "bizLine": self.cfg.biz_line,
            "cityId": self.cfg.city_id,
        }

    def _base_headers(self) -> Dict[str, str]:
        return {
            "content-type": "application/json; charset=utf-8",
            "user-agent": "okhttp/3.14.9",
            "ticket": self.cfg.ticket,
            "am-ttid": self.cfg.am_ttid_header,
            "am-did": self.cfg.am_did,
            "am-dinfo": self.cfg.am_dinfo,
            "appversion": self.cfg.app_version,
            "am-lang": self.cfg.am_lang,
            "am-fs": self.cfg.am_fs,
            "am-net": self.cfg.am_net,
            "am-nq": self.cfg.am_nq,
        }

    @staticmethod
    def _is_success_payload(payload: Dict[str, Any], allow_status: set[int]) -> bool:
        if payload.get("success") is not True:
            return False
        raw_status = payload.get("status")
        if raw_status is not None:
            try:
                if int(raw_status) in allow_status:
                    return True
            except (ValueError, TypeError):
                pass
        code = str(payload.get("code", ""))
        return code == "SERVICE_RUN_SUCCESS"

    @classmethod
    def _payload_error_detail(cls, payload: Dict[str, Any]) -> str:
        status = payload.get("status")
        code = payload.get("code")
        msg = payload.get("msg") or payload.get("message")
        detail = f"status={status}, code={code}, msg={msg}"
        low = " ".join(
            [
                str(status or ""),
                str(code or ""),
                str(msg or ""),
            ]
        ).lower()
        if "ticket" in low or "token" in low:
            return f"{detail} (auth credential invalid/expired)"
        if "ad_min" in low or "am_did" in low or "am-did" in low or "设备" in str(msg or ""):
            return (
                f"{detail} (device header mismatch; verify DAILYHUB_XIAOJU_AM_DID "
                "and DAILYHUB_XIAOJU_AM_DINFO from real app request)"
            )
        return detail

    @staticmethod
    def _extract_excitation_id(main_payload: Dict[str, Any]) -> Optional[str]:
        sign_info = (main_payload.get("data") or {}).get("signInfo") or []
        if not sign_info:
            logger.warning(
                "sign/main response has empty or missing signInfo; data keys: %s",
                list((main_payload.get("data") or {}).keys()),
            )
            return None
        excitation_id = sign_info[0].get("excitationId")
        if excitation_id is None:
            logger.warning(
                "signInfo[0] has no excitationId; available keys: %s",
                list(sign_info[0].keys()),
            )
        return str(excitation_id) if excitation_id is not None else None

    @staticmethod
    def _extract_sign_dates(main_payload: Dict[str, Any]) -> List[str]:
        dates: List[str] = []
        sign_info = (main_payload.get("data") or {}).get("signInfo") or []
        for item in sign_info:
            task = item.get("signTaskDTO") or {}
            records = task.get("signRecordDTOList") or item.get("signRecordDTOList") or []
            for rec in records:
                sign_date = str(rec.get("signDate") or "").strip()
                if sign_date:
                    dates.append(sign_date[:10])
        return dates

    def _is_today_signed(self, main_payload: Dict[str, Any], today: Optional[str] = None) -> bool:
        current_day = today or self._today_cn_date()
        return current_day in set(self._extract_sign_dates(main_payload))

    @staticmethod
    def _msg_indicates_already_signed(payload: Dict[str, Any]) -> bool:
        text = " ".join(
            [
                str(payload.get("msg", "")),
                str(payload.get("message", "")),
                str(payload.get("code", "")),
                str(payload.get("name", "")),
            ]
        )
        return ("已签" in text) or ("already" in text.lower() and "sign" in text.lower())

    @staticmethod
    def _today_cn_date() -> str:
        cn_tz = timezone(timedelta(hours=8))
        return datetime.now(cn_tz).date().isoformat()

    def _fail(self, status: str, message: str, data: Dict[str, Any]) -> TaskResult:
        return TaskResult(
            success=False,
            status=status,
            message=message,
            platform=self.PLATFORM,
            task="checkin",
            data=data,
        )
