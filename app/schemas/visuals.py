from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models.models import VisualType

class VisualAssetCreate(BaseModel):
    title: str
    type: VisualType
    description: Optional[str] = None
    image_url: str
    tags: Optional[List[str]] = None

class VisualAssetUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[VisualType] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None

class VisualAssetResponse(BaseModel):
    id: int
    title: str
    type: VisualType
    description: Optional[str]
    image_url: str
    tags: Optional[List[str]]
    created_at: datetime

    class Config:
        orm_mode = True