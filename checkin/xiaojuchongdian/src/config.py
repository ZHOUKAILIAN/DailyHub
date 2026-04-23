"""Configuration loading for Xiaoju Charging check-in."""

from __future__ import annotations

import logging
import os
import shlex
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigError(ValueError):
    """Raised when required runtime configuration is missing or invalid."""


def _parse_env_assignment(raw_line: str) -> tuple[str, str] | None:
    line = raw_line.strip()
    if not line or line.startswith("#"):
        return None
    if line.startswith("export "):
        line = line[len("export ") :].strip()
    if "=" not in line:
        return None
    key, value = line.split("=", 1)
    key = key.strip()
    if not key:
        return None
    value = value.strip()
    if not value:
        return key, ""
    try:
        parsed = shlex.split(value, comments=False, posix=True)
    except ValueError:
        parsed = [value]
    if len(parsed) == 1:
        return key, parsed[0]
    return key, value


def _load_env_file(path: Path) -> bool:
    if not path.is_file():
        return False
    loaded_any = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        parsed = _parse_env_assignment(raw_line)
        if not parsed:
            continue
        key, value = parsed
        os.environ.setdefault(key, value)
        loaded_any = True
    if loaded_any:
        logger.info("loaded Xiaoju env defaults from %s", path)
    return loaded_any


def _bootstrap_env() -> None:
    current_file = Path(__file__).resolve()
    repo_root = current_file.parents[3]
    candidates = [
        Path.cwd() / ".env",
        repo_root / ".env",
        repo_root.parent / ".env",
        Path("/root/DailyHub/.env"),
        Path("/root/.env"),
    ]
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve(strict=False)
        if resolved in seen:
            continue
        seen.add(resolved)
        _load_env_file(resolved)


_BOOTSTRAPPED_ENV = False


def _ensure_env_bootstrapped() -> None:
    global _BOOTSTRAPPED_ENV
    if _BOOTSTRAPPED_ENV:
        return
    _bootstrap_env()
    _BOOTSTRAPPED_ENV = True


def _get_required_env(name: str) -> str:
    _ensure_env_bootstrapped()
    value = os.getenv(name, "").strip()
    if not value:
        raise ConfigError(f"missing required env: {name}")
    return value


def _get_optional_env(name: str, default: str) -> str:
    _ensure_env_bootstrapped()
    raw = os.getenv(name)
    if raw is None:
        return default
    value = raw.strip()
    if not value:
        logger.warning(
            "env %s is set but contains only whitespace — using default value %r",
            name,
            default,
        )
        return default
    return value


def _get_int_env(name: str, default: int) -> int:
    _ensure_env_bootstrapped()
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigError(f"invalid int env {name}={raw!r}") from exc


def _get_float_env(name: str, default: float) -> float:
    _ensure_env_bootstrapped()
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise ConfigError(f"invalid float env {name}={raw!r}") from exc


@dataclass(frozen=True)
class HttpConfig:
    timeout_seconds: int = 30
    retries: int = 3
    backoff_seconds: float = 1.0
    backoff_factor: float = 2.0

    @classmethod
    def from_env(cls) -> "HttpConfig":
        return cls(
            timeout_seconds=_get_int_env("DAILYHUB_HTTP_TIMEOUT_SECONDS", 30),
            retries=_get_int_env("DAILYHUB_HTTP_RETRIES", 3),
            backoff_seconds=_get_float_env("DAILYHUB_HTTP_BACKOFF_SECONDS", 1.0),
            backoff_factor=_get_float_env("DAILYHUB_HTTP_BACKOFF_FACTOR", 2.0),
        )


@dataclass(frozen=True)
class XiaojuConfig:
    base_url: str
    ticket: str
    token: str
    token_id: str
    app_id: int
    am_channel: int
    source: str
    ttid: str
    biz_line: int
    city_id: int
    am_ttid_header: str
    am_did: str
    am_dinfo: str
    app_version: str
    am_lang: str
    am_fs: str
    am_net: str
    am_nq: str

    @classmethod
    def from_env(cls) -> "XiaojuConfig":
        return cls(
            base_url=_get_optional_env(
                "DAILYHUB_XIAOJU_BASE_URL", "https://energy.xiaojukeji.com"
            ),
            ticket=_get_required_env("DAILYHUB_XIAOJU_TICKET"),
            token=_get_required_env("DAILYHUB_XIAOJU_TOKEN"),
            token_id=_get_required_env("DAILYHUB_XIAOJU_TOKEN_ID"),
            app_id=_get_int_env("DAILYHUB_XIAOJU_APP_ID", 121358),
            am_channel=_get_int_env("DAILYHUB_XIAOJU_AM_CHANNEL", 1323124385),
            source=_get_optional_env("DAILYHUB_XIAOJU_SOURCE", "1323124385"),
            ttid=_get_optional_env("DAILYHUB_XIAOJU_TTID", "driver"),
            biz_line=_get_int_env("DAILYHUB_XIAOJU_BIZ_LINE", 250),
            city_id=_get_int_env("DAILYHUB_XIAOJU_CITY_ID", 5),
            am_ttid_header=_get_optional_env(
                "DAILYHUB_XIAOJU_AM_TTID", "10001@xjcd_android_1.8.7_1201080701"
            ),
            # am_did is the device fingerprint — must be unique per account to avoid
            # anti-fraud account linkage. Capture from real app traffic and set via env.
            am_did=_get_required_env("DAILYHUB_XIAOJU_AM_DID"),
            am_dinfo=_get_optional_env(
                "DAILYHUB_XIAOJU_AM_DINFO", "google-sdk_gphone64_arm64@16@1080"
            ),
            app_version=_get_optional_env("DAILYHUB_XIAOJU_APP_VERSION", "1.8.7"),
            am_lang=_get_optional_env("DAILYHUB_XIAOJU_AM_LANG", "en"),
            am_fs=_get_optional_env("DAILYHUB_XIAOJU_AM_FS", "10001"),
            am_net=_get_optional_env("DAILYHUB_XIAOJU_AM_NET", "WIFI"),
            am_nq=_get_optional_env("DAILYHUB_XIAOJU_AM_NQ", "WIFI"),
        )
