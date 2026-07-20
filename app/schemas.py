from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional, List
from enum import Enum

# Match the SQLAlchemy Enum
class VisualType(str, Enum):
    album_cover = "album-cover"
    poster = "poster"
    merch = "merch"
    ai_art = "ai-art"
    branding = "branding"

# Shared fields
class VisualAssetBase(BaseModel):
    title: str
    type: VisualType
    description: Optional[str] = None
    image_url: HttpUrl
    tags: Optional[List[str]] = None

# For POST requests
class VisualAssetCreate(VisualAssetBase):
    pass

# For PUT requests
class VisualAssetUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[VisualType] = None
    description: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    tags: Optional[List[str]] = None

# For responses
class VisualAssetResponse(VisualAssetBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True