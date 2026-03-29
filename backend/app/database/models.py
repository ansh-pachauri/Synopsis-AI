from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid
from .base import Base


# user model
class User(Base):
    __tablename__ = "user"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    google_id = Column(String, unique=True)
    email = Column(String, unique=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    research = relationship("ResearchQuery", back_populates="user")
    


# research model
class ResearchQuery(Base):
    __tablename__ = "research_query"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    query = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow) 
    embedding = relationship("Embedding", back_populates="research_query", uselist=False)
    user = relationship("User", back_populates="research")
    report = relationship("Report", back_populates="research_query")
    

 
# embedding model
class Embedding(Base): 
    __tablename__ = "embedding"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    research_query_id = Column(UUID(as_uuid=True), ForeignKey("research_query.id"))
    embedding = Column(Vector(768))  # assuming 768 dimensions for the embedding
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow) 
    research_query = relationship("ResearchQuery", back_populates="embedding")


class Report(Base):
    __tablename__ = "report"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    research_query_id = Column(UUID(as_uuid=True), ForeignKey("research_query.id"))
    title = Column(String)
    sections = Column(String)  # JSON string of sections
    summary = Column(String)
    key_takeaways = Column(String)  # JSON string of key takeaways
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    research_query = relationship("ResearchQuery")