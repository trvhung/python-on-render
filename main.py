from fastapi import FastAPI, HTTPException
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import re
import uuid

# Optional: Read environment variable (defaults to "development")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Database setup
# For local development, you can use SQLite: "sqlite:///./test.db"
# For Render, use the DATABASE_URL environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database model
class ItemModel(Base):
    __tablename__ = "items"

    id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


# Pydantic schemas for API
class ItemCreate(BaseModel):
    name: str
    description: str | None = None


class ItemResponse(BaseModel):
    id: str
    name: str
    description: str | None
    created_at: datetime

    class Config:
        from_attributes = True


app = FastAPI(title="FastAPI Render Tutorial")


# Create tables on startup
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


# Helper function to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Helper function to safely display database info
def get_database_info():
    """Returns database type and sanitized URL for display."""
    if DATABASE_URL.startswith("sqlite"):
        return {
            "type": "SQLite",
            "url": DATABASE_URL,
        }
    elif DATABASE_URL.startswith("postgresql"):
        # Mask the password in the URL for security
        sanitized = re.sub(r"://([^:]+):([^@]+)@", r"://\1:****@", DATABASE_URL)
        return {
            "type": "PostgreSQL",
            "url": sanitized,
        }
    else:
        return {
            "type": "Unknown",
            "url": "Not configured",
        }


@app.get("/")
def read_root():
    """Root endpoint that returns a welcome message."""
    db_info = get_database_info()
    return {
        "message": "Welcome to FastAPI on Render!",
        "environment": ENVIRONMENT,
        "database": db_info,
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/api/items", response_model=ItemResponse)
def create_item(item: ItemCreate):
    """Create a new item in the database."""
    db = next(get_db())
    db_item = ItemModel(name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.get("/api/items", response_model=list[ItemResponse])
def get_items():
    """Get all items from the database."""
    db = next(get_db())
    items = db.query(ItemModel).all()
    return items


@app.get("/api/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: str):
    """Get a specific item by ID."""
    db = next(get_db())
    item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.delete("/api/items/{item_id}")
def delete_item(item_id: str):
    """Delete an item by ID."""
    db = next(get_db())
    item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"message": f"Item {item_id} deleted successfully"}
