from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Visual, VisualCreate, VisualRead

router = APIRouter(
    prefix="/visuals-db",
    tags=["Visuals (Database CRUD)"]
)

# CREATE
@router.post("/", response_model=VisualRead)
async def create_visual(visual: VisualCreate, db: AsyncSession = Depends(get_db)):
    new_visual = Visual(
        title=visual.title,
        description=visual.description,
        tags=visual.tags,
        image_url=visual.image_url
    )
    db.add(new_visual)
    await db.commit()
    await db.refresh(new_visual)
    return new_visual

# READ ONE
@router.get("/{visual_id}", response_model=VisualRead)
async def get_visual(visual_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Visual).where(Visual.id == visual_id))
    visual = result.scalar_one_or_none()

    if not visual:
        raise HTTPException(status_code=404, detail="Visual not found")

    return visual

# READ ALL
@router.get("/", response_model=list[VisualRead])
async def list_visuals(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Visual))
    visuals = result.scalars().all()
    return visuals

# UPDATE
@router.put("/{visual_id}", response_model=VisualRead)
async def update_visual(visual_id: int, updated: VisualCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Visual).where(Visual.id == visual_id))
    visual = result.scalar_one_or_none()

    if not visual:
        raise HTTPException(status_code=404, detail="Visual not found")

    visual.title = updated.title
    visual.description = updated.description
    visual.tags = updated.tags
    visual.image_url = updated.image_url

    await db.commit()
    await db.refresh(visual)
    return visual

# DELETE
@router.delete("/{visual_id}")
async def delete_visual(visual_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Visual).where(Visual.id == visual_id))
    visual = result.scalar_one_or_none()

    if not visual:
        raise HTTPException(status_code=404, detail="Visual not found")

    await db.delete(visual)
    await db.commit()
    return {"detail": "Visual deleted"}
