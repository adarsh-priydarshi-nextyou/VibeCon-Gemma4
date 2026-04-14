"""
Insights API endpoints.
"""
from fastapi import APIRouter, HTTPException, Header, Request
from typing import List, Optional
from services.gemma4_client import get_gemma4_client
from storage.voice_storage import get_storage
from models.schemas import Insight, InsightDocument, ContextWindow
from datetime import datetime, timedelta
from logger import get_logger
from utils.device_id import get_or_create_device_id

logger = get_logger(__name__)

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.get("/health")
async def insights_health():
    """Check insights service health."""
    return {
        "status": "healthy",
        "service": "insight_generator"
    }


@router.get("/{user_id}", response_model=List[Insight])
async def get_insights(
    request: Request,
    user_id: Optional[str] = None
):
    """
    Get personalized insights for user.
    
    User ID is automatically generated from device fingerprint if not provided.
    
    Args:
        request: FastAPI request object
        user_id: Optional user identifier (auto-generated if not provided)
        
    Returns:
        List of insights
        
    Requirements: 8.1, 8.2, 9.1
    """
    try:
        # Get or create device-based user ID
        if not user_id:
            user_id = get_or_create_device_id(request)
        storage = get_storage()
        gemma4 = get_gemma4_client()
        
        # Retrieve 3-day context
        context = await storage.retrieve_user_context(user_id, days=3)
        
        voice_scores = context.get("voice_scores", [])
        sleep_debt = context.get("sleep_debt", [])
        meeting_density = context.get("meeting_density", [])
        
        if not voice_scores:
            logger.info("No voice data for insights", user_id=user_id)
            return []
        
        # Get baseline for comparison
        baseline_doc = await storage.retrieve_latest_baseline(user_id)
        baseline = {
            "stress": baseline_doc.get("baseline_stress", 0.5),
            "sleep_debt": baseline_doc.get("baseline_sleep_debt", 0.0),
            "meeting_density": baseline_doc.get("baseline_meeting_density", 0.0)
        } if baseline_doc else None
        
        # Generate insights using Gemma4
        baseline_stress = baseline.get("stress") if baseline else None
        insights_data = await gemma4.generate_insights(
            voice_scores, sleep_debt, meeting_density, baseline_stress
        )
        
        # Calculate correlations and deviations
        import numpy as np
        
        # Correlations (if we have enough data)
        sleep_corr = 0.0
        meeting_corr = 0.0
        if len(voice_scores) >= 2 and len(sleep_debt) >= 2:
            # Align arrays to same length
            min_len = min(len(voice_scores), len(sleep_debt))
            if min_len >= 2:
                sleep_corr = float(np.corrcoef(voice_scores[:min_len], sleep_debt[:min_len])[0, 1])
                if np.isnan(sleep_corr):
                    sleep_corr = 0.0
        
        if len(voice_scores) >= 2 and len(meeting_density) >= 2:
            min_len = min(len(voice_scores), len(meeting_density))
            if min_len >= 2:
                meeting_corr = float(np.corrcoef(voice_scores[:min_len], meeting_density[:min_len])[0, 1])
                if np.isnan(meeting_corr):
                    meeting_corr = 0.0
        
        # Deviations from baseline
        from models.schemas import Correlations, Deviations
        
        avg_stress = sum(voice_scores) / len(voice_scores) if voice_scores else 0
        avg_sleep = sum(sleep_debt) / len(sleep_debt) if sleep_debt else 0
        avg_meetings = sum(meeting_density) / len(meeting_density) if meeting_density else 0
        
        correlations = Correlations(
            sleep_correlation=sleep_corr,
            meeting_correlation=meeting_corr
        )
        
        deviations = Deviations(
            stress_deviation=avg_stress - baseline_stress if baseline_stress else 0.0,
            sleep_deviation=avg_sleep - baseline.get("sleep_debt", 0) if baseline else 0.0,
            meeting_deviation=avg_meetings - baseline.get("meeting_density", 0) if baseline else 0.0
        )
        
        # Store insight
        insight_doc = InsightDocument(
            user_id=user_id,
            generation_date=datetime.now(),
            stress_pattern=insights_data["pattern"],
            pattern_description=insights_data["pattern_description"],
            correlations=correlations,
            deviations=deviations,
            contributing_factors=insights_data["contributing_factors"],
            observations=insights_data["observations"],
            context_window=ContextWindow(
                start_date=datetime.now() - timedelta(days=3),
                end_date=datetime.now(),
                data_points=len(voice_scores)
            )
        )
        
        await storage.store_insight(insight_doc)
        
        # Format response
        insights = [
            Insight(
                stress_pattern=insights_data["pattern"],
                pattern_description=insights_data["pattern_description"],
                contributing_factors=insights_data["contributing_factors"],
                observations=insights_data["observations"],
                generation_date=datetime.now()
            )
        ]
        
        logger.info("Insights generated", user_id=user_id, count=len(insights))
        
        return insights
        
    except Exception as e:
        logger.error("Insights generation failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate insights")
