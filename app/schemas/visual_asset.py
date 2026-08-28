from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class VisualAssetBase(BaseModel):
    title: str
    type: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None

class VisualAssetCreate(VisualAssetBase):
    pass

class VisualAssetUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None

class VisualAssetResponse(VisualAssetBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
