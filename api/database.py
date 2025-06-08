from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Get database URL from environment variable
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable is not set")
    raise ValueError("DATABASE_URL environment variable is not set")

# Handle Railway's PostgreSQL URL format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

logger.info(f"Connecting to database: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    class Product(Base):
        __tablename__ = "products"

        id = Column(Integer, primary_key=True, index=True)
        name = Column(String, index=True)
        price = Column(Float)
        store = Column(String)
        category = Column(String)
        calories = Column(Float, nullable=True)
        protein = Column(Float, nullable=True)
        carbs = Column(Float, nullable=True)
        fat = Column(Float, nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)

    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Create tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

except Exception as e:
    logger.error(f"Database connection error: {str(e)}")
    raise 