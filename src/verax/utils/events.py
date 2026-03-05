"""Progress event system for multi-threaded processing."""

from dataclasses import dataclass
from queue import Queue
from typing import Literal

# Type for processing stages
StageType = Literal[
    "parsing",
    "extracting",
    "mapping",
    "enhancing",
    "building",
    "complete",
    "error",
]


@dataclass(frozen=True)
class ProgressEvent:
    """Typed progress event from processing thread."""

    cv_filename: str
    stage: StageType
    percent: int  # 0-100


# Module-level singleton queue
progress_queue: Queue[ProgressEvent] = Queue()


def emit_progress(event: ProgressEvent) -> None:
    """Emit a progress event to the global queue.

    Args:
        event: ProgressEvent to emit
    """
    progress_queue.put(event)


def clear_queue() -> None:
    """Clear all pending events from queue (for testing)."""
    while not progress_queue.empty():
        try:
            progress_queue.get_nowait()
        except Exception:
            break
