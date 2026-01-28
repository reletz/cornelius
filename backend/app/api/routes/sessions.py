"""
Session management routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.models import Session, Document
from app.schemas.schemas import SessionCreate, SessionResponse

router = APIRouter()


@router.post("/", response_model=SessionResponse)
async def create_session(
    db: AsyncSession = Depends(get_db)
):
    """Create a new document processing session."""
    session = Session(status="created")
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return SessionResponse(
        id=session.id,
        status=session.status,
        created_at=session.created_at,
        document_count=0
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get session details."""
    stmt = select(Session).where(Session.id == session_id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Count documents
    doc_stmt = select(Document).where(Document.session_id == session_id)
    doc_result = await db.execute(doc_stmt)
    documents = doc_result.scalars().all()
    
    return SessionResponse(
        id=session.id,
        status=session.status,
        created_at=session.created_at,
        document_count=len(documents)
    )


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a session and all associated data."""
    import shutil
    from pathlib import Path
    from app.core.config import settings
    
    stmt = select(Session).where(Session.id == session_id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Delete uploaded files
    upload_dir = Path(settings.UPLOAD_DIR) / session_id
    if upload_dir.exists():
        shutil.rmtree(upload_dir)
    
    # Delete session (cascades to documents, clusters, notes)
    await db.delete(session)
    await db.commit()
    
    return {"message": "Session deleted successfully"}
