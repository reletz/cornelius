"""
Database models for Cornell Notes Generator.
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    """User model - stores GitHub config, NOT API keys."""
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    github_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    sessions: Mapped[list["Session"]] = relationship(back_populates="user")


class Session(Base):
    """Session model - represents a document processing session."""
    __tablename__ = "sessions"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="created")  # created, processing, completed, failed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user: Mapped["User"] = relationship(back_populates="sessions")
    documents: Mapped[list["Document"]] = relationship(back_populates="session")
    clusters: Mapped[list["Cluster"]] = relationship(back_populates="session")


class Document(Base):
    """Document model - stores uploaded file info and extracted text."""
    __tablename__ = "documents"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessions.id"))
    filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="uploaded")  # uploaded, processing, extracted, failed
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    session: Mapped["Session"] = relationship(back_populates="documents")


class Cluster(Base):
    """Cluster model - represents a topic cluster for note generation."""
    __tablename__ = "clusters"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessions.id"))
    title: Mapped[str] = mapped_column(String(255))
    sources_json: Mapped[dict] = mapped_column(JSON, default=dict)
    order_index: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    session: Mapped["Session"] = relationship(back_populates="clusters")
    notes: Mapped[list["Note"]] = relationship(back_populates="cluster")


class Note(Base):
    """Note model - stores generated Cornell notes in markdown."""
    __tablename__ = "notes"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    cluster_id: Mapped[str] = mapped_column(String(36), ForeignKey("clusters.id"))
    markdown_content: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="generated")  # generating, generated, failed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    cluster: Mapped["Cluster"] = relationship(back_populates="notes")
