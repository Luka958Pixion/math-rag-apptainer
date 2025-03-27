from pydantic import BaseModel


class BuildResultRequest(BaseModel):
    task_id: str
