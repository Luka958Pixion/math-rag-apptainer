from threading import Lock

from math_rag_apptainer.enums import OverlayCreateStatus


class OverlayCreateStatusTracker:
    def __init__(self) -> None:
        self._statuses: dict[str, OverlayCreateStatus] = {}
        self._lock = Lock()

    def set_status(self, task_id: str, status: OverlayCreateStatus) -> None:
        with self._lock:
            self._statuses[task_id] = status

    def get_status(self, task_id: str) -> OverlayCreateStatus | None:
        with self._lock:
            return self._statuses.get(task_id)

    def remove_status(self, task_id: str) -> None:
        with self._lock:
            if task_id in self._statuses:
                del self._statuses[task_id]
