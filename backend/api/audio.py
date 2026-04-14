"""
Audio processing API endpoints.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Header, BackgroundTasks, Request
from typing import Optional
from services.audio_processor import get_processor, InvalidAudioError, ProcessingTimeoutError, ModelUnavailableError
from services.baseline_engine import get_baseline_engine, InsufficientDataError
from services.gemma4_client import gemma4_client
from storage.voice_storage import get_storage
from models.schemas import VoiceAnalysisResult, VoiceAnalysisDocument, ModelVersions, LinguisticSummary
from config import settings
from logger import get_logger
from utils.device_id import get_or_create_device_id

logger = get_logger(__name__)

router = APIRouter(prefix="/api/audio", tags=["audio"])


async def trigger_baseline_calculation(user_id: str):
    """
    Background task to trigger baseline recalculation.
    
    Args:
        user_id: User identifier
        
    Requirements: 6.1, 6.3
    """
    try:
        engine = get_baseline_engine()
        await engine.calculate_and_store_baseline(user_id)
        logger.info("Baseline recalculation triggered", user_id=user_id)
    except InsufficientDataError as e:
        logger.info("Insufficient data for baseline", user_id=user_id, error=str(e))
    except Exception as e:
        logger.error("Baseline calculation failed", user_id=user_id, error=str(e))


@router.post("/process", response_model=VoiceAnalysisResult)
async def process_audio(
    request: Request,
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(...),
    user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    """
    Process audio stream and return voice analysis result.
    
    User ID is automatically generated from device fingerprint if not provided.
    Device fingerprint uses: IP address + User-Agent + Device info
    
    Args:
        request: FastAPI request object
        background_tasks: FastAPI background tasks
        audio: Audio file upload
        user_id: Optional user identifier from header (auto-generated if not provided)
        
    Returns:
        VoiceAnalysisResult with stress score and features
        
    Raises:
        HTTPException: If processing fails
        
    Requirements: 1.2, 2.1, 2.2, 2.3, 6.1
    """
    try:
        # Get or create device-based user ID
        if not user_id:
            user_id = get_or_create_device_id(request)
        
        # Read audio data
        audio_data = await audio.read()
        
        logger.info(
            "Processing audio request",
            user_id=user_id,
            filename=audio.filename,
            content_type=audio.content_type,
            size_bytes=len(audio_data)
        )
        
        # Get processor and process audio
        processor = await get_processor()
        result = await processor.process_audio_stream(audio_data, user_id)
        
        # Extract features for Gemma4
        audio_array = processor.preprocess_audio(audio_data)
        features = processor.extract_features(audio_array)
        
        # Generate linguistic summary using Gemma4
        feature_dict = {
            "pitch_mean": float(sum(features.sensevoice_features.pitch) / len(features.sensevoice_features.pitch)) if features.sensevoice_features.pitch else 0,
            "pitch_std": float(sum((p - sum(features.sensevoice_features.pitch) / len(features.sensevoice_features.pitch))**2 for p in features.sensevoice_features.pitch) / len(features.sensevoice_features.pitch))**0.5 if features.sensevoice_features.pitch else 0,
            "energy_mean": float(sum(features.sensevoice_features.energy) / len(features.sensevoice_features.energy)) if features.sensevoice_features.energy else 0,
            "speaking_rate": 0.0  # Placeholder
        }
        
        linguistic_summary_dict = await gemma4_client.generate_linguistic_summary(
            feature_dict,
            result.stress_score
        )
        
        # Update result with Gemma4 linguistic summary
        result.linguistic_summary = LinguisticSummary(
            themes=linguistic_summary_dict.get("themes", []),
            emotions=linguistic_summary_dict.get("emotions", {}),
            patterns=linguistic_summary_dict.get("patterns", [])
        )
        
        # Store result in database
        storage = get_storage()
        document = VoiceAnalysisDocument(
            user_id=result.user_id,
            timestamp=result.timestamp,
            audio_features=features,  # Use already extracted features
            stress_score=result.stress_score,
            linguistic_summary=result.linguistic_summary,  # Use Gemma4 summary
            audio_duration_seconds=result.audio_duration_seconds,
            processing_time_ms=result.processing_time_ms,
            model_versions=ModelVersions(
                sensevoice=settings.sensevoice_version,
                wav2vec2=settings.wav2vec2_version,
                gemma4=settings.gemma4_version
            )
        )
        
        doc_id = await storage.store_voice_analysis(document)
        
        # Trigger baseline recalculation in background
        background_tasks.add_task(trigger_baseline_calculation, user_id)
        
        logger.info(
            "Audio processing successful",
            user_id=user_id,
            doc_id=doc_id,
            stress_score=result.stress_score
        )
        
        return result
        
    except InvalidAudioError as e:
        logger.warning("Invalid audio data", user_id=user_id, error=str(e))
        raise HTTPException(status_code=400, detail=f"Invalid audio: {e}")
        
    except ProcessingTimeoutError as e:
        logger.warning("Processing timeout", user_id=user_id, error=str(e))
        raise HTTPException(status_code=408, detail=f"Processing timeout: {e}")
        
    except ModelUnavailableError as e:
        logger.error("Model unavailable", error=str(e))
        raise HTTPException(status_code=503, detail=f"Service unavailable: {e}")
        
    except Exception as e:
        logger.error("Audio processing failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def audio_health():
    """Check audio processing service health."""
    try:
        processor = await get_processor()
        return {
            "status": "healthy" if processor.models_loaded else "degraded",
            "models_loaded": processor.models_loaded,
            "service": "audio_processor"
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "models_loaded": False,
            "service": "audio_processor",
            "error": str(e)
        }
