"""
MongoDB initialization script for Voice Analysis and Intervention System.
Creates collections and indexes as defined in the design document.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from logger import get_logger

logger = get_logger(__name__)


async def create_collections_and_indexes():
    """Create MongoDB collections and indexes."""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_database]
    
    logger.info("Initializing MongoDB collections and indexes")
    
    # Voice Analysis Collection
    logger.info("Creating voice_analysis collection")
    await db.create_collection("voice_analysis")
    await db.voice_analysis.create_index([("user_id", 1), ("timestamp", -1)])
    await db.voice_analysis.create_index([("user_id", 1), ("stress_score", 1)])
    await db.voice_analysis.create_index([("timestamp", -1)])
    logger.info("voice_analysis collection created with indexes")
    
    # Baseline Metrics Collection
    logger.info("Creating baseline_metrics collection")
    await db.create_collection("baseline_metrics")
    await db.baseline_metrics.create_index([("user_id", 1), ("calculation_date", -1)])
    await db.baseline_metrics.create_index([("user_id", 1)])
    logger.info("baseline_metrics collection created with indexes")
    
    # Contextual Data Collection
    logger.info("Creating contextual_data collection")
    await db.create_collection("contextual_data")
    await db.contextual_data.create_index([("user_id", 1), ("date", -1)])
    await db.contextual_data.create_index([("user_id", 1)])
    logger.info("contextual_data collection created with indexes")
    
    # Audio Intervention Database Collection
    logger.info("Creating audio_intervention_database collection")
    await db.create_collection("audio_intervention_database")
    await db.audio_intervention_database.create_index([("category", 1), ("effectiveness_rating", -1)])
    await db.audio_intervention_database.create_index([("audio_id", 1)])
    await db.audio_intervention_database.create_index([("tags", 1)])
    logger.info("audio_intervention_database collection created with indexes")
    
    # Intervention Telemetry Collection
    logger.info("Creating intervention_telemetry collection")
    await db.create_collection("intervention_telemetry")
    await db.intervention_telemetry.create_index([("user_id", 1), ("timestamp", -1)])
    await db.intervention_telemetry.create_index([("audio_id", 1), ("user_id", 1)])
    await db.intervention_telemetry.create_index([("user_id", 1), ("like_status", 1)])
    await db.intervention_telemetry.create_index([("user_id", 1), ("early_skip", 1)])
    logger.info("intervention_telemetry collection created with indexes")
    
    # Insights Collection
    logger.info("Creating insights collection")
    await db.create_collection("insights")
    await db.insights.create_index([("user_id", 1), ("generation_date", -1)])
    await db.insights.create_index([("user_id", 1)])
    logger.info("insights collection created with indexes")
    
    logger.info("MongoDB initialization complete")
    
    # Close connection
    client.close()


if __name__ == "__main__":
    asyncio.run(create_collections_and_indexes())
