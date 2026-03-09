from __future__ import annotations

from datetime import datetime
import unittest

from checkin.xiaojuchongdian.src.task_base import TaskResult


class TaskResultTests(unittest.TestCase):
    def test_to_dict_keeps_payload_and_iso_timestamp(self) -> None:
        result = TaskResult(
            success=True,
            status="signed",
            message="ok",
            platform="xiaoju",
            task="checkin",
            data={"points": 1},
        )

        payload = result.to_dict()
        self.assertEqual(payload["data"], {"points": 1})
        self.assertEqual(payload["status"], "signed")
        self.assertEqual(payload["platform"], "xiaoju")
        datetime.fromisoformat(payload["timestamp"])
