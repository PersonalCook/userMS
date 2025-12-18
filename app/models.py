from sqlalchemy import Column, Integer, String, Date, TIMESTAMP
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    username = Column(String, unique=True,index=True, nullable=False)
    public_name = Column(String, nullable=False)
    birthdate = Column(Date)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())