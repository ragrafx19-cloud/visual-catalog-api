from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.models import models
from app.routers.visuals_router import router as visuals_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Visual Catalog API",
    description="API for storing and managing creative visual assets.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(visuals_router)

@app.get("/")
def root():
    return {"message": "Visual Catalog API is running!"}

app.mount("/uploaded_images", StaticFiles(directory="uploaded_images"), name="uploaded_images")
