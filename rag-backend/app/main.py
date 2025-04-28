from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from app.core.config import settings
from app.core.logger import logger
from app.db.base import db
from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.rag import router as rag_router
from app.core.exception_handler import (
    app_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)
from app.core.exceptions import AppException
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="Document Management and RAG-based Q&A Application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Request: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.2f}s")
    return response

# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(documents_router, prefix="/documents", tags=["Documents"])
app.include_router(rag_router, prefix="/rag", tags=["RAG"])

@app.on_event("startup")
async def startup_event():
    try:
        logger.info("Starting application initialization...")
        logger.info(f"Application configuration:")
        logger.info(f"Database URL: {settings.DATABASE_URL}")
        logger.info(f"Debug mode: {settings.DEBUG}")
        logger.info(f"App name: {settings.APP_NAME}")
        
        logger.info("Initializing database...")
        await db.init_db()
        logger.info("Database initialized successfully")
        
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        logger.error(f"Stack trace:", exc_info=True)
        raise

@app.get("/health", response_model=dict)
async def health_check():
    """Health check endpoint that returns the status of the application."""
    try:
        # Check database connection
        await db.check_connection()
        return {
            "status": "healthy",
            "version": "1.0.0",
            "app_name": settings.APP_NAME,
            "database": "connected",
            "services": {
                "embedding": "ready",
                "reranker": "ready"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        ) 