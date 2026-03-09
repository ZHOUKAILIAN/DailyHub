from __future__ import annotations

import sys
import unittest
from unittest.mock import patch

from checkin.xiaojuchongdian.src import main
from checkin.xiaojuchongdian.src.task_base import TaskResult


def _result(*, success: bool, status: str = "ok") -> TaskResult:
    return TaskResult(
        success=success,
        status=status,
        message="msg",
        platform="xiaoju",
        task="checkin",
        data={"a": 1},
    )


class MainCliTests(unittest.TestCase):
    def test_list_command_returns_zero(self) -> None:
        fake_router = type(
            "FakeRouter",
            (),
            {"list_tasks": lambda self: {"xiaoju.checkin": {"task_type": "api-driven"}}},
        )()

        with patch.object(sys, "argv", ["prog", "list"]):
            with patch("checkin.xiaojuchongdian.src.main.configure_logging"):
                with patch("checkin.xiaojuchongdian.src.main.TaskRouter", return_value=fake_router):
                    with patch("checkin.xiaojuchongdian.src.main._print_json") as mock_print:
                        code = main.main()

        self.assertEqual(code, 0)
        mock_print.assert_called_once()

    def test_run_command_success_returns_zero(self) -> None:
        class FakeRouter:
            def run(self, task: str, **kwargs: object) -> TaskResult:
                self.task = task
                self.kwargs = kwargs
                return _result(success=True, status="signed")

        fake_router = FakeRouter()
        with patch.object(sys, "argv", ["prog", "run", "--task", "xiaoju.checkin"]):
            with patch("checkin.xiaojuchongdian.src.main.configure_logging"):
                with patch("checkin.xiaojuchongdian.src.main.TaskRouter", return_value=fake_router):
                    with patch("checkin.xiaojuchongdian.src.main._print_json"):
                        code = main.main()

        self.assertEqual(code, 0)
        self.assertEqual(fake_router.task, "xiaoju.checkin")
        self.assertEqual(fake_router.kwargs["record_days"], 30)
        self.assertFalse(fake_router.kwargs["verify_record"])

    def test_run_command_exception_returns_one_and_prints_error(self) -> None:
        class FakeRouter:
            def run(self, task: str, **kwargs: object) -> TaskResult:
                raise RuntimeError("boom")

        with patch.object(sys, "argv", ["prog", "run", "--task", "xiaoju.checkin"]):
            with patch("checkin.xiaojuchongdian.src.main.configure_logging"):
                with patch("checkin.xiaojuchongdian.src.main.TaskRouter", return_value=FakeRouter()):
                    with patch("checkin.xiaojuchongdian.src.main._print_json") as mock_print:
                        code = main.main()

        self.assertEqual(code, 1)
        payload = mock_print.call_args.args[0]
        self.assertEqual(payload["success"], False)
        self.assertIn("boom", payload["error"])

    def test_status_command_returns_one_when_result_failed(self) -> None:
        class FakeRouter:
            def status(self, task: str, **kwargs: object) -> TaskResult:
                return _result(success=False, status="failed")

        with patch.object(sys, "argv", ["prog", "status", "--task", "xiaoju.checkin"]):
            with patch("checkin.xiaojuchongdian.src.main.configure_logging"):
                with patch("checkin.xiaojuchongdian.src.main.TaskRouter", return_value=FakeRouter()):
                    with patch("checkin.xiaojuchongdian.src.main._print_json"):
                        code = main.main()

        self.assertEqual(code, 1)
