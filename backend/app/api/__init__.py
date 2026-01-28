"""
API Router - aggregates all route modules.
"""
from fastapi import APIRouter

from app.api.routes import config, upload, sessions, clusters, generate, export, github

router = APIRouter()

router.include_router(config.router, prefix="/config", tags=["Configuration"])
router.include_router(upload.router, prefix="/upload", tags=["Upload"])
router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
router.include_router(clusters.router, prefix="/clusters", tags=["Clusters"])
router.include_router(generate.router, prefix="/generate", tags=["Generation"])
router.include_router(export.router, prefix="/export", tags=["Export"])
router.include_router(github.router, prefix="/github", tags=["GitHub"])
