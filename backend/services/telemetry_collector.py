"""
Telemetry collection service for Voice Analysis and Intervention System.
Captures user interaction data with audio interventions.
"""
from typing import Optional
from datetime import datetime
from models.schemas import (
    InterventionTelemetryDocument,
    SkipStatus,
    DeviceInfo,
)
from storage.voice_storage import VoiceStorage, get_storage
from config import settings
from logger import get_logger
import time

logger = get_logger(__name__)


class PersistenceError(Exception):
    """Raised when telemetry cannot be persisted after retries."""
    pass


class TelemetryCollector:
    """
    Telemetry collection service for intervention interactions.
    
    Captures play events, feedback, and calculates skip status.
    Persists telemetry within 1-second SLA.
    
    Requirements: 13.1, 13.2, 13.3, 13.4, 13.5
    """
    
    def __init__(self, storage: VoiceStorage = None):
        """
        Initialize TelemetryCollector.
        
        Args:
            storage: VoiceStorage instance (defaults to global instance)
        """
        self.storage = storage or get_storage()
    
    def calculate_skip_status(
        self,
        play_duration: float,
        total_duration: float
    ) -> SkipStatus:
        """
        Calculate skip status based on play duration.
        
        Args:
            play_duration: Seconds of audio played
            total_duration: Total audio duration in seconds
            
        Returns:
            SkipStatus with early_skip, partial_skip, completed flags
            
        Requirements: 13.3
        """
        early_skip = play_duration < 5.0
        partial_skip = play_duration < (0.5 * total_duration)
        completed = play_duration >= (0.8 * total_duration)
        
        status = SkipStatus(
            early_skip=early_skip,
            partial_skip=partial_skip,
            completed=completed
        )
        
        logger.debug(
            "Skip status calculated",
            play_duration=play_duration,
            total_duration=total_duration,
            early_skip=early_skip,
            partial_skip=partial_skip,
            completed=completed
        )
        
        return status
    
    def capture_play_event(
        self,
        user_id: str,
        audio_id: str,
        audio_url: str,
        play_duration: float,
        total_duration: float,
        stress_score_at_interaction: float,
        session_id: str,
        device_info: DeviceInfo
    ) -> InterventionTelemetryDocument:
        """
        Capture audio play event with duration metrics.
        
        Args:
            user_id: User identifier
            audio_id: Intervention audio ID
            audio_url: Intervention audio URL
            play_duration: Seconds of audio played
            total_duration: Total audio duration
            stress_score_at_interaction: User's stress score when playing
            session_id: Session identifier
            device_info: Device information
            
        Returns:
            InterventionTelemetryDocument ready for persistence
            
        Requirements: 13.1, 13.2, 13.3
        """
        # Calculate skip status
        skip_status = self.calculate_skip_status(play_duration, total_duration)
        
        # Calculate completion percentage
        completion_percentage = (play_duration / total_duration * 100) if total_duration > 0 else 0.0
        completion_percentage = min(100.0, completion_percentage)
        
        telemetry = InterventionTelemetryDocument(
            user_id=user_id,
            audio_id=audio_id,
            audio_url=audio_url,
            timestamp=datetime.now(),
            play_duration_seconds=play_duration,
            total_duration_seconds=total_duration,
            completion_percentage=completion_percentage,
            early_skip=skip_status.early_skip,
            partial_skip=skip_status.partial_skip,
            completed=skip_status.completed,
            like_status=None,
            dislike_status=None,
            feedback_text=None,
            stress_score_at_interaction=stress_score_at_interaction,
            session_id=session_id,
            device_info=device_info
        )
        
        logger.info(
            "Play event captured",
            user_id=user_id,
            audio_id=audio_id,
            play_duration=play_duration,
            completion_percentage=completion_percentage,
            early_skip=skip_status.early_skip,
            completed=skip_status.completed
        )
        
        return telemetry
    
    def capture_feedback_event(
        self,
        user_id: str,
        audio_id: str,
        audio_url: str,
        like_status: bool,
        feedback_text: Optional[str],
        stress_score_at_interaction: float,
        session_id: str,
        device_info: DeviceInfo,
        play_duration: float = 0.0,
        total_duration: float = 1.0
    ) -> InterventionTelemetryDocument:
        """
        Capture user feedback event.
        
        Args:
            user_id: User identifier
            audio_id: Intervention audio ID
            audio_url: Intervention audio URL
            like_status: True if liked, False if disliked
            feedback_text: Optional text feedback
            stress_score_at_interaction: User's stress score
            session_id: Session identifier
            device_info: Device information
            play_duration: Play duration (optional)
            total_duration: Total duration (optional)
            
        Returns:
            InterventionTelemetryDocument ready for persistence
            
        Requirements: 13.4
        """
        # Calculate skip status
        skip_status = self.calculate_skip_status(play_duration, total_duration)
        completion_percentage = (play_duration / total_duration * 100) if total_duration > 0 else 0.0
        
        telemetry = InterventionTelemetryDocument(
            user_id=user_id,
            audio_id=audio_id,
            audio_url=audio_url,
            timestamp=datetime.now(),
            play_duration_seconds=play_duration,
            total_duration_seconds=total_duration,
            completion_percentage=completion_percentage,
            early_skip=skip_status.early_skip,
            partial_skip=skip_status.partial_skip,
            completed=skip_status.completed,
            like_status=like_status if like_status else None,
            dislike_status=not like_status if like_status is not None else None,
            feedback_text=feedback_text,
            stress_score_at_interaction=stress_score_at_interaction,
            session_id=session_id,
            device_info=device_info
        )
        
        logger.info(
            "Feedback event captured",
            user_id=user_id,
            audio_id=audio_id,
            like_status=like_status,
            has_feedback_text=feedback_text is not None
        )
        
        return telemetry
    
    async def record_interaction(
        self,
        telemetry: InterventionTelemetryDocument
    ) -> str:
        """
        Record user interaction with audio intervention.
        
        Persists telemetry to storage within 1-second SLA.
        
        Args:
            telemetry: InterventionTelemetryDocument to persist
            
        Returns:
            Document ID of stored telemetry
            
        Raises:
            PersistenceError: If telemetry cannot be persisted after retries
            
        Requirements: 13.5
        """
        start_time = time.time()
        
        try:
            doc_id = await self.storage.store_telemetry(telemetry)
            
            persistence_time = time.time() - start_time
            
            # Check SLA (< 1 second)
            if persistence_time > settings.telemetry_timeout_seconds:
                logger.warning(
                    "Telemetry persistence exceeded SLA",
                    user_id=telemetry.user_id,
                    audio_id=telemetry.audio_id,
                    persistence_time_seconds=persistence_time,
                    sla_seconds=settings.telemetry_timeout_seconds
                )
            
            logger.info(
                "Telemetry recorded",
                user_id=telemetry.user_id,
                audio_id=telemetry.audio_id,
                doc_id=doc_id,
                persistence_time_seconds=persistence_time
            )
            
            return doc_id
            
        except Exception as e:
            logger.error(
                "Failed to record telemetry",
                user_id=telemetry.user_id,
                audio_id=telemetry.audio_id,
                error=str(e)
            )
            raise PersistenceError(f"Failed to persist telemetry: {e}")


# Global collector instance
_collector_instance: Optional[TelemetryCollector] = None


def get_telemetry_collector() -> TelemetryCollector:
    """Get global TelemetryCollector instance."""
    global _collector_instance
    if _collector_instance is None:
        _collector_instance = TelemetryCollector()
    return _collector_instance
