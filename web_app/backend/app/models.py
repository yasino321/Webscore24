from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # User-specific API Keys
    gemini_api_key = Column(String, nullable=True)
    openai_api_key = Column(String, nullable=True)
    google_places_api_key = Column(String, nullable=True)

    leads = relationship("Lead", back_populates="owner")

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    address = Column(String)
    url = Column(String)
    phone = Column(String)
    reviews_count = Column(Integer, default=0)
    status = Column(String, default="neu")
    score_total = Column(Integer, nullable=True)
    score_details = Column(Text, nullable=True) # JSON string

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="leads")
