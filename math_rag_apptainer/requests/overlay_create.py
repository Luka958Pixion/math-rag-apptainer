from pydantic import BaseModel


class OverlayCreateRequest(BaseModel):
    fakeroot: bool
    size: int
