from __future__ import annotations

import io
import os
import types
import unittest
from contextlib import redirect_stderr
from unittest.mock import patch

from checkin.xiaojuchongdian.src import logger


class LoggerTests(unittest.TestCase):
    def test_configure_logging_calls_basic_config_when_no_handlers(self) -> None:
        fake_root = types.SimpleNamespace(handlers=[], setLevel=lambda _: None)
        with patch.dict(os.environ, {"DAILYHUB_LOG_LEVEL": "DEBUG"}, clear=True):
            with patch("checkin.xiaojuchongdian.src.logger.logging.getLogger", return_value=fake_root):
                with patch("checkin.xiaojuchongdian.src.logger.logging.basicConfig") as mock_basic:
                    logger.configure_logging()
        mock_basic.assert_called_once()
        self.assertEqual(mock_basic.call_args.kwargs["level"], logger.logging.DEBUG)

    def test_configure_logging_warns_and_falls_back_on_invalid_level(self) -> None:
        fake_root = types.SimpleNamespace(handlers=[object()], setLevel=lambda _: None)
        err = io.StringIO()
        with patch.dict(os.environ, {"DAILYHUB_LOG_LEVEL": "BAD_LEVEL"}, clear=True):
            with patch("checkin.xiaojuchongdian.src.logger.logging.getLogger", return_value=fake_root):
                with redirect_stderr(err):
                    logger.configure_logging()

        output = err.getvalue()
        self.assertIn("not a valid log level", output)
