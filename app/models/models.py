from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import ARRAY
from app.database import Base

class VisualAsset(Base):
    __tablename__ = "visual_assets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    type = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    tags = Column(ARRAY(String), default=[])
    created_at = Column(TIMESTAMP, server_default=func.now())
