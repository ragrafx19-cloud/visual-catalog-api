import os

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine
)

from sqlalchemy.orm import (
    declarative_base,
    sessionmaker
)

DATABASE_URL = os.getenv("DATABASE_URL")

# Render/PostgreSQL
if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+asyncpg://",
        1
    )

# Local SQLite
else:
    DATABASE_URL = "sqlite+aiosqlite:///./local.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    async with SessionLocal() as session:
        yield session