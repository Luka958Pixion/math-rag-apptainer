from pydantic import BaseModel


class OverlayCreateResultRequest(BaseModel):
    task_id: str
