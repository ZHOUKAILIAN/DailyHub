from __future__ import annotations

import types
import unittest
from unittest.mock import patch

from checkin.xiaojuchongdian.src.checkin_task import SIGN_RECORD_PATH, XiaojuCheckInTask
from checkin.xiaojuchongdian.src.config import XiaojuConfig
from checkin.xiaojuchongdian.src.http import AuthError


class _NoopHttp:
    def post_json(self, **kwargs: object) -> object:
        raise AssertionError(f"unexpected HTTP call: {kwargs}")


class _CaptureHttp:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def post_json(self, *, url: str, body: dict, headers: dict) -> object:
        self.calls.append({"url": url, "body": body, "headers": headers})
        return types.SimpleNamespace(data={"ok": True})


def _cfg() -> XiaojuConfig:
    return XiaojuConfig(
        base_url="https://energy.xiaojukeji.com",
        ticket="ticket",
        token="token",
        token_id="token-id",
        app_id=121358,
        am_channel=1323124385,
        source="1323124385",
        ttid="driver",
        biz_line=250,
        city_id=5,
        am_ttid_header="ttid-header",
        am_did="device-id",
        am_dinfo="dinfo",
        app_version="1.8.7",
        am_lang="en",
        am_fs="10001",
        am_net="WIFI",
        am_nq="WIFI",
    )


def _main_payload(
    *,
    dates: list[str] | None = None,
    excitation_id: str | None = "eid-1",
    success: bool = True,
    status: int = 10000,
    code: str = "SERVICE_RUN_SUCCESS",
) -> dict:
    record_list = [{"signDate": d} for d in (dates or [])]
    item: dict = {"signTaskDTO": {"signRecordDTOList": record_list}}
    if excitation_id is not None:
        item["excitationId"] = excitation_id
    return {
        "success": success,
        "status": status,
        "code": code,
        "data": {"signInfo": [item]},
    }


class XiaojuCheckInTaskTests(unittest.TestCase):
    def test_execute_returns_already_signed_when_main_contains_today(self) -> None:
        task = XiaojuCheckInTask(_cfg(), _NoopHttp())
        payload = _main_payload(dates=["2026-03-09"])
        with patch.object(task, "_call_sign_main", return_value=payload) as mock_main:
            with patch.object(task, "_safe_record", return_value={"rows": []}) as mock_record:
                with patch.object(task, "_today_cn_date", return_value="2026-03-09"):
                    with patch.object(task, "_call_do_sign") as mock_sign:
                        result = task.execute(verify_record=True, record_days=7)

        self.assertTrue(result.success)
        self.assertEqual(result.status, "already_signed")
        self.assertEqual(result.data["already_signed"], True)
        mock_main.assert_called_once()
        mock_record.assert_called_once_with(7)
        mock_sign.assert_not_called()

    def test_execute_signs_when_not_signed_initially(self) -> None:
        task = XiaojuCheckInTask(_cfg(), _NoopHttp())
        before = _main_payload(dates=["2026-03-08"], excitation_id="ex1")
        after = _main_payload(dates=["2026-03-08", "2026-03-09"], excitation_id="ex1")
        with patch.object(task, "_call_sign_main", side_effect=[before, after]) as mock_main:
            with patch.object(
                task,
                "_call_do_sign",
                return_value={"success": True, "status": 10000},
            ) as mock_sign:
                with patch.object(task, "_today_cn_date", return_value="2026-03-09"):
                    result = task.execute()

        self.assertTrue(result.success)
        self.assertEqual(result.status, "signed")
        self.assertEqual(result.data["signed_after"], True)
        self.assertEqual(mock_main.call_count, 2)
        mock_sign.assert_called_once_with("ex1")

    def test_execute_fails_when_excitation_id_missing(self) -> None:
        task = XiaojuCheckInTask(_cfg(), _NoopHttp())
        before = _main_payload(dates=["2026-03-08"], excitation_id=None)
        with patch.object(task, "_call_sign_main", return_value=before):
            with patch.object(task, "_today_cn_date", return_value="2026-03-09"):
                result = task.execute()

        self.assertFalse(result.success)
        self.assertIn("cannot extract excitationId", result.message)

    def test_execute_accepts_platform_already_signed_message(self) -> None:
        task = XiaojuCheckInTask(_cfg(), _NoopHttp())
        before = _main_payload(dates=["2026-03-08"], excitation_id="ex2")
        after = _main_payload(dates=["2026-03-08"], excitation_id="ex2")
        with patch.object(task, "_call_sign_main", side_effect=[before, after]):
            with patch.object(
                task,
                "_call_do_sign",
                return_value={"success": True, "status": 10000, "msg": "已签到"},
            ):
                with patch.object(task, "_today_cn_date", return_value="2026-03-09"):
                    result = task.execute()

        self.assertTrue(result.success)
        self.assertEqual(result.status, "already_signed")

    def test_execute_converts_auth_error_to_failed_result(self) -> None:
        task = XiaojuCheckInTask(_cfg(), _NoopHttp())
        with patch.object(task, "_call_sign_main", side_effect=AuthError("invalid token")):
            result = task.execute()

        self.assertFalse(result.success)
        self.assertIn("authentication failed", result.message)

    def test_check_status_reports_today_signed(self) -> None:
        task = XiaojuCheckInTask(_cfg(), _NoopHttp())
        payload = _main_payload(dates=["2026-03-09"])
        with patch.object(task, "_call_sign_main", return_value=payload):
            with patch.object(task, "_today_cn_date", return_value="2026-03-09"):
                result = task.check_status()

        self.assertTrue(result.success)
        self.assertEqual(result.status, "status_ok")
        self.assertTrue(result.data["today_signed"])

    def test_safe_record_returns_warning_payload_on_exception(self) -> None:
        task = XiaojuCheckInTask(_cfg(), _NoopHttp())
        with patch.object(task, "_call_sign_record", side_effect=RuntimeError("boom")):
            result = task._safe_record(5)
        self.assertIn("_error", result)
        self.assertEqual(result["_error_type"], "unexpected")

    def test_is_success_payload_accepts_service_run_success_code(self) -> None:
        ok = XiaojuCheckInTask._is_success_payload(
            {"success": True, "code": "SERVICE_RUN_SUCCESS"},
            allow_status=set(),
        )
        self.assertTrue(ok)

    def test_extract_sign_dates_supports_multiple_record_shapes(self) -> None:
        payload = {
            "data": {
                "signInfo": [
                    {"signTaskDTO": {"signRecordDTOList": [{"signDate": "2026-03-01 10:00:00"}]}},
                    {"signRecordDTOList": [{"signDate": "2026-03-02"}]},
                ]
            }
        }
        dates = XiaojuCheckInTask._extract_sign_dates(payload)
        self.assertEqual(dates, ["2026-03-01", "2026-03-02"])

    def test_msg_indicates_already_signed_for_english_phrase(self) -> None:
        payload = {"message": "already signed today"}
        self.assertTrue(XiaojuCheckInTask._msg_indicates_already_signed(payload))

    def test_call_sign_record_builds_time_window_and_path(self) -> None:
        http = _CaptureHttp()
        task = XiaojuCheckInTask(_cfg(), http)
        with patch("checkin.xiaojuchongdian.src.checkin_task.time.time", return_value=1000.0):
            data = task._call_sign_record(days=0)

        self.assertEqual(data, {"ok": True})
        self.assertEqual(len(http.calls), 1)
        call = http.calls[0]
        self.assertTrue(call["url"].endswith(SIGN_RECORD_PATH))
        self.assertEqual(call["body"]["pageNo"], 1)
        self.assertEqual(call["body"]["pageSize"], 30)
        self.assertLess(call["body"]["startTime"], call["body"]["endTime"])
