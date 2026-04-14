"""
Baseline calculation engine for Voice Analysis and Intervention System.
Implements rolling 7-day baseline calculation with exponential decay weighting.
"""
import numpy as np
from typing import List, Dict, Any
from datetime import datetime, timedelta
from models.schemas import BaselineDocument, DateRange, BaselineMetrics
from storage.voice_storage import VoiceStorage, get_storage
from config import settings
from logger import get_logger
import time

logger = get_logger(__name__)


class InsufficientDataError(Exception):
    """Raised when insufficient data is available for baseline calculation."""
    pass


class HistoricalData:
    """Container for historical data used in baseline calculation."""
    
    def __init__(
        self,
        voice_scores: List[float],
        sleep_debt: List[float],
        meeting_density: List[float],
        timestamps: List[datetime]
    ):
        self.voice_scores = voice_scores
        self.sleep_debt = sleep_debt
        self.meeting_density = meeting_density
        self.timestamps = timestamps


class BaselineEngine:
    """
    Baseline calculation engine for rolling 7-day metrics.
    
    Calculates baseline stress, sleep debt, and meeting density
    using exponential decay weighting (recent data weighted higher).
    
    Requirements: 5.1, 5.2, 5.3, 6.1, 6.2, 6.3, 6.4
    """
    
    def __init__(self, storage: VoiceStorage = None):
        """
        Initialize BaselineEngine.
        
        Args:
            storage: VoiceStorage instance (defaults to global instance)
        """
        self.storage = storage or get_storage()
        self.min_data_points = 3  # Minimum days of data required
    
    async def retrieve_historical_data(
        self,
        user_id: str,
        days: int = 7
    ) -> HistoricalData:
        """
        Retrieve historical data from Voice_Storage.
        
        Args:
            user_id: User identifier
            days: Number of days to retrieve (default 7)
            
        Returns:
            HistoricalData with voice scores, sleep debt, meeting density
            
        Raises:
            InsufficientDataError: If less than minimum data points available
            
        Requirements: 5.1, 5.2, 5.3
        """
        # Get user context (includes voice scores, sleep debt, meeting density)
        context = await self.storage.retrieve_user_context(user_id, days)
        
        voice_scores = context.get("voice_scores", [])
        sleep_debt = context.get("sleep_debt", [])
        meeting_density = context.get("meeting_density", [])
        timestamps = context.get("timestamps", [])
        
        # Check minimum data requirement
        unique_days = len(set(ts.date() for ts in timestamps)) if timestamps else 0
        
        if unique_days < self.min_data_points:
            raise InsufficientDataError(
                f"Insufficient data: {unique_days} days available, "
                f"{self.min_data_points} days required"
            )
        
        logger.info(
            "Retrieved historical data",
            user_id=user_id,
            days=days,
            voice_samples=len(voice_scores),
            unique_days=unique_days
        )
        
        return HistoricalData(
            voice_scores=voice_scores,
            sleep_debt=sleep_debt,
            meeting_density=meeting_density,
            timestamps=timestamps
        )
    
    def compute_weighted_average(
        self,
        values: List[float],
        days: int = 7
    ) -> float:
        """
        Compute weighted average with exponential decay.
        
        Recent data is weighted more heavily than older data.
        Uses exponential decay: weight = exp(-0.2 * day_index)
        
        Args:
            values: List of values to average
            days: Number of days (for weight calculation)
            
        Returns:
            Weighted average
            
        Requirements: 6.1, 6.2
        """
        if not values:
            return 0.0
        
        # Generate exponential decay weights (more recent = higher weight)
        weights = [np.exp(-0.2 * i) for i in range(days)]
        
        # Normalize weights to sum to 1
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        
        # If we have fewer values than days, adjust weights
        if len(values) < len(weights):
            weights = weights[:len(values)]
            total_weight = sum(weights)
            if total_weight > 0:
                weights = [w / total_weight for w in weights]
        
        # Calculate weighted average
        # Reverse values so most recent is first
        values_reversed = list(reversed(values))
        weighted_sum = sum(w * v for w, v in zip(weights, values_reversed))
        
        return weighted_sum
    
    async def calculate_baseline(self, user_id: str) -> BaselineMetrics:
        """
        Calculate 7-day rolling baseline for user.
        
        Incorporates voice scores, sleep debt, and meeting density
        with exponential decay weighting.
        
        Args:
            user_id: User identifier
            
        Returns:
            BaselineMetrics with calculated baselines
            
        Raises:
            InsufficientDataError: If less than 3 days of data available
            
        Requirements: 6.1, 6.2, 6.4
        """
        start_time = time.time()
        
        # Retrieve historical data
        data = await self.retrieve_historical_data(user_id, days=7)
        
        # Calculate weighted averages
        baseline_stress = self.compute_weighted_average(data.voice_scores, days=7)
        baseline_sleep_debt = self.compute_weighted_average(data.sleep_debt, days=7)
        baseline_meeting_density = self.compute_weighted_average(data.meeting_density, days=7)
        
        # Get previous baseline for comparison
        previous_baseline_doc = await self.storage.retrieve_latest_baseline(user_id)
        previous_baseline_stress = None
        change_percentage = None
        
        if previous_baseline_doc:
            previous_baseline_stress = previous_baseline_doc.get("baseline_stress")
            if previous_baseline_stress and previous_baseline_stress > 0:
                change_percentage = (
                    (baseline_stress - previous_baseline_stress) / previous_baseline_stress * 100
                )
        
        calculation_time = time.time() - start_time
        
        # Check SLA (< 1 second)
        if calculation_time > settings.baseline_timeout_seconds:
            logger.warning(
                "Baseline calculation exceeded SLA",
                user_id=user_id,
                calculation_time_seconds=calculation_time,
                sla_seconds=settings.baseline_timeout_seconds
            )
        
        metrics = BaselineMetrics(
            user_id=user_id,
            baseline_stress=baseline_stress,
            baseline_sleep_debt=baseline_sleep_debt,
            baseline_meeting_density=baseline_meeting_density,
            calculation_date=datetime.now(),
            change_percentage=change_percentage
        )
        
        logger.info(
            "Baseline calculated",
            user_id=user_id,
            baseline_stress=baseline_stress,
            baseline_sleep_debt=baseline_sleep_debt,
            baseline_meeting_density=baseline_meeting_density,
            change_percentage=change_percentage,
            calculation_time_seconds=calculation_time
        )
        
        return metrics
    
    async def calculate_and_store_baseline(self, user_id: str) -> str:
        """
        Calculate baseline and persist to storage.
        
        Args:
            user_id: User identifier
            
        Returns:
            Document ID of stored baseline
            
        Requirements: 6.3
        """
        # Calculate baseline
        metrics = await self.calculate_baseline(user_id)
        
        # Get previous baseline for document
        previous_baseline_doc = await self.storage.retrieve_latest_baseline(user_id)
        previous_baseline_stress = (
            previous_baseline_doc.get("baseline_stress")
            if previous_baseline_doc else None
        )
        
        # Create document
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        document = BaselineDocument(
            user_id=user_id,
            calculation_date=metrics.calculation_date,
            baseline_stress=metrics.baseline_stress,
            baseline_sleep_debt=metrics.baseline_sleep_debt,
            baseline_meeting_density=metrics.baseline_meeting_density,
            data_points_used=7,
            date_range=DateRange(start=start_date, end=end_date),
            previous_baseline_stress=previous_baseline_stress,
            change_percentage=metrics.change_percentage
        )
        
        # Store baseline
        doc_id = await self.storage.store_baseline(document)
        
        logger.info(
            "Baseline stored",
            user_id=user_id,
            doc_id=doc_id
        )
        
        return doc_id


# Global engine instance
_engine_instance: BaselineEngine = None


def get_baseline_engine() -> BaselineEngine:
    """Get global BaselineEngine instance."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = BaselineEngine()
    return _engine_instance
