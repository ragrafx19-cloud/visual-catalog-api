from pydantic import BaseModel
from typing import List
from datetime import datetime

class VisualAssetBase(BaseModel):
    title: str
    description: str
    type: str
    image_url: str
    tags: List[str] = []

class VisualAssetCreate(VisualAssetBase):
    pass

class VisualAssetResponse(VisualAssetBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
