from pydantic import BaseModel


class BuildClearRequest(BaseModel):
    task_id: str
