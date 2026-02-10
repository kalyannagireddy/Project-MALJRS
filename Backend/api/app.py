"""
FastAPI application for legal case management and AI processing.
This is the main entry point for the REST API.
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging
import sys
import os
from dotenv import load_dotenv

# Configure logging - ensure output appears in console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("maljrs")

# Load environment variables from .env file
load_dotenv()

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.routes import case, ai_processing
from api.middleware.cors import setup_cors
from api.middleware.error_handler import setup_error_handlers

# Create FastAPI application
app = FastAPI(
    title="MALJRS API",
    description="Multi-Agent Legal Justice Recommendation System - REST API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Setup middleware
setup_cors(app)
setup_error_handlers(app)

# Include routers
app.include_router(case.router)
app.include_router(ai_processing.router)


@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": "MALJRS API",
        "version": "1.0.0",
        "description": "Multi-Agent Legal Justice Recommendation System",
        "docs": "/api/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MALJRS Backend API"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
