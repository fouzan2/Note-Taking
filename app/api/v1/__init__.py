"""
API v1 routers.
"""
from fastapi import APIRouter

from app.api.v1 import auth, notes, tags, cache

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router)
api_router.include_router(notes.router)
api_router.include_router(tags.router)
api_router.include_router(cache.router) 