"""BradlyAI Database Setup (SQLAlchemy sync + async)"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from bradlyai.config import settings

Base = declarative_base()

_connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(
    settings.DATABASE_URL.replace("+aiosqlite", ""),
    connect_args=_connect_args, echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

try:
    async_engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
except Exception:
    async_engine = None
    AsyncSessionLocal = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    if AsyncSessionLocal is None:
        raise RuntimeError("Async database is not available.")
    async with AsyncSessionLocal() as session:
        yield session
