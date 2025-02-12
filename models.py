# filepath: /Users/yashdargude/Downloads/steps_AI/models.py
from sqlalchemy import Column, Integer, String, JSON
from database import Base


class ModerationResult(Base):
    __tablename__ = "moderation_results"

    id = Column(Integer, primary_key=True, index=True)
    model = Column(String, index=True)
    results = Column(JSON)
