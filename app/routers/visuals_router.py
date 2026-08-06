from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from app.database import get_db
from app.models.models import VisualAsset, VisualType
from app.models.image import Image
from app.schemas import (
    VisualAssetCreate,
    VisualAssetUpdate,
    VisualAssetResponse
)
from app.schemas.image import ImageOut

router = APIRouter(prefix="/visuals", tags=["Visual Assets"])

# ---------------------------
# GALLERY ENDPOINT
# ---------------------------
@router.get("/gallery", response_model=List[ImageOut])
def get_gallery(db: Session = Depends(get_db)):
    images = db.query(Image).order_by(Image.created_at.desc()).all()
    return images


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


# ---------------------------
# UPLOAD IMAGE
# ---------------------------
UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-image", response_model=ImageOut)
async def upload_image(
    file: UploadFile = File(...),
    description: str | None = None,
    tags: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    file_url = f"http://127.0.0.1:8000/{UPLOAD_DIR}/{file.filename}"

    new_image = Image(
        filename=file.filename,
        url=file_url,
        description=description,
        tags=tags,
        category=category,
    )
    db.add(new_image)
    db.commit()
    db.refresh(new_image)

    return new_image
