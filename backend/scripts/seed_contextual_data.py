"""
Seed script to populate dummy contextual data (sleep debt and meeting density).
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import random
from config import settings
from logger import get_logger

logger = get_logger(__name__)


async def seed_contextual_data(user_id: str = "test_user", days: int = 7):
    """
    Seed dummy contextual data for testing.
    
    Args:
        user_id: User identifier
        days: Number of days of data to generate
    """
    
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_database]
    
    logger.info(f"Seeding contextual data for user {user_id}")
    
    contextual_data = []
    
    for i in range(days):
        date = datetime.now() - timedelta(days=days - i - 1)
        
        # Generate realistic dummy data
        # Sleep debt: 0-4 hours (higher = more tired)
        sleep_debt = random.uniform(0.5, 3.5)
        
        # Meeting density: 0-1.5 meetings per hour (higher = busier)
        meeting_density = random.uniform(0.1, 1.2)
        
        # Add some patterns (weekends have less meetings, more sleep)
        if date.weekday() >= 5:  # Weekend
            sleep_debt *= 0.6  # Less sleep debt on weekends
            meeting_density *= 0.2  # Fewer meetings on weekends
        
        contextual_data.append({
            "user_id": user_id,
            "date": date,
            "sleep_debt_hours": round(sleep_debt, 2),
            "meeting_density": round(meeting_density, 2),
            "created_at": datetime.now()
        })
    
    # Clear existing contextual data for this user
    await db.contextual_data.delete_many({"user_id": user_id})
    
    # Insert new contextual data
    if contextual_data:
        result = await db.contextual_data.insert_many(contextual_data)
        logger.info(f"Seeded {len(result.inserted_ids)} contextual data records for {user_id}")
    
    client.close()


if __name__ == "__main__":
    import sys
    user_id = sys.argv[1] if len(sys.argv) > 1 else "test_user"
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    asyncio.run(seed_contextual_data(user_id, days))
