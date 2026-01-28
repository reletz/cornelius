"""
GitHub integration routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.models import User, Cluster, Note
from app.schemas.schemas import (
    GitHubConfigRequest,
    GitHubSyncRequest,
    GitHubSyncResponse
)
from app.services.github_sync import GitHubService

router = APIRouter()


@router.post("/validate")
async def validate_github_config(request: GitHubConfigRequest):
    """Validate GitHub PAT and repository access."""
    try:
        service = GitHubService(request.pat)
        validation = service.validate_connection()
        
        if not validation.get("valid"):
            raise HTTPException(status_code=401, detail=validation.get("error", "Invalid PAT"))
        
        # Try to access repository
        try:
            repo = service.get_repo(request.repo)
            return {
                "valid": True,
                "username": validation["username"],
                "repo_name": repo.full_name,
                "repo_private": repo.private
            }
        except Exception:
            raise HTTPException(
                status_code=404, 
                detail=f"Repository '{request.repo}' not found or not accessible"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/config/{user_id}")
async def save_github_config(
    user_id: str,
    request: GitHubConfigRequest,
    db: AsyncSession = Depends(get_db)
):
    """Save GitHub configuration for a user (PAT is stored)."""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        # Create user
        user = User(
            id=user_id,
            github_config={
                "pat": request.pat,  # Note: In production, encrypt this
                "repo": request.repo,
                "path": request.path
            }
        )
        db.add(user)
    else:
        user.github_config = {
            "pat": request.pat,
            "repo": request.repo,
            "path": request.path
        }
    
    await db.commit()
    
    return {"message": "GitHub configuration saved"}


@router.post("/sync", response_model=GitHubSyncResponse)
async def sync_to_github(
    request: GitHubSyncRequest,
    config: GitHubConfigRequest,
    db: AsyncSession = Depends(get_db)
):
    """Sync notes to GitHub repository."""
    # Get clusters for session
    cluster_stmt = select(Cluster).where(Cluster.session_id == request.session_id)
    cluster_result = await db.execute(cluster_stmt)
    clusters = cluster_result.scalars().all()
    
    if not clusters:
        raise HTTPException(status_code=400, detail="No clusters found")
    
    cluster_ids = [c.id for c in clusters]
    
    # Get notes
    if request.note_ids:
        note_stmt = select(Note).where(
            Note.id.in_(request.note_ids),
            Note.cluster_id.in_(cluster_ids)
        )
    else:
        note_stmt = select(Note).where(Note.cluster_id.in_(cluster_ids))
    
    note_result = await db.execute(note_stmt)
    notes = note_result.scalars().all()
    
    if not notes:
        raise HTTPException(status_code=400, detail="No notes found")
    
    # Prepare notes for sync
    cluster_titles = {c.id: c.title for c in clusters}
    notes_to_sync = []
    
    for note in notes:
        title = cluster_titles.get(note.cluster_id, "Untitled")
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        notes_to_sync.append({
            "filename": f"{safe_title}.md",
            "content": note.markdown_content
        })
    
    # Sync to GitHub
    try:
        service = GitHubService(config.pat)
        synced_files = service.sync_notes(
            repo_name=config.repo,
            base_path=config.path,
            notes=notes_to_sync
        )
        
        return GitHubSyncResponse(
            success=True,
            synced_files=synced_files,
            message=f"Successfully synced {len(synced_files)} files"
        )
        
    except Exception as e:
        return GitHubSyncResponse(
            success=False,
            synced_files=[],
            message=f"Sync failed: {str(e)}"
        )
