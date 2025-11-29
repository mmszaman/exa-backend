"""
Exa Backend - FastAPI Application
Clean slate for building features from scratch.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import email_router

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Exa Backend API",
    version="1.0.0",
    debug=settings.DEBUG,
)

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_frontend_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(email_router.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
