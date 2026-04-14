"""
Main entry point for Voice Analysis and Intervention System backend.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from logger import get_logger
from api.audio import router as audio_router
from api.telemetry import router as telemetry_router
from api.insights import router as insights_router
from api.interventions import router as interventions_router

logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Voice Analysis and Intervention System",
    description="Backend API for voice stress analysis and intervention recommendations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(audio_router)
app.include_router(telemetry_router)
app.include_router(insights_router)
app.include_router(interventions_router)


@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    logger.info(
        "Starting Voice Analysis and Intervention System",
        mongodb_uri=settings.mongodb_uri,
        audio_processor_port=settings.audio_processor_port,
    )
    
    # Initialize Gemma4 LLM
    try:
        from services.gemma4_client import gemma4_client
        logger.info("Initializing Gemma4 LLM...")
        await gemma4_client.initialize()
        logger.info("Gemma4 LLM initialized successfully")
    except Exception as e:
        logger.warning(f"Gemma4 LLM initialization failed: {e}. Running in fallback mode.")
    
    # Initialize Audio Processor
    try:
        from services.audio_processor import get_processor
        logger.info("Initializing Audio Processor...")
        processor = await get_processor()
        await processor.initialize()
        logger.info("Audio Processor initialized successfully")
    except Exception as e:
        logger.warning(f"Audio Processor initialization failed: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down Voice Analysis and Intervention System")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "voice-analysis-intervention-system",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Voice Analysis and Intervention System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.audio_processor_host,
        port=settings.audio_processor_port,
        reload=True,
        log_level=settings.log_level.lower()
    )
