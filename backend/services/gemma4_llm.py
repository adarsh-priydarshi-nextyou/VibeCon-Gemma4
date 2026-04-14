"""
Gemma4 LLM Service for linguistic analysis and recommendations.
Uses local Gemma 2B model for text generation.
"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Dict, List, Any, Optional
import json
from logger import get_logger

logger = get_logger(__name__)


class Gemma4LLM:
    """
    Gemma4 LLM service for:
    1. Linguistic summary generation from voice features
    2. Insights generation from historical data
    3. Intervention recommendations
    """
    
    def __init__(self):
        """Initialize Gemma4 model."""
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # Use a non-gated alternative model for now
        # Options: "microsoft/phi-2", "TinyLlama/TinyLlama-1.1B-Chat-v1.0", "google/flan-t5-base"
        self.model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # Small, fast, no auth required
        
    async def initialize(self):
        """Load Gemma4 model."""
        from config import settings
        
        if not settings.enable_llm:
            logger.info("LLM disabled in config, using statistical fallback mode")
            return
        
        try:
            logger.info(f"Loading Gemma4 model on {self.device}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True
            )
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            self.model.eval()
            
            logger.info("Gemma4 model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Gemma4 model: {e}")
            # Fallback to statistical mode
            logger.warning("Running in statistical mode without LLM")
    
    def generate_text(self, prompt: str, max_length: int = 512) -> str:
        """
        Generate text using LLM.
        
        Args:
            prompt: Input prompt
            max_length: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        if self.model is None:
            return self._fallback_generation(prompt)
        
        try:
            # Format prompt for chat model
            formatted_prompt = f"<|system|>\nYou are a helpful AI assistant analyzing voice stress patterns.</s>\n<|user|>\n{prompt}</s>\n<|assistant|>\n"
            
            # Tokenize
            inputs = self.tokenizer(
                formatted_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048
            ).to(self.device)
            
            # Generate with reduced tokens for speed
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=min(max_length, 50),  # Limit to 50 tokens for speed
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    num_beams=1  # Disable beam search for speed
                )
            
            # Decode
            generated_text = self.tokenizer.decode(
                outputs[0],
                skip_special_tokens=True
            )
            
            # Extract only the assistant's response
            if "<|assistant|>" in generated_text:
                generated_text = generated_text.split("<|assistant|>")[-1].strip()
            
            return generated_text
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._fallback_generation(prompt)
    
    def _fallback_generation(self, prompt: str) -> str:
        """Fallback when LLM is unavailable."""
        if "linguistic summary" in prompt.lower():
            return "Moderate stress detected with elevated vocal patterns."
        elif "insights" in prompt.lower():
            return "Your stress levels show a stable pattern over recent recordings."
        elif "intervention" in prompt.lower():
            return "Deep breathing and theta reset recommended based on your stress profile."
        return "Analysis complete."
    
    async def generate_linguistic_summary(
        self,
        features: Dict[str, Any],
        stress_score: float
    ) -> Dict[str, Any]:
        """
        Generate linguistic summary from voice features.
        
        Args:
            features: Extracted voice features
            stress_score: Calculated stress score
            
        Returns:
            Linguistic summary with themes, emotions, patterns
        """
        try:
            # Create prompt
            prompt = f"""Analyze this voice sample and provide a brief linguistic summary.

Voice Features:
- Pitch: mean={features.get('pitch_mean', 0):.1f}Hz, std={features.get('pitch_std', 0):.1f}Hz
- Energy: mean={features.get('energy_mean', 0):.3f}
- Speaking rate: {features.get('speaking_rate', 0):.1f} syllables/sec
- Stress score: {stress_score:.2f} (0-1 scale)

Provide a concise summary (2-3 sentences) describing:
1. Emotional state
2. Stress indicators
3. Voice patterns observed

Summary:"""

            # Generate
            summary_text = self.generate_text(prompt, max_length=150)
            
            # Parse into structured format
            themes = []
            if stress_score > 0.7:
                themes.append("high_stress")
            elif stress_score > 0.4:
                themes.append("moderate_stress")
            else:
                themes.append("low_stress")
            
            emotions = {
                "stress": float(stress_score),
                "anxiety": float(stress_score * 0.8),
                "calmness": float(1 - stress_score)
            }
            
            patterns = []
            if features.get('pitch_std', 0) > 50:
                patterns.append("elevated_pitch_variability")
            if features.get('energy_mean', 0) > 0.3:
                patterns.append("high_vocal_energy")
            
            return {
                "summary_text": summary_text,
                "themes": themes,
                "emotions": emotions,
                "patterns": patterns
            }
            
        except Exception as e:
            logger.error(f"Linguistic summary generation failed: {e}")
            return self._fallback_linguistic_summary(stress_score)
    
    def _fallback_linguistic_summary(self, stress_score: float) -> Dict[str, Any]:
        """Fallback linguistic summary."""
        themes = ["moderate_stress"] if stress_score > 0.5 else ["low_stress"]
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
        Generate insights using Gemma4 with historical context.
        
        Args:
            voice_scores: Last 3 days of voice stress scores
            sleep_debt: Last 3 days of sleep debt (dummy)
            meeting_density: Last 3 days of meeting density (dummy)
            baseline: User's baseline stress score
            
        Returns:
            Insights with pattern, description, factors, observations
        """
        try:
            # Prepare context
            avg_stress = sum(voice_scores) / len(voice_scores) if voice_scores else 0
            avg_sleep = sum(sleep_debt) / len(sleep_debt) if sleep_debt else 0
            avg_meetings = sum(meeting_density) / len(meeting_density) if meeting_density else 0
            
            # Create prompt
            prompt = f"""Analyze this user's stress pattern over the last 3 days and provide insights.

Data:
- Voice stress scores (0-1): {[f'{s:.2f}' for s in voice_scores]}
- Average stress: {avg_stress:.2f}
- Sleep debt hours: {[f'{s:.1f}' for s in sleep_debt]}
- Meeting density (meetings/hour): {[f'{m:.2f}' for m in meeting_density]}
- Baseline stress: {baseline:.2f if baseline else 'Not established'}

Provide:
1. Pattern (increasing/decreasing/stable)
2. Key contributing factors (2-3 points)
3. Actionable observations (2-3 points)

Analysis:"""

            # Generate
            analysis = self.generate_text(prompt, max_length=300)
            
            # Determine pattern
            if len(voice_scores) >= 2:
                trend = voice_scores[-1] - voice_scores[0]
                if trend > 0.1:
                    pattern = "increasing"
                elif trend < -0.1:
                    pattern = "decreasing"
                else:
                    pattern = "stable"
            else:
                pattern = "insufficient_data"
            
            # Extract factors
            factors = []
            if avg_stress > 0.7:
                factors.append("High overall stress levels detected")
            if avg_sleep > 2:
                factors.append(f"Elevated sleep debt ({avg_sleep:.1f} hours)")
            if avg_meetings > 0.5:
                factors.append(f"High meeting density ({avg_meetings:.1f} meetings/hour)")
            
            # Extract observations
            observations = []
            if pattern == "increasing":
                observations.append("Upward stress trend detected")
                observations.append("Consider stress management interventions")
            elif pattern == "decreasing":
                observations.append("Positive downward trend")
                observations.append("Current strategies appear effective")
            else:
                observations.append("Stable pattern maintained")
            
            return {
                "pattern": pattern,
                "pattern_description": analysis,
                "contributing_factors": factors,
                "observations": observations
            }
            
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
        
        return {
            "pattern": pattern,
            "pattern_description": f"Your stress levels are {pattern} over the past {len(voice_scores)} recordings.",
            "contributing_factors": ["Voice stress analysis"],
            "observations": ["Pattern detected from voice data"]
        }
    
    async def recommend_interventions(
        self,
        stress_score: float,
        intervention_history: Dict[str, Any],
        available_interventions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Recommend top 3 interventions using Gemma4.
        
        Args:
            stress_score: Current stress score
            intervention_history: User's past intervention usage (dict format)
            available_interventions: Available intervention library
            
        Returns:
            Top 3 recommended interventions with reasoning
        """
        try:
            # Prepare context
            history_summary = self._summarize_history(intervention_history)
            interventions_list = self._format_interventions(available_interventions)
            
            # Create prompt
            prompt = f"""Recommend the top 3 audio interventions for this user.

Current stress score: {stress_score:.2f} (0-1 scale)

User's intervention history:
{history_summary}

Available interventions:
{interventions_list}

Based on the stress level and past usage, recommend the top 3 interventions.
For each, explain why it's suitable.

Recommendations:"""

            # Generate
            recommendations_text = self.generate_text(prompt, max_length=400)
            
            # Score interventions
            scored = []
            for intervention in available_interventions:
                score = self._score_intervention(
                    intervention,
                    stress_score,
                    intervention_history
                )
                scored.append({
                    **intervention,
                    "relevance_score": score,
                    "reasoning": f"Matched for stress level {stress_score:.0%}"
                })
            
            # Sort and return top 3
            scored.sort(key=lambda x: x["relevance_score"], reverse=True)
            return scored[:3]
            
        except Exception as e:
            logger.error(f"Intervention recommendation failed: {e}")
            return self._fallback_recommendations(stress_score, available_interventions)
    
    def _summarize_history(self, history: Dict[str, Any]) -> str:
        """Summarize intervention history."""
        if not history or not isinstance(history, dict):
            return "No previous interventions"
        
        total = history.get("total_interactions", 0)
        if total == 0:
            return "No previous interventions"
        
        liked = history.get("liked_interventions", [])
        skipped = history.get("skipped_interventions", [])
        completed = history.get("completed_interventions", [])
        
        summary = [
            f"Total interactions: {total}",
            f"Liked interventions: {len(liked)}",
            f"Skipped interventions: {len(skipped)}",
            f"Completed interventions: {len(completed)}"
        ]
        
        return "\n".join(summary)
    
    def _format_interventions(self, interventions: List[Dict[str, Any]]) -> str:
        """Format interventions for prompt."""
        formatted = []
        for i, intervention in enumerate(interventions, 1):
            formatted.append(
                f"{i}. {intervention.get('title', 'Unknown')} "
                f"({intervention.get('duration', 0)}s, "
                f"{intervention.get('category', 'unknown')})"
            )
        return "\n".join(formatted)
    
    def _score_intervention(
        self,
        intervention: Dict[str, Any],
        stress_score: float,
        history: Dict[str, Any]
    ) -> float:
        """Score intervention based on stress and history."""
        score = intervention.get("effectiveness", 0.5)
        
        # Match stress range
        target_range = intervention.get("target_stress_range", {})
        if target_range:
            min_stress = target_range.get("min", 0)
            max_stress = target_range.get("max", 1)
            if min_stress <= stress_score <= max_stress:
                score += 0.2
        
        # Boost if user liked it before
        if isinstance(history, dict):
            audio_id = intervention.get("audio_id")
            if audio_id in history.get("liked_interventions", []):
                score += 0.3
            if audio_id in history.get("completed_interventions", []):
                score += 0.1
            # Penalize if frequently skipped
            skip_count = history.get("skip_counts", {}).get(audio_id, 0)
            if skip_count > 2:
                score -= 0.2
        
        return min(1.0, max(0.0, score))
    
    def _fallback_recommendations(
        self,
        stress_score: float,
        interventions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Fallback recommendations without LLM."""
        scored = []
        for intervention in interventions:
            score = self._score_intervention(intervention, stress_score, {})
            scored.append({
                **intervention,
                "relevance_score": score,
                "reasoning": f"Matched for stress level {stress_score:.0%}"
            })
        
        scored.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored[:3]


# Global instance
gemma4_llm = Gemma4LLM()
