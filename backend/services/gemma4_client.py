"""
Gemma4 client for AI-powered analysis.
Now uses real Gemma4 LLM for linguistic summaries, insights, and recommendations.
"""
from typing import List, Dict, Any, Optional
from logger import get_logger
from services.gemma4_llm import gemma4_llm
import asyncio

logger = get_logger(__name__)


class ModelUnavailableError(Exception):
    """Raised when Gemma4 model is unavailable."""
    pass


class Gemma4Client:
    """
    Client for Gemma4 model interactions.
    
    Provides linguistic analysis, insights, and intervention recommendations
    using real Gemma4 LLM.
    """
    
    def __init__(self):
        """Initialize Gemma4 client."""
        self.llm = gemma4_llm
    
    async def initialize(self):
        """Initialize Gemma4 LLM."""
        await self.llm.initialize()
    
    async def generate_linguistic_summary(
        self,
        audio_features: Dict[str, Any],
        stress_score: float
    ) -> Dict[str, Any]:
        """
        Generate linguistic summary using Gemma4 LLM.
        
        Args:
            audio_features: Extracted audio features
            stress_score: Calculated stress score
            
        Returns:
            Dictionary with themes, emotions, patterns, summary_text
        """
        try:
            logger.info("Generating linguistic summary with Gemma4")
            
            # Use Gemma4 LLM
            summary = await self.llm.generate_linguistic_summary(
                audio_features,
                stress_score
            )
            
            logger.info("Linguistic summary generated successfully")
            return summary
            
        except Exception as e:
            logger.error(f"Linguistic summary generation failed: {e}")
            # Fallback
            return self._fallback_linguistic_summary(stress_score)
    
    def _fallback_linguistic_summary(self, stress_score: float) -> Dict[str, Any]:
        """Fallback when LLM unavailable."""
        themes = []
        if stress_score > 0.7:
            themes.append("high_stress")
        elif stress_score > 0.4:
            themes.append("moderate_stress")
        else:
            themes.append("low_stress")
        
        return {
            "summary_text": f"Voice analysis indicates {'elevated' if stress_score > 0.5 else 'normal'} stress levels.",
            "themes": themes,
            "emotions": {
                "stress": float(stress_score),
                "anxiety": float(stress_score * 0.8),
                "calmness": float(1 - stress_score)
            },
            "patterns": ["normal_voice_patterns"]
        }
    
    async def generate_insights(
        self,
        voice_scores: List[float],
        sleep_debt: List[float],
        meeting_density: List[float],
        baseline: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate insights using Gemma4 LLM with historical context.
        
        Args:
            voice_scores: Last 3 days of voice stress scores
            sleep_debt: Last 3 days of sleep debt (dummy)
            meeting_density: Last 3 days of meeting density (dummy)
            baseline: User's baseline stress score
            
        Returns:
            Insights with pattern, description, factors, observations
        """
        try:
            logger.info("Generating insights with Gemma4")
            
            # Use Gemma4 LLM
            insights = await self.llm.generate_insights(
                voice_scores,
                sleep_debt,
                meeting_density,
                baseline
            )
            
            logger.info(f"Insights generated: pattern={insights['pattern']}")
            return insights
            
        except Exception as e:
            logger.error(f"Insights generation failed: {e}")
            return self._fallback_insights(voice_scores)
    
    def _fallback_insights(self, voice_scores: List[float]) -> Dict[str, Any]:
        """Fallback insights without LLM."""
        if not voice_scores:
            return {
                "pattern": "insufficient_data",
                "pattern_description": "Not enough data to generate insights",
                "contributing_factors": ["Record more voice samples"],
                "observations": ["Need at least 3 recordings for analysis"]
            }
        
        avg_stress = sum(voice_scores) / len(voice_scores)
        pattern = "stable"
        
        if len(voice_scores) >= 2:
            trend = voice_scores[-1] - voice_scores[0]
            if trend > 0.1:
                pattern = "increasing"
            elif trend < -0.1:
                pattern = "decreasing"
        
        # Safe formatting with default values
        avg_stress_pct = avg_stress * 100 if avg_stress is not None else 0
        
        return {
            "pattern": pattern,
            "pattern_description": f"Your stress levels are {pattern} over the past {len(voice_scores)} recordings. Average stress is {avg_stress_pct:.0f}%.",
            "contributing_factors": [f"Average stress: {avg_stress_pct:.0f}%"],
            "observations": ["Pattern detected from voice data"]
        }
    
    async def recommend_interventions(
        self,
        stress_score: float,
        intervention_history: Dict[str, Any],
        available_interventions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Recommend top 3 interventions using Gemma4 LLM.
        
        Args:
            stress_score: Current stress score
            intervention_history: User's past intervention usage (dict format)
            available_interventions: Available intervention library
            
        Returns:
            Top 3 recommended interventions with reasoning
        """
        try:
            logger.info("Generating intervention recommendations with Gemma4")
            
            # Use Gemma4 LLM
            recommendations = await self.llm.recommend_interventions(
                stress_score,
                intervention_history,
                available_interventions
            )
            
            logger.info(f"Recommended {len(recommendations)} interventions")
            return recommendations
            
        except Exception as e:
            logger.error(f"Intervention recommendation failed: {e}")
            return self._fallback_recommendations(stress_score, available_interventions)
    
    def _fallback_recommendations(
        self,
        stress_score: float,
        interventions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Fallback recommendations without LLM."""
        scored = []
        for intervention in interventions:
            score = intervention.get("effectiveness", 0.5)
            
            # Match stress range
            target_range = intervention.get("target_stress_range", {})
            if target_range:
                min_stress = target_range.get("min", 0)
                max_stress = target_range.get("max", 1)
                if min_stress <= stress_score <= max_stress:
                    score += 0.2
            
            scored.append({
                **intervention,
                "relevance_score": min(1.0, score),
                "reasoning": f"Matched for stress level {stress_score:.0%}"
            })
        
        scored.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored[:3]


# Global instance
gemma4_client = Gemma4Client()


def get_gemma4_client() -> Gemma4Client:
    """Get global Gemma4Client instance."""
    return gemma4_client
