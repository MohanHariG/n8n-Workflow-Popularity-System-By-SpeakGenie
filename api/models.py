# api/models.py
from sqlalchemy import Column, BigInteger, String, Enum, JSON, Integer, TIMESTAMP, func, BigInteger as BigInt
from db import Base

class Workflow(Base):
    __tablename__ = "workflows"
    id = Column(BigInt, primary_key=True, autoincrement=True)
    workflow_name = Column(String(512), nullable=False)
    normalized_name = Column(String(512), nullable=False)
    platform = Column(Enum('YouTube','Forum','Google'), nullable=False)
    country = Column(String(8), nullable=False)
    evidence = Column(JSON, nullable=False)
    views = Column(BigInt, default=0)
    likes = Column(BigInt, default=0)
    comments = Column(BigInt, default=0)
    replies = Column(BigInt, default=0)
    contributors = Column(Integer, default=0)
    source_url = Column(String(1024))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
