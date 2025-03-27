from pydantic import BaseModel


class BuildStatusRequest(BaseModel):
    task_id: str
