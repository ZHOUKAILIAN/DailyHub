"""Task registry and execution router for Xiaoju check-in."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict

from .checkin_task import XiaojuCheckInTask
from .task_base import TaskModule, TaskResult


class TaskNotFoundError(ValueError):
    """Raised when the requested task name is not registered."""


@dataclass(frozen=True)
class TaskSpec:
    name: str
    task_type: str
    platform: str
    description: str
    factory: Callable[[], TaskModule]


TASK_SPECS: Dict[str, TaskSpec] = {
    "xiaoju.checkin": TaskSpec(
        name="xiaoju.checkin",
        task_type=XiaojuCheckInTask.TASK_TYPE,
        platform=XiaojuCheckInTask.PLATFORM,
        description=XiaojuCheckInTask.DESCRIPTION,
        factory=XiaojuCheckInTask.from_env,
    ),
}


class TaskRouter:
    def list_tasks(self) -> Dict[str, Dict[str, str]]:
        return {
            name: {
                "task_type": spec.task_type,
                "platform": spec.platform,
                "description": spec.description,
            }
            for name, spec in TASK_SPECS.items()
        }

    def run(self, task_name: str, **kwargs: object) -> TaskResult:
        task = self._build(task_name)
        return task.execute(**kwargs)

    def status(self, task_name: str, **kwargs: object) -> TaskResult:
        task = self._build(task_name)
        return task.check_status(**kwargs)

    @staticmethod
    def _build(task_name: str) -> TaskModule:
        spec = TASK_SPECS.get(task_name)
        if not spec:
            known = ", ".join(sorted(TASK_SPECS.keys()))
            raise TaskNotFoundError(f"unknown task: {task_name}. known tasks: {known}")
        return spec.factory()
