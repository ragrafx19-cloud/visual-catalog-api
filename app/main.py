from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import visuals

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
app.include_router(visuals.router)

@app.get("/")
def root():
    return {"message": "Visual Catalog API is running!"}