"""
API Routes
"""
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.checkins import router as checkins_router
from app.api.interventions import router as interventions_router
from app.api.crisis import router as crisis_router

__all__ = [
    "auth_router",
    "users_router",
    "checkins_router",
    "interventions_router",
    "crisis_router",
]
