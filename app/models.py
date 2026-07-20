from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class VisualType(str, enum.Enum):
    album_cover = "album-cover"
    poster = "poster"
    merch = "merch"
    ai_art = "ai-art"
    branding = "branding"

class VisualAsset(Base):
    __tablename__ = "visual_assets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    type = Column(Enum(VisualType), nullable=False)
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=False)
    tags = Column(String, nullable=True)  # comma-separated tags
    created_at = Column(DateTime, default=datetime.utcnow)