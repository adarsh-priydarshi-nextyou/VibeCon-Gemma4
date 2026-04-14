"""
Configuration management for Voice Analysis and Intervention System.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # MongoDB Configuration
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "voice_analysis"
    mongodb_encryption_key_file: Optional[str] = None
    
    # Audio Processor Configuration
    audio_processor_host: str = "0.0.0.0"
    audio_processor_port: int = 8000
    audio_processor_max_concurrent_users: int = 10
    
    # MCP Server Configuration
    mcp_server_url: str = "http://localhost:8001"
    gemma4_model_path: Optional[str] = None
    enable_llm: bool = False  # Set to True to enable real LLM (slow on CPU, use False for fast statistical mode)
    
    # Security Configuration
    jwt_secret_key: str = "change-this-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 1
    anonymization_salt: str = "change-this-salt"
    
    # TLS Configuration
    tls_cert_file: Optional[str] = None
    tls_key_file: Optional[str] = None
    tls_ca_file: Optional[str] = None
    
    # Performance Configuration
    processing_timeout_seconds: int = 30
    linguistic_timeout_seconds: int = 10
    insight_timeout_seconds: int = 10
    intervention_timeout_seconds: int = 5
    baseline_timeout_seconds: int = 1
    telemetry_timeout_seconds: int = 1
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Model Versions
    sensevoice_version: str = "1.0.0"
    wav2vec2_version: str = "1.0.0"
    gemma4_version: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
