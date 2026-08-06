from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Correct imports
from database import Base, engine
import models
from app.routers import visuals_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Visual Catalog API",
    description="API for storing and managing creative visual assets.",
    version="1.0.0"
)

# CORS (allow all for now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(visuals_router.router)

@app.get("/")
def root():
    return {"message": "Visual Catalog API is running!"}

# Serve uploaded images
app.mount("/uploaded_images", StaticFiles(directory="uploaded_images"), name="uploaded_images")
