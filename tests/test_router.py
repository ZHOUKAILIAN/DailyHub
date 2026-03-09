from __future__ import annotations

import unittest
from unittest.mock import patch

from checkin.xiaojuchongdian.src import router
from checkin.xiaojuchongdian.src.task_base import TaskResult


class DummyTask:
    def execute(self, **kwargs: object) -> TaskResult:
        return TaskResult(
            success=True,
            status="ok",
            message=str(kwargs),
            platform="xiaoju",
            task="checkin",
        )

    def check_status(self, **kwargs: object) -> TaskResult:
        return TaskResult(
            success=True,
            status="status_ok",
            message=str(kwargs),
            platform="xiaoju",
            task="checkin",
        )


class TaskRouterTests(unittest.TestCase):
    def test_list_tasks_contains_xiaoju_checkin(self) -> None:
        data = router.TaskRouter().list_tasks()
        self.assertIn("xiaoju.checkin", data)
        self.assertEqual(data["xiaoju.checkin"]["task_type"], "api-driven")

    def test_run_delegates_to_task_execute(self) -> None:
        spec = router.TaskSpec(
            name="dummy.task",
            task_type="api-driven",
            platform="dummy",
            description="dummy",
            factory=DummyTask,
        )
        with patch.dict(router.TASK_SPECS, {"dummy.task": spec}, clear=True):
            result = router.TaskRouter().run("dummy.task", verify_record=True, record_days=5)

        self.assertTrue(result.success)
        self.assertIn("verify_record", result.message)
        self.assertIn("record_days", result.message)

    def test_status_delegates_to_task_check_status(self) -> None:
        spec = router.TaskSpec(
            name="dummy.task",
            task_type="api-driven",
            platform="dummy",
            description="dummy",
            factory=DummyTask,
        )
        with patch.dict(router.TASK_SPECS, {"dummy.task": spec}, clear=True):
            result = router.TaskRouter().status("dummy.task", quick=True)

        self.assertEqual(result.status, "status_ok")
        self.assertIn("quick", result.message)

    def test_build_raises_for_unknown_task_with_known_list(self) -> None:
        spec = router.TaskSpec(
            name="dummy.task",
            task_type="api-driven",
            platform="dummy",
            description="dummy",
            factory=DummyTask,
        )
        with patch.dict(router.TASK_SPECS, {"dummy.task": spec}, clear=True):
            with self.assertRaises(ValueError) as ctx:
                router.TaskRouter().run("unknown.task")
        self.assertIn("unknown task", str(ctx.exception))
        self.assertIn("dummy.task", str(ctx.exception))
