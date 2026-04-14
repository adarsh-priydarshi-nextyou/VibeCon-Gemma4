"""
Seed script to populate sample intervention data.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from logger import get_logger

logger = get_logger(__name__)


async def seed_interventions():
    """Seed sample audio interventions into database."""
    
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_database]
    
    logger.info("Seeding intervention database")
    
    interventions = [
        {
            "audio_id": "breathing-001",
            "audio_url": "https://example.com/audio/breathing-001.mp3",
            "title": "Deep Breathing Exercise",
            "description": "5-minute guided deep breathing to reduce stress",
            "duration_seconds": 300.0,
            "category": "breathing",
            "subcategory": "deep_breathing",
            "tags": ["stress", "anxiety", "quick"],
            "effectiveness_rating": 0.85,
            "usage_count": 0,
            "average_completion_rate": 0.0,
            "target_stress_range": {"min": 0.5, "max": 1.0},
            "recommended_for": ["high_stress", "anxiety", "quick_relief"]
        },
        {
            "audio_id": "meditation-001",
            "audio_url": "https://example.com/audio/meditation-001.mp3",
            "title": "Mindfulness Meditation",
            "description": "10-minute mindfulness meditation for stress relief",
            "duration_seconds": 600.0,
            "category": "meditation",
            "subcategory": "mindfulness",
            "tags": ["stress", "mindfulness", "calm"],
            "effectiveness_rating": 0.90,
            "usage_count": 0,
            "average_completion_rate": 0.0,
            "target_stress_range": {"min": 0.4, "max": 0.8},
            "recommended_for": ["moderate_stress", "mindfulness", "relaxation"]
        },
        {
            "audio_id": "music-001",
            "audio_url": "https://example.com/audio/music-001.mp3",
            "title": "Calming Nature Sounds",
            "description": "15 minutes of peaceful nature sounds",
            "duration_seconds": 900.0,
            "category": "music",
            "subcategory": "nature",
            "tags": ["relaxation", "nature", "ambient"],
            "effectiveness_rating": 0.75,
            "usage_count": 0,
            "average_completion_rate": 0.0,
            "target_stress_range": {"min": 0.3, "max": 0.7},
            "recommended_for": ["mild_stress", "relaxation", "sleep"]
        },
        {
            "audio_id": "breathing-002",
            "audio_url": "https://example.com/audio/breathing-002.mp3",
            "title": "Box Breathing Technique",
            "description": "7-minute box breathing for focus and calm",
            "duration_seconds": 420.0,
            "category": "breathing",
            "subcategory": "box_breathing",
            "tags": ["stress", "focus", "technique"],
            "effectiveness_rating": 0.88,
            "usage_count": 0,
            "average_completion_rate": 0.0,
            "target_stress_range": {"min": 0.6, "max": 1.0},
            "recommended_for": ["high_stress", "focus", "anxiety"]
        },
        {
            "audio_id": "meditation-002",
            "audio_url": "https://example.com/audio/meditation-002.mp3",
            "title": "Body Scan Meditation",
            "description": "12-minute body scan for deep relaxation",
            "duration_seconds": 720.0,
            "category": "meditation",
            "subcategory": "body_scan",
            "tags": ["relaxation", "body_awareness", "stress"],
            "effectiveness_rating": 0.82,
            "usage_count": 0,
            "average_completion_rate": 0.0,
            "target_stress_range": {"min": 0.4, "max": 0.9},
            "recommended_for": ["moderate_stress", "tension", "relaxation"]
        },
        {
            "audio_id": "music-002",
            "audio_url": "https://example.com/audio/music-002.mp3",
            "title": "Binaural Beats for Relaxation",
            "description": "20 minutes of theta wave binaural beats",
            "duration_seconds": 1200.0,
            "category": "music",
            "subcategory": "binaural",
            "tags": ["relaxation", "binaural", "deep"],
            "effectiveness_rating": 0.78,
            "usage_count": 0,
            "average_completion_rate": 0.0,
            "target_stress_range": {"min": 0.5, "max": 0.9},
            "recommended_for": ["moderate_stress", "deep_relaxation", "meditation"]
        }
    ]
    
    # Clear existing interventions
    await db.audio_intervention_database.delete_many({})
    
    # Insert new interventions
    result = await db.audio_intervention_database.insert_many(interventions)
    
    logger.info(f"Seeded {len(result.inserted_ids)} interventions")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_interventions())
