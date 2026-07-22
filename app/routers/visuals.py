from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import VisualAsset, VisualType
from app.schemas import (
    VisualAssetCreate,
    VisualAssetUpdate,
    VisualAssetResponse
)

router = APIRouter(
    prefix="/visuals",
    tags=["Visual Assets"]
)

# ---------------------------
# GET ALL VISUALS (with filters)
# ---------------------------
@router.get("/", response_model=List[VisualAssetResponse])
def get_visuals(
    type: Optional[VisualType] = None,
    tag: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(VisualAsset)

    if type:
        query = query.filter(VisualAsset.type == type)

    if tag:
        query = query.filter(VisualAsset.tags.contains(tag))

    return query.offset(skip).limit(limit).all()

# ---------------------------
# GET VISUAL BY ID
# ---------------------------
@router.get("/{visual_id}", response_model=VisualAssetResponse)
def get_visual_by_id(visual_id: int, db: Session = Depends(get_db)):
    visual = db.query(VisualAsset).filter(VisualAsset.id == visual_id).first()
    if not visual:
        raise HTTPException(status_code=404, detail="Visual asset not found")
    return visual

# ---------------------------
# CREATE NEW VISUAL
# ---------------------------
@router.post("/", response_model=VisualAssetResponse)
def create_visual(payload: VisualAssetCreate, db: Session = Depends(get_db)):
    tags_str = ",".join(payload.tags) if payload.tags else None

    new_visual = VisualAsset(
        title=payload.title,
        type=payload.type,
        description=payload.description,
        image_url=payload.image_url,
        tags=tags_str
    )

    db.add(new_visual)
    db.commit()
    db.refresh(new_visual)

    return new_visual

# ---------------------------
# UPDATE VISUAL
# ---------------------------
@router.put("/{visual_id}", response_model=VisualAssetResponse)
def update_visual(visual_id: int, payload: VisualAssetUpdate, db: Session = Depends(get_db)):
    visual = db.query(VisualAsset).filter(VisualAsset.id == visual_id).first()
    if not visual:
        raise HTTPException(status_code=404, detail="Visual asset not found")

    if payload.title is not None:
        visual.title = payload.title
    if payload.type is not None:
        visual.type = payload.type
    if payload.description is not None:
        visual.description = payload.description
    if payload.image_url is not None:
        visual.image_url = payload.image_url
    if payload.tags is not None:
        visual.tags = ",".join(payload.tags)

    db.commit()
    db.refresh(visual)

    return visual

# ---------------------------
# DELETE VISUAL
# ---------------------------
@router.delete("/{visual_id}")
def delete_visual(visual_id: int, db: Session = Depends(get_db)):
    visual = db.query(VisualAsset).filter(VisualAsset.id == visual_id).first()
    if not visual:
        raise HTTPException(status_code=404, detail="Visual asset not found")

    db.delete(visual)
    db.commit()

    return {"message": "Visual asset deleted successfully"}

# ---------------------------
# SEARCH VISUALS
# ---------------------------
@router.get("/search", response_model=List[VisualAssetResponse])
def search_visuals(
    title: Optional[str] = None,
    tag: Optional[str] = None,
    type: Optional[VisualType] = None,
    db: Session = Depends(get_db)
):
    query = db.query(VisualAsset)

    if title:
        query = query.filter(VisualAsset.title.ilike(f"%{title}%"))

    if tag:
        query = query.filter(VisualAsset.tags.contains(tag))

    if type:
        query = query.filter(VisualAsset.type == type)

    return query.all()

from fastapi import UploadFile, File, HTTPException
import shutil
import os

UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": file.filename,
        "url": f"/images/{file.filename}"
    }