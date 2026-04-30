from dataclasses import dataclass
from threading import Lock
from typing import Optional


@dataclass(frozen=True)
class RelivioStatsSnapshot:
    captured_events: int
    capture_send_failures: int
    last_capture_error: Optional[str]


class RelivioStatsStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._captured_events = 0
        self._capture_send_failures = 0
        self._last_capture_error: Optional[str] = None

    def record_captured_event(self) -> None:
        with self._lock:
            self._captured_events += 1

    def record_capture_send_failure(self, error: BaseException) -> None:
        with self._lock:
            self._capture_send_failures += 1
            self._last_capture_error = str(error)

    def snapshot(self) -> RelivioStatsSnapshot:
        with self._lock:
            return RelivioStatsSnapshot(
                captured_events=self._captured_events,
                capture_send_failures=self._capture_send_failures,
                last_capture_error=self._last_capture_error,
            )
