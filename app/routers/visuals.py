from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os

from app.database import get_db
from app.models.models import VisualAsset
from app.models.image import Image
from app.schemas.visuals import VisualAssetCreate, VisualAssetResponse
from app.schemas.image import ImageOut

router = APIRouter(prefix="/visuals", tags=["Visual Assets"])

# ---------------------------
# GALLERY ENDPOINT (KEEP)
# ---------------------------
@router.get("/gallery", response_model=List[ImageOut])
def get_gallery(db: Session = Depends(get_db)):
    images = db.query(Image).order_by(Image.created_at.desc()).all()
    return images

# ---------------------------
# GET ALL VISUALS (REPLACED)
# ---------------------------
@router.get("/", response_model=List[VisualAssetResponse])
def get_visuals(db: Session = Depends(get_db)):
    return db.query(VisualAsset).all()

# ---------------------------
# GET VISUAL BY ID (REPLACED)
# ---------------------------
@router.get("/{visual_id}", response_model=VisualAssetResponse)
def get_visual_by_id(visual_id: int, db: Session = Depends(get_db)):
    visual = db.query(VisualAsset).filter(VisualAsset.id == visual_id).first()
    if not visual:
        raise HTTPException(status_code=404, detail="Visual asset not found")
    return visual

# ---------------------------
# CREATE NEW VISUAL (REPLACED)
# ---------------------------
@router.post("/", response_model=VisualAssetResponse)
def create_visual(payload: VisualAssetCreate, db: Session = Depends(get_db)):
    visual = VisualAsset(
        title=payload.title,
        description=payload.description,
        type=payload.type,
        image_url=payload.image_url,
        tags=payload.tags
    )
    db.add(visual)
    db.commit()
    db.refresh(visual)
    return visual

# ---------------------------
# DELETE VISUAL (REPLACED)
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
# UPLOAD IMAGE (KEEP)
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
