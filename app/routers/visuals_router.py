from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from app.database import get_db
from app.models.models import VisualAsset
from app.models.image import Image
from app.schemas import (
    VisualAssetCreate,
    VisualAssetUpdate,
    VisualAssetResponse
)
from app.schemas.image import ImageOut

from fastapi import UploadFile, File, HTTPException
from azure.storage.blob import BlobServiceClient
import os
import uuid


router = APIRouter(prefix="/visuals", tags=["Visual Assets"])

AZURE_STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT")
AZURE_STORAGE_KEY = os.getenv("AZURE_STORAGE_KEY")
AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")

blob_service_client = BlobServiceClient(
    f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net",
    credential=AZURE_STORAGE_KEY
)


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
    type: Optional[str] = None,
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

    results = query.offset(skip).limit(limit).all()

    for v in results:
        v.tags = v.tags.split(",") if v.tags else []

    return results


# ---------------------------
# GET VISUAL BY ID
# ---------------------------
@router.get("/{visual_id}", response_model=VisualAssetResponse)
def get_visual_by_id(visual_id: int, db: Session = Depends(get_db)):
    visual = db.query(VisualAsset).filter(VisualAsset.id == visual_id).first()
    if not visual:
        raise HTTPException(status_code=404, detail="Visual asset not found")

    visual.tags = visual.tags.split(",") if visual.tags else []

    return visual



# ---------------------------
# CREATE NEW VISUAL
# ---------------------------
@router.post("/", response_model=VisualAssetResponse)
def create_visual(payload: VisualAssetCreate, db: Session = Depends(get_db)):
    new_visual = VisualAsset(
        title=payload.title,
        type=payload.type,
        description=payload.description,
        image_url=payload.image_url,
        tags=payload.tags or []
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
        visual.tags = payload.tags

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
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(VisualAsset)

    if title:
        query = query.filter(VisualAsset.title.ilike(f"%{title}%"))

    if tag:
        query = query.filter(VisualAsset.tags.contains(tag))

    if type:
        query = query.filter(VisualAsset.type == type)

    results = query.all()

    for v in results:
        v.tags = v.tags.split(",") if v.tags else []

    return results



# ---------------------------
# UPLOAD IMAGE TO AZURE BLOB STORAGE
# ---------------------------
@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    try:
        extension = file.filename.split(".")[-1]
        blob_name = f"{uuid.uuid4()}.{extension}"

        blob_client = blob_service_client.get_blob_client(
            container=AZURE_CONTAINER_NAME,
            blob=blob_name
        )

        await blob_client.upload_blob(file.file, overwrite=True)

        url = (
            f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/"
            f"{AZURE_CONTAINER_NAME}/{blob_name}"
        )

        return {"filename": blob_name, "url": url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
