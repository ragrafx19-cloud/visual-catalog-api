from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

# SQLAlchemy model (database table)
class Visual(Base):
    __tablename__ = "visuals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    tags = Column(String, nullable=True)  # comma-separated or JSON later
    image_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


from pydantic import BaseModel
from datetime import datetime

# Pydantic schema for reading data
class VisualBase(BaseModel):
    title: str
    description: str | None = None
    tags: str | None = None
    image_url: str

class VisualCreate(VisualBase):
    pass

class VisualRead(VisualBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
