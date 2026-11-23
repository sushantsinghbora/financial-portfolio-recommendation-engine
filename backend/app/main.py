from fastapi import FastAPI

from app.database import Base, engine
from app.models import User, Portfolio, Holding

from app.api.auth import router as auth_router
from app.api import auth
from app.api import portfolio
from app.api.market import router as market_router

# Recommendation API
from app.api.recommendation import (
    router as recommendation_router
)


# --------------------------------------------------
# Database initialization
# --------------------------------------------------

Base.metadata.create_all(
    bind=engine
)


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="Financial Portfolio Recommendation API",
    description=(
        "Backend API for managing portfolios, analysing stocks "
        "and generating investment recommendations."
    ),
    version="1.0.0",
)


# --------------------------------------------------
# Existing API routers
# --------------------------------------------------

app.include_router(
    auth.router
)

app.include_router(
    portfolio.router
)

app.include_router(
    market_router
)


# --------------------------------------------------
# Recommendation API router
# --------------------------------------------------

app.include_router(
    recommendation_router
)


# --------------------------------------------------
# Root endpoint
# --------------------------------------------------

@app.get("/")
def root() -> dict[str, str]:
    """Return a basic message to confirm that the API is running."""

    return {
        "message": (
            "Financial Portfolio Recommendation API is running"
        )
    }


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/health")
def health_check() -> dict[str, str]:
    """Return the current health status of the backend."""

    return {
        "status": "healthy"
    }