from enum import Enum


class OverlayCreateStatus(str, Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    DONE = 'done'
    FAILED = 'failed'
