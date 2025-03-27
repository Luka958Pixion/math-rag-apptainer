from pydantic import BaseModel


class OverlayCreateStatusRequest(BaseModel):
    task_id: str
