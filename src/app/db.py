from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import settings

# ----- SQLAlchemy base -----
class Base(DeclarativeBase):  # type: ignore [valid-type]
    pass

# ----- Engine & Session -----
engine = create_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


# ----- FastAPI dependency -----
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
