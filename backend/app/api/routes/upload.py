"""
File upload routes.
"""
import uuid
import aiofiles
from pathlib import Path
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.models import Session, Document
from app.schemas.schemas import DocumentResponse, DocumentListResponse
from app.services.document_processor import document_processor

router = APIRouter()


def validate_file(file: UploadFile) -> None:
    """Validate uploaded file."""
    # Check extension
    ext = Path(file.filename).suffix.lower().lstrip('.')
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not supported. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # File size is checked by the framework via chunk reading


async def process_document(document_id: str, file_path: str, db: AsyncSession):
    """Background task to process a document."""
    from sqlalchemy import select
    
    try:
        # Extract text
        text = await document_processor.extract_text(file_path)
        
        # Update document
        async with db.begin():
            stmt = select(Document).where(Document.id == document_id)
            result = await db.execute(stmt)
            doc = result.scalar_one_or_none()
            
            if doc:
                doc.extracted_text = text
                doc.status = "extracted"
                await db.commit()
                
    except Exception as e:
        async with db.begin():
            stmt = select(Document).where(Document.id == document_id)
            result = await db.execute(stmt)
            doc = result.scalar_one_or_none()
            
            if doc:
                doc.status = "failed"
                doc.error_message = str(e)
                await db.commit()


@router.post("/", response_model=DocumentListResponse)
async def upload_files(
    session_id: str,
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload multiple files for processing.
    Files are saved and queued for text extraction.
    """
    # Validate session exists
    from sqlalchemy import select
    
    stmt = select(Session).where(Session.id == session_id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Process each file
    documents = []
    upload_dir = Path(settings.UPLOAD_DIR) / session_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    for file in files:
        validate_file(file)
        
        # Save file
        file_id = str(uuid.uuid4())
        ext = Path(file.filename).suffix
        file_path = upload_dir / f"{file_id}{ext}"
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} exceeds size limit of {settings.MAX_FILE_SIZE // 1024 // 1024}MB"
                )
            await f.write(content)
        
        # Create document record
        doc = Document(
            id=file_id,
            session_id=session_id,
            filename=file.filename,
            file_path=str(file_path),
            status="uploaded"
        )
        db.add(doc)
        documents.append(doc)
        
        # Queue processing
        background_tasks.add_task(
            process_document, 
            file_id, 
            str(file_path),
            db
        )
    
    await db.commit()
    
    return DocumentListResponse(
        documents=[
            DocumentResponse(
                id=doc.id,
                filename=doc.filename,
                status=doc.status,
                error_message=doc.error_message,
                created_at=doc.created_at
            )
            for doc in documents
        ],
        total=len(documents)
    )


@router.get("/{session_id}", response_model=DocumentListResponse)
async def list_documents(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """List all documents in a session."""
    from sqlalchemy import select
    
    stmt = select(Document).where(Document.session_id == session_id)
    result = await db.execute(stmt)
    documents = result.scalars().all()
    
    return DocumentListResponse(
        documents=[
            DocumentResponse(
                id=doc.id,
                filename=doc.filename,
                status=doc.status,
                error_message=doc.error_message,
                created_at=doc.created_at
            )
            for doc in documents
        ],
        total=len(documents)
    )
