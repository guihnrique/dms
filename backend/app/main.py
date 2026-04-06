"""
FastAPI Application - Main Entry Point
DMS (Digital Music Service) Backend
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.routers import auth, artists, albums, songs, playlists, reviews, search
from app.database import init_db
from app.middleware.rate_limit import limiter, setup_rate_limiting

# Create FastAPI application
app = FastAPI(
    title="DMS API",
    description="Digital Music Service Backend API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Setup rate limiting
setup_rate_limiting(app)

# CORS middleware - Task 9.1, 9.2
# Requirements: 7.1-7.7
import os
from dotenv import load_dotenv

load_dotenv()

# Get FRONTEND_URL from environment (comma-separated for multiple origins)
frontend_urls = os.getenv("FRONTEND_URL", "http://localhost:3000").split(",")
allowed_origins = [url.strip() for url in frontend_urls]

# Prohibit wildcard in production
if "*" in allowed_origins:
    raise ValueError("Wildcard (*) not allowed in CORS origins for security")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Specific origins only
    allow_credentials=True,  # Allow cookies
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],  # Explicit methods
    allow_headers=["Content-Type", "Authorization", "Accept"],  # Specific headers
    max_age=86400  # Cache preflight for 24 hours
)

# Include routers
app.include_router(auth.router)
app.include_router(artists.router)
app.include_router(albums.router)
app.include_router(songs.router)
app.include_router(playlists.router)
app.include_router(reviews.router)
app.include_router(search.router)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    # Initialize database (create tables if needed)
    await init_db()


@app.get("/", tags=["health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "DMS API",
        "version": "1.0.0"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "service": "DMS API"
    }
