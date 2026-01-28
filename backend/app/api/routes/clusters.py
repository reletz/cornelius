"""
Cluster management routes.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_api_key
from app.models.models import Session, Document, Cluster
from app.schemas.schemas import (
    ClusterResponse, 
    ClusterListResponse, 
    ClusterUpdate,
    ClusterMergeRequest
)
from app.services.clustering import clustering_service

router = APIRouter()


@router.post("/analyze/{session_id}", response_model=ClusterListResponse)
async def analyze_and_cluster(
    session_id: str,
    api_key: str = Depends(get_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze documents and create topic clusters using LLM.
    """
    # Get session documents
    stmt = select(Document).where(
        Document.session_id == session_id,
        Document.status == "extracted"
    )
    result = await db.execute(stmt)
    documents = result.scalars().all()
    
    if not documents:
        raise HTTPException(
            status_code=400, 
            detail="No processed documents found. Please upload and process documents first."
        )
    
    # Prepare texts
    texts = [
        {"filename": doc.filename, "content": doc.extracted_text}
        for doc in documents
        if doc.extracted_text
    ]
    
    # Run clustering
    clustering_result = await clustering_service.analyze_and_cluster(texts, api_key)
    
    # Delete existing clusters
    existing_stmt = select(Cluster).where(Cluster.session_id == session_id)
    existing_result = await db.execute(existing_stmt)
    for cluster in existing_result.scalars().all():
        await db.delete(cluster)
    
    # Create new clusters
    clusters = []
    for idx, cluster_data in enumerate(clustering_result.get("clusters", [])):
        cluster = Cluster(
            session_id=session_id,
            title=cluster_data.get("title", f"Topic {idx + 1}"),
            sources_json={
                "keywords": cluster_data.get("keywords", []),
                "source_mapping": cluster_data.get("source_mapping", []),
                "summary": cluster_data.get("summary", ""),
                "estimated_word_count": cluster_data.get("estimated_word_count", 0)
            },
            order_index=idx
        )
        db.add(cluster)
        clusters.append(cluster)
    
    await db.commit()
    
    # Refresh to get IDs
    for cluster in clusters:
        await db.refresh(cluster)
    
    return ClusterListResponse(
        clusters=[
            ClusterResponse(
                id=c.id,
                session_id=c.session_id,
                title=c.title,
                sources_json=c.sources_json,
                order_index=c.order_index,
                created_at=c.created_at
            )
            for c in clusters
        ],
        total=len(clusters)
    )


@router.get("/{session_id}", response_model=ClusterListResponse)
async def list_clusters(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """List all clusters for a session."""
    stmt = select(Cluster).where(Cluster.session_id == session_id).order_by(Cluster.order_index)
    result = await db.execute(stmt)
    clusters = result.scalars().all()
    
    return ClusterListResponse(
        clusters=[
            ClusterResponse(
                id=c.id,
                session_id=c.session_id,
                title=c.title,
                sources_json=c.sources_json,
                order_index=c.order_index,
                created_at=c.created_at
            )
            for c in clusters
        ],
        total=len(clusters)
    )


@router.patch("/{cluster_id}", response_model=ClusterResponse)
async def update_cluster(
    cluster_id: str,
    update: ClusterUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a cluster's title or sources."""
    stmt = select(Cluster).where(Cluster.id == cluster_id)
    result = await db.execute(stmt)
    cluster = result.scalar_one_or_none()
    
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    if update.title is not None:
        cluster.title = update.title
    if update.sources_json is not None:
        cluster.sources_json = update.sources_json
    
    await db.commit()
    await db.refresh(cluster)
    
    return ClusterResponse(
        id=cluster.id,
        session_id=cluster.session_id,
        title=cluster.title,
        sources_json=cluster.sources_json,
        order_index=cluster.order_index,
        created_at=cluster.created_at
    )


@router.delete("/{cluster_id}")
async def delete_cluster(
    cluster_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a cluster."""
    stmt = select(Cluster).where(Cluster.id == cluster_id)
    result = await db.execute(stmt)
    cluster = result.scalar_one_or_none()
    
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    await db.delete(cluster)
    await db.commit()
    
    return {"message": "Cluster deleted successfully"}


@router.post("/merge", response_model=ClusterResponse)
async def merge_clusters(
    request: ClusterMergeRequest,
    db: AsyncSession = Depends(get_db)
):
    """Merge multiple clusters into one."""
    # Get all clusters to merge
    stmt = select(Cluster).where(Cluster.id.in_(request.cluster_ids))
    result = await db.execute(stmt)
    clusters = result.scalars().all()
    
    if len(clusters) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 clusters to merge")
    
    # Verify all clusters are from same session
    session_ids = set(c.session_id for c in clusters)
    if len(session_ids) > 1:
        raise HTTPException(status_code=400, detail="All clusters must be from the same session")
    
    # Merge sources
    merged_sources = {
        "keywords": [],
        "source_mapping": [],
        "summary": "",
        "estimated_word_count": 0
    }
    
    for cluster in clusters:
        if cluster.sources_json:
            merged_sources["keywords"].extend(cluster.sources_json.get("keywords", []))
            merged_sources["source_mapping"].extend(cluster.sources_json.get("source_mapping", []))
            merged_sources["estimated_word_count"] += cluster.sources_json.get("estimated_word_count", 0)
    
    # Remove duplicates from keywords
    merged_sources["keywords"] = list(set(merged_sources["keywords"]))
    
    # Create merged cluster
    new_cluster = Cluster(
        session_id=clusters[0].session_id,
        title=request.new_title,
        sources_json=merged_sources,
        order_index=min(c.order_index for c in clusters)
    )
    db.add(new_cluster)
    
    # Delete old clusters
    for cluster in clusters:
        await db.delete(cluster)
    
    await db.commit()
    await db.refresh(new_cluster)
    
    return ClusterResponse(
        id=new_cluster.id,
        session_id=new_cluster.session_id,
        title=new_cluster.title,
        sources_json=new_cluster.sources_json,
        order_index=new_cluster.order_index,
        created_at=new_cluster.created_at
    )
