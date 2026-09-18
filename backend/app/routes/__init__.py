"""
API routes package.
"""
from app.routes.health import router as health_router
from app.routes.analyze import router as analyze_router
from app.routes.quality import router as quality_router
from app.routes.enhancement import router as enhancement_router

__all__ = ["health_router", "analyze_router", "quality_router", "enhancement_router"]

