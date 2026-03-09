"""Base interfaces and result models for Xiaoju tasks."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict


@dataclass
class TaskResult:
    success: bool
    status: str
    message: str
    platform: str
    task: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TaskModule(ABC):
    """Abstract task module interface."""

    TASK_TYPE = "api-driven"
    PLATFORM = "unknown"
    DESCRIPTION = "unknown task"

    @abstractmethod
    def execute(self, **kwargs: Any) -> TaskResult:
        """Execute the primary task action."""

    @abstractmethod
    def check_status(self, **kwargs: Any) -> TaskResult:
        """Query task/platform status without side effects."""
