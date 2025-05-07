#db/database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/mydb"

# ✅ Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# ✅ Create async session
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,   # Important: session class must be AsyncSession
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# ✅ Declarative Base
Base = declarative_base()

# ✅ Dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
