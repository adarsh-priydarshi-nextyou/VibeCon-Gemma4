"""
Telemetry API endpoints for intervention interactions.
"""
from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel, Field
from typing import Optional
from services.telemetry_collector import get_telemetry_collector, PersistenceError
from models.schemas import DeviceInfo
from logger import get_logger
from utils.device_id import get_or_create_device_id

logger = get_logger(__name__)

router = APIRouter(prefix="/api/telemetry", tags=["telemetry"])


class PlayEventRequest(BaseModel):
    """Request model for play event."""
    audio_id: str
    audio_url: str
    play_duration_seconds: float = Field(..., ge=0.0)
    total_duration_seconds: float = Field(..., gt=0.0)
    stress_score_at_interaction: float = Field(..., ge=0.0, le=1.0)
    session_id: str
    device_platform: str
    app_version: str


class FeedbackEventRequest(BaseModel):
    """Request model for feedback event."""
    audio_id: str
    audio_url: str
    like_status: bool
    feedback_text: Optional[str] = None
    stress_score_at_interaction: float = Field(..., ge=0.0, le=1.0)
    session_id: str
    device_platform: str
    app_version: str
    play_duration_seconds: float = Field(default=0.0, ge=0.0)
    total_duration_seconds: float = Field(default=1.0, gt=0.0)


class TelemetryResponse(BaseModel):
    """Response model for telemetry recording."""
    success: bool
    telemetry_id: str
    message: str


@router.post("/play", response_model=TelemetryResponse)
async def record_play_event(
    request: Request,
    play_request: PlayEventRequest,
    user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    """
    Record audio play event.
    
    User ID is automatically generated from device fingerprint if not provided.
    
    Args:
        request: FastAPI request object
        play_request: Play event data
        user_id: Optional user identifier (auto-generated if not provided)
        
    Returns:
        TelemetryResponse with success status
        
    Requirements: 13.1, 13.2, 13.3, 13.5
    """
    try:
        # Get or create device-based user ID
        if not user_id:
            user_id = get_or_create_device_id(request)
        
        collector = get_telemetry_collector()
        
        device_info = DeviceInfo(
            platform=play_request.device_platform,
            app_version=play_request.app_version
        )
        
        telemetry = collector.capture_play_event(
            user_id=user_id,
            audio_id=play_request.audio_id,
            audio_url=play_request.audio_url,
            play_duration=play_request.play_duration_seconds,
            total_duration=play_request.total_duration_seconds,
            stress_score_at_interaction=play_request.stress_score_at_interaction,
            session_id=play_request.session_id,
            device_info=device_info
        )
        
        doc_id = await collector.record_interaction(telemetry)
        
        return TelemetryResponse(
            success=True,
            telemetry_id=doc_id,
            message="Play event recorded successfully"
        )
        
    except PersistenceError as e:
        logger.error("Failed to persist play event", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to record telemetry: {e}")
        
    except Exception as e:
        logger.error("Play event recording failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/feedback", response_model=TelemetryResponse)
async def record_feedback_event(
    request: Request,
    feedback_request: FeedbackEventRequest,
    user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    """
    Record user feedback event.
    
    User ID is automatically generated from device fingerprint if not provided.
    
    Args:
        request: FastAPI request object
        feedback_request: Feedback event data
        user_id: Optional user identifier (auto-generated if not provided)
        
    Returns:
        TelemetryResponse with success status
        
    Requirements: 13.4, 13.5
    """
    try:
        # Get or create device-based user ID
        if not user_id:
            user_id = get_or_create_device_id(request)
        
        collector = get_telemetry_collector()
        
        device_info = DeviceInfo(
            platform=feedback_request.device_platform,
            app_version=feedback_request.app_version
        )
        
        telemetry = collector.capture_feedback_event(
            user_id=user_id,
            audio_id=feedback_request.audio_id,
            audio_url=feedback_request.audio_url,
            like_status=feedback_request.like_status,
            feedback_text=feedback_request.feedback_text,
            stress_score_at_interaction=feedback_request.stress_score_at_interaction,
            session_id=feedback_request.session_id,
            device_info=device_info,
            play_duration=feedback_request.play_duration_seconds,
            total_duration=feedback_request.total_duration_seconds
        )
        
        doc_id = await collector.record_interaction(telemetry)
        
        return TelemetryResponse(
            success=True,
            telemetry_id=doc_id,
            message="Feedback recorded successfully"
        )
        
    except PersistenceError as e:
        logger.error("Failed to persist feedback", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to record telemetry: {e}")
        
    except Exception as e:
        logger.error("Feedback recording failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def telemetry_health():
    """Check telemetry service health."""
    return {
        "status": "healthy",
        "service": "telemetry_collector"
    }
