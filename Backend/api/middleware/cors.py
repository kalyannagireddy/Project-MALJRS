"""
CORS middleware for frontend integration.
"""
from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app):
    """
    Configure CORS middleware for frontend communication.
    
    Args:
        app: FastAPI application instance
    """
    # Allow frontend origin
    origins = [
        "http://localhost:5173",  # Vite default dev server
        "http://localhost:3000",  # Alternative port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
