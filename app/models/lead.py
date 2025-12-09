from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    verification_token = Column(String, unique=True, nullable=False)
    token_expiry = Column(DateTime(timezone=True), nullable=False)
    is_verified = Column(Boolean, default=False)
    newsletter = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
