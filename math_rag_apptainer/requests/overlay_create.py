from pydantic import BaseModel


class OverlayCreateRequest(BaseModel):
    filename: str
    fakeroot: bool
    size: int
