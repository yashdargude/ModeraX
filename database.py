# filepath: /Users/yashdargude/Downloads/steps_AI/database.py
import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# You can change this to your preferred database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:yash5678@localhost/stepai")

engine = create_engine(DATABASE_URL)
metadata = MetaData()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
