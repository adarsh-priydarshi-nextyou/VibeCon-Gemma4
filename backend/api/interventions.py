"""
Interventions API endpoints.
"""
from fastapi import APIRouter, HTTPException, Header, Request
from typing import List, Optional
from services.gemma4_client import get_gemma4_client
from storage.voice_storage import get_storage
from models.schemas import InterventionRecommendation
from logger import get_logger
from utils.device_id import get_or_create_device_id
import numpy as np

logger = get_logger(__name__)

router = APIRouter(prefix="/api/interventions", tags=["interventions"])


@router.get("/health")
async def interventions_health():
    """Check interventions service health."""
    return {
        "status": "healthy",
        "service": "intervention_recommender"
    }


@router.get("/{user_id}", response_model=List[InterventionRecommendation])
async def get_recommendations(
    request: Request,
    user_id: Optional[str] = None
):
    """
    Get intervention recommendations for user.
    
    User ID is automatically generated from device fingerprint if not provided.
    
    Args:
        request: FastAPI request object
        user_id: Optional user identifier (auto-generated if not provided)
        
    Returns:
        List of top 3 intervention recommendations
        
    Requirements: 11.1, 11.2, 11.3, 12.1
    """
    try:
        # Get or create device-based user ID
        if not user_id:
            user_id = get_or_create_device_id(request)
        storage = get_storage()
        gemma4 = get_gemma4_client()
        
        # Retrieve user context
        context = await storage.retrieve_user_context(user_id, days=3)
        voice_scores = context.get("voice_scores", [])
        
        if not voice_scores:
            logger.info("No voice data for recommendations", user_id=user_id)
            return []
        
        # Get current stress score (most recent)
        current_stress = voice_scores[-1] if voice_scores else 0.5
        
        # Retrieve intervention database
        interventions = await storage.retrieve_intervention_database()
        
        # Retrieve user history
        user_history = await storage.retrieve_user_intervention_history(user_id)
        
        # Generate recommendations using Gemma4
        recommendations_data = await gemma4.recommend_interventions(
            stress_score=current_stress,
            intervention_history=user_history,
            available_interventions=interventions
        )
        
        # Format response
        recommendations = [
            InterventionRecommendation(**rec)
            for rec in recommendations_data
        ]
        
        logger.info(
            "Recommendations generated",
            user_id=user_id,
            count=len(recommendations),
            current_stress=current_stress
        )
        
        return recommendations
        
    except Exception as e:
        logger.error("Recommendations generation failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")
