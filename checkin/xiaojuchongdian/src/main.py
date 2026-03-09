"""CLI entrypoint for Xiaoju Charging check-in."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

if __package__ in {None, ""}:
    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from checkin.xiaojuchongdian.src.logger import configure_logging
    from checkin.xiaojuchongdian.src.router import TaskNotFoundError, TaskRouter
else:
    from .logger import configure_logging
    from .router import TaskNotFoundError, TaskRouter

logger = logging.getLogger(__name__)


def _print_json(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Xiaoju check-in task runner")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List registered tasks")

    run = sub.add_parser("run", help="Execute a task")
    run.add_argument("--task", required=True, help="Task name, e.g. xiaoju.checkin")
    run.add_argument(
        "--verify-record",
        action="store_true",
        help="Fetch signRecord after check-in",
    )
    run.add_argument(
        "--record-days",
        type=int,
        default=30,
        help="Record window days when --verify-record is enabled",
    )

    status = sub.add_parser("status", help="Query task status")
    status.add_argument("--task", required=True, help="Task name, e.g. xiaoju.checkin")

    return parser


def main() -> int:
    configure_logging()
    parser = build_parser()
    args = parser.parse_args()
    router = TaskRouter()

    if args.command == "list":
        _print_json(router.list_tasks())
        return 0

    if args.command == "run":
        try:
            result = router.run(
                args.task,
                verify_record=bool(args.verify_record),
                record_days=int(args.record_days),
            )
        except TaskNotFoundError as exc:
            logger.error("task not found: %s", exc)
            _print_json({"success": False, "error": str(exc), "error_type": "task_not_found"})
            return 2
        except Exception as exc:  # noqa: BLE001
            logger.exception("unexpected error running task %r", args.task)
            _print_json({"success": False, "error": str(exc)})
            return 1
        _print_json(result.to_dict())
        return 0 if result.success else 1

    if args.command == "status":
        try:
            result = router.status(args.task)
        except TaskNotFoundError as exc:
            logger.error("task not found: %s", exc)
            _print_json({"success": False, "error": str(exc), "error_type": "task_not_found"})
            return 2
        except Exception as exc:  # noqa: BLE001
            logger.exception("unexpected error running status for task %r", args.task)
            _print_json({"success": False, "error": str(exc)})
            return 1
        _print_json(result.to_dict())
        return 0 if result.success else 1

    parser.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
