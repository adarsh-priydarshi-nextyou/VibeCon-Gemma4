"""
Pydantic schemas for Voice Analysis and Intervention System.
Based on MongoDB data models from design document.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic v2."""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate),
            ])
        ],
        serialization=core_schema.plain_serializer_function_ser_schema(
            lambda x: str(x)
        ))
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")


class SenseVoiceFeatures(BaseModel):
    """SenseVoice acoustic features."""
    pitch: List[float]
    energy: List[float]
    spectral_features: List[float]
    mfcc: List[float]


class AudioFeatures(BaseModel):
    """Combined audio features from SenseVoice and wav2vec2."""
    sensevoice_features: SenseVoiceFeatures
    wav2vec2_embeddings: List[float] = Field(..., min_items=768, max_items=768)


class EmotionalIndicators(BaseModel):
    """Emotional indicators from linguistic analysis."""
    stress: float = Field(..., ge=0.0, le=1.0)
    anxiety: float = Field(..., ge=0.0, le=1.0)
    calmness: float = Field(..., ge=0.0, le=1.0)


class LinguisticSummary(BaseModel):
    """Linguistic summary from Gemma4 analysis."""
    themes: List[str]
    emotions: EmotionalIndicators
    patterns: List[str]


class ModelVersions(BaseModel):
    """Model versions used for analysis."""
    sensevoice: str
    wav2vec2: str
    gemma4: str


class VoiceAnalysisDocument(BaseModel):
    """Voice analysis document stored in MongoDB."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str
    timestamp: datetime
    audio_features: AudioFeatures
    stress_score: float = Field(..., ge=0.0, le=1.0)
    linguistic_summary: LinguisticSummary
    audio_duration_seconds: float
    processing_time_ms: int
    model_versions: ModelVersions
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class DateRange(BaseModel):
    """Date range for baseline calculation."""
    start: datetime
    end: datetime


class BaselineDocument(BaseModel):
    """Baseline metrics document stored in MongoDB."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str
    calculation_date: datetime
    baseline_stress: float = Field(..., ge=0.0, le=1.0)
    baseline_sleep_debt: float = Field(..., ge=0.0)
    baseline_meeting_density: float = Field(..., ge=0.0)
    data_points_used: int
    date_range: DateRange
    previous_baseline_stress: Optional[float] = None
    change_percentage: Optional[float] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ContextualDataDocument(BaseModel):
    """Contextual data document stored in MongoDB."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str
    date: datetime
    sleep_debt_hours: float = Field(..., ge=0.0)
    meeting_count: int = Field(..., ge=0)
    meeting_duration_minutes: float = Field(..., ge=0.0)
    meeting_density: float = Field(..., ge=0.0)
    daily_avg_stress: float = Field(..., ge=0.0, le=1.0)
    daily_max_stress: float = Field(..., ge=0.0, le=1.0)
    daily_min_stress: float = Field(..., ge=0.0, le=1.0)
    voice_sample_count: int = Field(..., ge=0)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class StressRange(BaseModel):
    """Target stress range for interventions."""
    min: float = Field(..., ge=0.0, le=1.0)
    max: float = Field(..., ge=0.0, le=1.0)


class AudioInterventionDocument(BaseModel):
    """Audio intervention document stored in MongoDB."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    audio_id: str
    audio_url: str
    title: str
    description: str
    duration_seconds: float = Field(..., gt=0.0)
    category: str
    subcategory: str
    tags: List[str]
    effectiveness_rating: float = Field(..., ge=0.0, le=1.0)
    usage_count: int = Field(default=0, ge=0)
    average_completion_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    target_stress_range: StressRange
    recommended_for: List[str]
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class DeviceInfo(BaseModel):
    """Device information for telemetry."""
    platform: str
    app_version: str


class InterventionTelemetryDocument(BaseModel):
    """Intervention telemetry document stored in MongoDB."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str
    audio_id: str
    audio_url: str
    timestamp: datetime
    play_duration_seconds: float = Field(..., ge=0.0)
    total_duration_seconds: float = Field(..., gt=0.0)
    completion_percentage: float = Field(..., ge=0.0, le=100.0)
    early_skip: bool
    partial_skip: bool
    completed: bool
    like_status: Optional[bool] = None
    dislike_status: Optional[bool] = None
    feedback_text: Optional[str] = None
    stress_score_at_interaction: float = Field(..., ge=0.0, le=1.0)
    session_id: str
    device_info: DeviceInfo
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Correlations(BaseModel):
    """Correlation metrics for insights."""
    sleep_correlation: float = Field(..., ge=-1.0, le=1.0)
    meeting_correlation: float = Field(..., ge=-1.0, le=1.0)


class Deviations(BaseModel):
    """Deviation metrics from baseline."""
    stress_deviation: float
    sleep_deviation: float
    meeting_deviation: float


class ContextWindow(BaseModel):
    """Context window for insight generation."""
    start_date: datetime
    end_date: datetime
    data_points: int = Field(..., ge=0)


class InsightDocument(BaseModel):
    """Insight document stored in MongoDB."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str
    generation_date: datetime
    stress_pattern: str
    pattern_description: str
    correlations: Correlations
    deviations: Deviations
    contributing_factors: List[str]
    observations: List[str]
    context_window: ContextWindow
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# Request/Response models for API

class VoiceAnalysisResult(BaseModel):
    """Result of voice analysis processing."""
    user_id: str
    stress_score: float = Field(..., ge=0.0, le=1.0)
    linguistic_summary: LinguisticSummary
    audio_duration_seconds: float
    processing_time_ms: int
    timestamp: datetime


class BaselineMetrics(BaseModel):
    """Baseline metrics result."""
    user_id: str
    baseline_stress: float = Field(..., ge=0.0, le=1.0)
    baseline_sleep_debt: float = Field(..., ge=0.0)
    baseline_meeting_density: float = Field(..., ge=0.0)
    calculation_date: datetime
    change_percentage: Optional[float] = None


class Insight(BaseModel):
    """Insight result."""
    stress_pattern: str
    pattern_description: str
    contributing_factors: List[str]
    observations: List[str]
    generation_date: datetime


class InterventionRecommendation(BaseModel):
    """Intervention recommendation result."""
    audio_id: str
    audio_url: str
    title: str
    description: str
    duration_seconds: float
    category: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    reasoning: str


class SkipStatus(BaseModel):
    """Skip status calculation result."""
    early_skip: bool
    partial_skip: bool
    completed: bool
