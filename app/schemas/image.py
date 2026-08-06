from pydantic import BaseModel
from datetime import datetime

class ImageBase(BaseModel):
    filename: str
    url: str
    description: str | None = None
    tags: str | None = None
    category: str | None = None

class ImageCreate(ImageBase):
    pass

class ImageOut(ImageBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True