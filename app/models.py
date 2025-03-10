from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    predictions = relationship("Prediction", back_populates="user")

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Location data
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    city = Column(String, nullable=True)
    temperature = Column(Float, nullable=True)
    
    # Input features - removed image storage
    image_path = Column(String, nullable=True)  # Kept for backward compatibility, but will be NULL for new entries
    clinical_features = Column(JSON)  # Store as JSON
    
    # Model predictions
    image_model_result = Column(Boolean)
    clinical_model_result = Column(Boolean)
    
    # Generated report
    language = Column(String, default="English")
    report = Column(Text)
    
    user = relationship("User", back_populates="predictions")

class DiseaseStats(Base):
    __tablename__ = "disease_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, unique=True, index=True)
    disease_count = Column(Integer, default=0) 