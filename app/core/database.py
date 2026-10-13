from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativaBase

Database_URL = "sqlite:///./app/core/estacionamento.db"

engine = create_engine(Database_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclaritiveBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

        