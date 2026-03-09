from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from checkin.xiaojuchongdian.src import config


class ConfigEnvHelperTests(unittest.TestCase):
    def test_get_required_env_raises_when_missing(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(config.ConfigError):
                config._get_required_env("DAILYHUB_XIAOJU_TICKET")

    def test_get_optional_env_returns_default_and_warns_on_whitespace(self) -> None:
        with patch.dict(os.environ, {"DAILYHUB_XIAOJU_SOURCE": "   "}, clear=True):
            with patch("checkin.xiaojuchongdian.src.config.logger.warning") as mock_warning:
                value = config._get_optional_env("DAILYHUB_XIAOJU_SOURCE", "1323124385")

        self.assertEqual(value, "1323124385")
        mock_warning.assert_called_once()

    def test_get_int_env_raises_on_invalid_value(self) -> None:
        with patch.dict(os.environ, {"DAILYHUB_HTTP_RETRIES": "abc"}, clear=True):
            with self.assertRaises(config.ConfigError):
                config._get_int_env("DAILYHUB_HTTP_RETRIES", 3)

    def test_get_float_env_uses_default_when_empty(self) -> None:
        with patch.dict(os.environ, {"DAILYHUB_HTTP_BACKOFF_FACTOR": "   "}, clear=True):
            value = config._get_float_env("DAILYHUB_HTTP_BACKOFF_FACTOR", 2.0)
        self.assertEqual(value, 2.0)


class HttpConfigTests(unittest.TestCase):
    def test_http_config_from_env_reads_values(self) -> None:
        with patch.dict(
            os.environ,
            {
                "DAILYHUB_HTTP_TIMEOUT_SECONDS": "12",
                "DAILYHUB_HTTP_RETRIES": "5",
                "DAILYHUB_HTTP_BACKOFF_SECONDS": "0.5",
                "DAILYHUB_HTTP_BACKOFF_FACTOR": "3.0",
            },
            clear=True,
        ):
            cfg = config.HttpConfig.from_env()

        self.assertEqual(cfg.timeout_seconds, 12)
        self.assertEqual(cfg.retries, 5)
        self.assertEqual(cfg.backoff_seconds, 0.5)
        self.assertEqual(cfg.backoff_factor, 3.0)


class XiaojuConfigTests(unittest.TestCase):
    def test_xiaoju_config_from_env_uses_defaults_and_required_fields(self) -> None:
        with patch.dict(
            os.environ,
            {
                "DAILYHUB_XIAOJU_TICKET": "ticket",
                "DAILYHUB_XIAOJU_TOKEN": "token",
                "DAILYHUB_XIAOJU_TOKEN_ID": "token-id",
                "DAILYHUB_XIAOJU_AM_DID": "did-value",
            },
            clear=True,
        ):
            cfg = config.XiaojuConfig.from_env()

        self.assertEqual(cfg.base_url, "https://energy.xiaojukeji.com")
        self.assertEqual(cfg.ticket, "ticket")
        self.assertEqual(cfg.token, "token")
        self.assertEqual(cfg.token_id, "token-id")
        self.assertEqual(cfg.am_did, "did-value")
        self.assertEqual(cfg.biz_line, 250)
        self.assertEqual(cfg.city_id, 5)

    def test_xiaoju_config_from_env_raises_when_required_missing(self) -> None:
        with patch.dict(
            os.environ,
            {
                "DAILYHUB_XIAOJU_TICKET": "ticket",
                "DAILYHUB_XIAOJU_TOKEN": "token",
                "DAILYHUB_XIAOJU_TOKEN_ID": "token-id",
            },
            clear=True,
        ):
            with self.assertRaises(config.ConfigError):
                config.XiaojuConfig.from_env()
