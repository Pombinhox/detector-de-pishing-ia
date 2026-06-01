from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    analysis_type = Column(String) # 'image' or 'link'
    risk_score = Column(Float)
    classification = Column(String) # 'Seguro', 'Suspeito', 'Alto Risco'
    ai_probability = Column(String) # 'Baixa', 'Média', 'Alta'
    detailed_report = Column(Text) # JSON string of full results
    created_at = Column(DateTime(timezone=True), server_default=func.now())
