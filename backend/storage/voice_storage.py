"""
MongoDB storage layer for Voice Analysis and Intervention System.
Implements VoiceStorage class with CRUD operations and retry logic.
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import List, Optional
from datetime import datetime, timedelta
from models.schemas import (
    VoiceAnalysisDocument,
    BaselineDocument,
    InterventionTelemetryDocument,
    AudioInterventionDocument,
    InsightDocument,
    ContextualDataDocument,
)
from config import settings
from logger import get_logger
from utils.retry import retry_with_backoff

logger = get_logger(__name__)


class VoiceStorage:
    """
    MongoDB storage layer for voice analysis data.
    
    Provides CRUD operations for all collections with retry logic
    and error handling as specified in Requirements 4, 5, 7, 10.
    """
    
    def __init__(self, mongodb_uri: Optional[str] = None, database_name: Optional[str] = None):
        """
        Initialize VoiceStorage with MongoDB connection.
        
        Args:
            mongodb_uri: MongoDB connection URI (defaults to settings)
            database_name: Database name (defaults to settings)
        """
        self.mongodb_uri = mongodb_uri or settings.mongodb_uri
        self.database_name = database_name or settings.mongodb_database
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        
    async def connect(self):
        """Establish MongoDB connection."""
        if not self.client:
            self.client = AsyncIOMotorClient(self.mongodb_uri)
            self.db = self.client[self.database_name]
            logger.info("Connected to MongoDB", database=self.database_name)
    
    async def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            logger.info("Disconnected from MongoDB")
    
    # Voice Analysis Operations
    
    @retry_with_backoff(max_attempts=3, base_delay=1.0)
    async def store_voice_analysis(self, analysis: VoiceAnalysisDocument) -> str:
        """
        Store voice analysis result.
        
        Args:
            analysis: VoiceAnalysisDocument to store
            
        Returns:
            Document ID as string
            
        Raises:
            Exception: If storage fails after retries
            
        Requirements: 4.1, 4.2, 4.3
        """
        await self.connect()
        
        try:
            result = await self.db.voice_analysis.insert_one(
                analysis.dict(by_alias=True, exclude={"id"})
            )
            doc_id = str(result.inserted_id)
            
            logger.info(
                "Stored voice analysis",
                user_id=analysis.user_id,
                doc_id=doc_id,
                stress_score=analysis.stress_score
            )
            
            return doc_id
            
        except Exception as e:
            logger.error(
                "Failed to store voice analysis",
                user_id=analysis.user_id,
                error=str(e)
            )
            raise
    
    async def retrieve_historical_voice_scores(
        self,
        user_id: str,
        days: int
    ) -> List[dict]:
        """
        Retrieve historical voice scores for specified days.
        
        Args:
            user_id: User identifier
            days: Number of days to retrieve
            
        Returns:
            List of voice score documents
            
        Requirements: 5.1, 5.4
        """
        await self.connect()
        
        start_date = datetime.now() - timedelta(days=days)
        
        cursor = self.db.voice_analysis.find(
            {
                "user_id": user_id,
                "timestamp": {"$gte": start_date}
            },
            {
                "stress_score": 1,
                "timestamp": 1,
                "_id": 0
            }
        ).sort("timestamp", -1)
        
        results = await cursor.to_list(length=None)
        
        logger.info(
            "Retrieved historical voice scores",
            user_id=user_id,
            days=days,
            count=len(results)
        )
        
        return results
    
    # Baseline Operations
    
    @retry_with_backoff(max_attempts=3, base_delay=1.0)
    async def store_baseline(self, baseline: BaselineDocument) -> str:
        """
        Store baseline metrics.
        
        Args:
            baseline: BaselineDocument to store
            
        Returns:
            Document ID as string
            
        Requirements: 6.3
        """
        await self.connect()
        
        try:
            result = await self.db.baseline_metrics.insert_one(
                baseline.dict(by_alias=True, exclude={"id"})
            )
            doc_id = str(result.inserted_id)
            
            logger.info(
                "Stored baseline metrics",
                user_id=baseline.user_id,
                doc_id=doc_id,
                baseline_stress=baseline.baseline_stress
            )
            
            return doc_id
            
        except Exception as e:
            logger.error(
                "Failed to store baseline",
                user_id=baseline.user_id,
                error=str(e)
            )
            raise
    
    async def retrieve_latest_baseline(self, user_id: str) -> Optional[dict]:
        """
        Retrieve latest baseline for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Latest baseline document or None
        """
        await self.connect()
        
        result = await self.db.baseline_metrics.find_one(
            {"user_id": user_id},
            sort=[("calculation_date", -1)]
        )
        
        if result:
            logger.info(
                "Retrieved latest baseline",
                user_id=user_id,
                baseline_stress=result.get("baseline_stress")
            )
        
        return result
    
    # Contextual Data Operations
    
    async def retrieve_user_context(self, user_id: str, days: int) -> dict:
        """
        Retrieve complete user context including scores, sleep, meetings.
        
        Args:
            user_id: User identifier
            days: Number of days to retrieve
            
        Returns:
            Dictionary with voice scores, sleep debt, meeting density
            
        Requirements: 7.1, 7.2, 7.3, 7.4
        """
        await self.connect()
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Retrieve voice scores
        voice_scores = await self.retrieve_historical_voice_scores(user_id, days)
        
        # Retrieve contextual data
        cursor = self.db.contextual_data.find(
            {
                "user_id": user_id,
                "date": {"$gte": start_date}
            }
        ).sort("date", -1)
        
        contextual_data = await cursor.to_list(length=None)
        
        # Aggregate data
        context = {
            "user_id": user_id,
            "voice_scores": [doc["stress_score"] for doc in voice_scores],
            "timestamps": [doc["timestamp"] for doc in voice_scores],
            "sleep_debt": [doc["sleep_debt_hours"] for doc in contextual_data],
            "meeting_density": [doc["meeting_density"] for doc in contextual_data],
            "dates": [doc["date"] for doc in contextual_data],
        }
        
        logger.info(
            "Retrieved user context",
            user_id=user_id,
            days=days,
            voice_samples=len(voice_scores),
            contextual_records=len(contextual_data)
        )
        
        return context
    
    # Intervention Operations
    
    async def retrieve_intervention_database(self) -> List[dict]:
        """
        Retrieve labelled audio intervention database.
        
        Returns:
            List of audio intervention documents
            
        Requirements: 10.1, 10.3
        """
        await self.connect()
        
        cursor = self.db.audio_intervention_database.find({})
        results = await cursor.to_list(length=None)
        
        logger.info(
            "Retrieved intervention database",
            count=len(results)
        )
        
        return results
    
    async def retrieve_user_intervention_history(self, user_id: str) -> dict:
        """
        Retrieve user's intervention interaction history.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with liked, skipped, and completed interventions
            
        Requirements: 10.2, 10.3
        """
        await self.connect()
        
        # Get all telemetry for user
        cursor = self.db.intervention_telemetry.find(
            {"user_id": user_id}
        ).sort("timestamp", -1)
        
        telemetry = await cursor.to_list(length=None)
        
        # Aggregate by interaction type
        liked = [doc["audio_id"] for doc in telemetry if doc.get("like_status") is True]
        skipped = [doc["audio_id"] for doc in telemetry if doc.get("early_skip") is True]
        completed = [doc["audio_id"] for doc in telemetry if doc.get("completed") is True]
        
        # Count skip frequency per intervention
        skip_counts = {}
        for doc in telemetry:
            if doc.get("early_skip"):
                audio_id = doc["audio_id"]
                skip_counts[audio_id] = skip_counts.get(audio_id, 0) + 1
        
        history = {
            "user_id": user_id,
            "liked_interventions": list(set(liked)),
            "skipped_interventions": list(set(skipped)),
            "completed_interventions": list(set(completed)),
            "skip_counts": skip_counts,
            "total_interactions": len(telemetry)
        }
        
        logger.info(
            "Retrieved user intervention history",
            user_id=user_id,
            total_interactions=len(telemetry),
            liked_count=len(liked),
            skipped_count=len(skipped)
        )
        
        return history
    
    # Telemetry Operations
    
    @retry_with_backoff(max_attempts=3, base_delay=1.0)
    async def store_telemetry(self, telemetry: InterventionTelemetryDocument) -> str:
        """
        Store intervention telemetry.
        
        Args:
            telemetry: InterventionTelemetryDocument to store
            
        Returns:
            Document ID as string
            
        Requirements: 13.5, 14.1
        """
        await self.connect()
        
        try:
            result = await self.db.intervention_telemetry.insert_one(
                telemetry.dict(by_alias=True, exclude={"id"})
            )
            doc_id = str(result.inserted_id)
            
            logger.info(
                "Stored intervention telemetry",
                user_id=telemetry.user_id,
                audio_id=telemetry.audio_id,
                doc_id=doc_id,
                early_skip=telemetry.early_skip,
                completed=telemetry.completed
            )
            
            return doc_id
            
        except Exception as e:
            logger.error(
                "Failed to store telemetry",
                user_id=telemetry.user_id,
                audio_id=telemetry.audio_id,
                error=str(e)
            )
            raise
    
    # Insights Operations
    
    @retry_with_backoff(max_attempts=3, base_delay=1.0)
    async def store_insight(self, insight: InsightDocument) -> str:
        """
        Store generated insight.
        
        Args:
            insight: InsightDocument to store
            
        Returns:
            Document ID as string
        """
        await self.connect()
        
        try:
            result = await self.db.insights.insert_one(
                insight.dict(by_alias=True, exclude={"id"})
            )
            doc_id = str(result.inserted_id)
            
            logger.info(
                "Stored insight",
                user_id=insight.user_id,
                doc_id=doc_id,
                stress_pattern=insight.stress_pattern
            )
            
            return doc_id
            
        except Exception as e:
            logger.error(
                "Failed to store insight",
                user_id=insight.user_id,
                error=str(e)
            )
            raise
    
    async def retrieve_latest_insights(self, user_id: str, limit: int = 5) -> List[dict]:
        """
        Retrieve latest insights for user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of insights to retrieve
            
        Returns:
            List of insight documents
        """
        await self.connect()
        
        cursor = self.db.insights.find(
            {"user_id": user_id}
        ).sort("generation_date", -1).limit(limit)
        
        results = await cursor.to_list(length=limit)
        
        logger.info(
            "Retrieved latest insights",
            user_id=user_id,
            count=len(results)
        )
        
        return results


# Global storage instance
_storage_instance: Optional[VoiceStorage] = None


def get_storage() -> VoiceStorage:
    """Get global VoiceStorage instance."""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = VoiceStorage()
    return _storage_instance
