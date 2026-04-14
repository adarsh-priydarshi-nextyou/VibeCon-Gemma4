"""
Audio processing service for Voice Analysis and Intervention System.
Implements AudioProcessor with SenseVoice and wav2vec2 integration.
"""
import asyncio
import numpy as np
import librosa
import soundfile as sf
from typing import Optional, Dict, Any
from datetime import datetime
from io import BytesIO
from models.schemas import (
    AudioFeatures,
    SenseVoiceFeatures,
    VoiceAnalysisResult,
    VoiceAnalysisDocument,
    LinguisticSummary,
    ModelVersions,
)
from config import settings
from logger import get_logger
import time

logger = get_logger(__name__)


class InvalidAudioError(Exception):
    """Raised when audio data is corrupted or invalid."""
    pass


class ProcessingTimeoutError(Exception):
    """Raised when processing exceeds time limit."""
    pass


class ModelUnavailableError(Exception):
    """Raised when ML models fail to load or are unavailable."""
    pass


class AudioProcessor:
    """
    Audio processing service for voice stress analysis.
    
    Extracts audio features using SenseVoice and wav2vec2 models,
    calculates stress scores, and manages the processing pipeline.
    
    Requirements: 1.2, 1.3, 2.1, 2.2, 2.3, 2.4
    """
    
    def __init__(self):
        """Initialize AudioProcessor with model loading."""
        self.sensevoice_model = None
        self.wav2vec2_model = None
        self.models_loaded = False
        self.target_sample_rate = 16000  # Required by wav2vec2
        
    async def initialize(self):
        """
        Load ML models asynchronously.
        
        Raises:
            ModelUnavailableError: If models fail to load
        """
        try:
            logger.info("Loading audio processing models")
            
            # TODO: Load actual SenseVoice model
            # self.sensevoice_model = load_sensevoice_model()
            
            # TODO: Load actual wav2vec2 model
            # from transformers import Wav2Vec2Model
            # self.wav2vec2_model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base")
            
            # Placeholder: Mark as loaded for now
            self.models_loaded = True
            
            logger.info(
                "Audio processing models loaded",
                sensevoice_version=settings.sensevoice_version,
                wav2vec2_version=settings.wav2vec2_version
            )
            
        except Exception as e:
            logger.error("Failed to load audio processing models", error=str(e))
            raise ModelUnavailableError(f"Failed to load models: {e}")
    
    def validate_audio(self, audio_data: bytes) -> None:
        """
        Validate audio data format and integrity.
        
        Args:
            audio_data: Raw audio bytes
            
        Raises:
            InvalidAudioError: If audio is corrupted or invalid
            
        Requirements: 1.3, 2.4
        """
        if not audio_data or len(audio_data) == 0:
            raise InvalidAudioError("Audio data is empty")
        
        try:
            # Try to load audio to verify format
            audio_buffer = BytesIO(audio_data)
            data, sr = sf.read(audio_buffer)
            
            if len(data) == 0:
                raise InvalidAudioError("Audio contains no samples")
            
            if sr <= 0:
                raise InvalidAudioError(f"Invalid sample rate: {sr}")
            
            logger.debug(
                "Audio validation passed",
                sample_rate=sr,
                duration_seconds=len(data) / sr,
                samples=len(data)
            )
            
        except Exception as e:
            logger.error("Audio validation failed", error=str(e))
            raise InvalidAudioError(f"Invalid audio format: {e}")
    
    def preprocess_audio(self, audio_data: bytes) -> np.ndarray:
        """
        Preprocess audio: normalize and resample to 16kHz.
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Preprocessed audio as numpy array
            
        Requirements: 2.1
        """
        # Load audio
        audio_buffer = BytesIO(audio_data)
        data, sr = sf.read(audio_buffer)
        
        # Convert to mono if stereo
        if len(data.shape) > 1:
            data = np.mean(data, axis=1)
        
        # Resample to target sample rate (16kHz for wav2vec2)
        if sr != self.target_sample_rate:
            data = librosa.resample(
                data,
                orig_sr=sr,
                target_sr=self.target_sample_rate
            )
        
        # Normalize audio to [-1, 1]
        if np.abs(data).max() > 0:
            data = data / np.abs(data).max()
        
        logger.debug(
            "Audio preprocessing complete",
            original_sr=sr,
            target_sr=self.target_sample_rate,
            duration_seconds=len(data) / self.target_sample_rate
        )
        
        return data
    
    def extract_sensevoice_features(self, audio: np.ndarray) -> SenseVoiceFeatures:
        """
        Extract acoustic features using SenseVoice.
        
        Args:
            audio: Preprocessed audio array
            
        Returns:
            SenseVoiceFeatures with pitch, energy, spectral features, MFCC
            
        Requirements: 2.1
        """
        # Extract pitch (fundamental frequency)
        pitches, magnitudes = librosa.piptrack(
            y=audio,
            sr=self.target_sample_rate,
            fmin=50,
            fmax=500
        )
        pitch = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch.append(pitches[index, t])
        
        # Extract energy (RMS)
        energy = librosa.feature.rms(y=audio)[0].tolist()
        
        # Extract spectral features (spectral centroid)
        spectral_features = librosa.feature.spectral_centroid(
            y=audio,
            sr=self.target_sample_rate
        )[0].tolist()
        
        # Extract MFCC (Mel-frequency cepstral coefficients)
        mfcc = librosa.feature.mfcc(
            y=audio,
            sr=self.target_sample_rate,
            n_mfcc=13
        )
        mfcc_mean = np.mean(mfcc, axis=1).tolist()
        
        features = SenseVoiceFeatures(
            pitch=pitch,
            energy=energy,
            spectral_features=spectral_features,
            mfcc=mfcc_mean
        )
        
        logger.debug(
            "SenseVoice features extracted",
            pitch_samples=len(pitch),
            energy_samples=len(energy),
            spectral_samples=len(spectral_features),
            mfcc_coefficients=len(mfcc_mean)
        )
        
        return features
    
    def extract_wav2vec2_embeddings(self, audio: np.ndarray) -> list:
        """
        Extract contextual embeddings using wav2vec2.
        
        Args:
            audio: Preprocessed audio array
            
        Returns:
            768-dimensional embedding vector
            
        Requirements: 2.1
        """
        # TODO: Use actual wav2vec2 model
        # import torch
        # with torch.no_grad():
        #     inputs = self.wav2vec2_model.feature_extractor(
        #         audio,
        #         sampling_rate=self.target_sample_rate,
        #         return_tensors="pt"
        #     )
        #     outputs = self.wav2vec2_model(**inputs)
        #     embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()
        
        # Placeholder: Generate dummy 768-dimensional embedding
        embeddings = np.random.randn(768).tolist()
        
        logger.debug(
            "wav2vec2 embeddings extracted",
            embedding_dim=len(embeddings)
        )
        
        return embeddings
    
    def extract_features(self, audio: np.ndarray) -> AudioFeatures:
        """
        Extract combined audio features from SenseVoice and wav2vec2.
        
        Args:
            audio: Preprocessed audio array
            
        Returns:
            AudioFeatures containing all extracted features
            
        Requirements: 2.1
        """
        start_time = time.time()
        
        # Extract SenseVoice features
        sensevoice_features = self.extract_sensevoice_features(audio)
        
        # Extract wav2vec2 embeddings
        wav2vec2_embeddings = self.extract_wav2vec2_embeddings(audio)
        
        features = AudioFeatures(
            sensevoice_features=sensevoice_features,
            wav2vec2_embeddings=wav2vec2_embeddings
        )
        
        extraction_time = (time.time() - start_time) * 1000
        
        logger.info(
            "Audio features extracted",
            extraction_time_ms=extraction_time
        )
        
        return features
    
    def calculate_stress_score(self, features: AudioFeatures) -> float:
        """
        Calculate stress score from audio features using improved algorithm.
        
        Uses weighted combination of acoustic and contextual features with
        more sophisticated stress indicators.
        Score is normalized to [0.0, 1.0] range.
        
        Args:
            features: Extracted audio features
            
        Returns:
            Stress score in range [0.0, 1.0]
            
        Requirements: 2.2
        """
        # Extract feature statistics
        pitch_values = features.sensevoice_features.pitch
        energy_values = features.sensevoice_features.energy
        spectral_values = features.sensevoice_features.spectral_features
        mfcc_values = features.sensevoice_features.mfcc
        
        # Calculate pitch statistics
        pitch_mean = np.mean(pitch_values) if len(pitch_values) > 0 else 0
        pitch_std = np.std(pitch_values) if len(pitch_values) > 0 else 0
        pitch_range = np.ptp(pitch_values) if len(pitch_values) > 0 else 0  # Peak-to-peak
        
        # Calculate energy statistics
        energy_mean = np.mean(energy_values) if len(energy_values) > 0 else 0
        energy_std = np.std(energy_values) if len(energy_values) > 0 else 0
        energy_max = np.max(energy_values) if len(energy_values) > 0 else 0
        
        # Calculate spectral statistics
        spectral_mean = np.mean(spectral_values) if len(spectral_values) > 0 else 0
        spectral_std = np.std(spectral_values) if len(spectral_values) > 0 else 0
        
        # MFCC statistics (first 3 coefficients are most important)
        mfcc_mean = np.mean(mfcc_values[:3]) if len(mfcc_values) >= 3 else 0
        mfcc_std = np.std(mfcc_values[:3]) if len(mfcc_values) >= 3 else 0
        
        # Embedding statistics
        embedding_mean = np.mean(features.wav2vec2_embeddings)
        embedding_std = np.std(features.wav2vec2_embeddings)
        embedding_max = np.max(np.abs(features.wav2vec2_embeddings))
        
        # Stress indicators with improved normalization
        # 1. Pitch variability (high variance = stress)
        pitch_stress = min(1.0, pitch_std / 50.0)  # Normalize by typical range
        
        # 2. Pitch range (wider range = stress)
        pitch_range_stress = min(1.0, pitch_range / 200.0)
        
        # 3. Energy level (high energy = stress)
        energy_stress = min(1.0, energy_mean * 3.0)
        
        # 4. Energy variability (high variance = stress)
        energy_var_stress = min(1.0, energy_std * 5.0)
        
        # 5. Spectral centroid (higher = brighter/tenser sound)
        spectral_stress = min(1.0, spectral_mean / 3000.0)
        
        # 6. Spectral variability
        spectral_var_stress = min(1.0, spectral_std / 500.0)
        
        # 7. MFCC features (capture timbre changes)
        mfcc_stress = min(1.0, abs(mfcc_mean) * 2.0)
        
        # 8. Embedding features (deep learning representation)
        embedding_stress = min(1.0, abs(embedding_mean) * 1.5)
        embedding_var_stress = min(1.0, embedding_std * 0.8)
        embedding_max_stress = min(1.0, embedding_max * 0.5)
        
        # Weighted combination with improved weights
        stress_components = [
            (pitch_stress, 0.12),           # Pitch variability
            (pitch_range_stress, 0.10),     # Pitch range
            (energy_stress, 0.15),          # Energy level
            (energy_var_stress, 0.12),      # Energy variability
            (spectral_stress, 0.10),        # Spectral centroid
            (spectral_var_stress, 0.08),    # Spectral variability
            (mfcc_stress, 0.10),            # MFCC features
            (embedding_stress, 0.10),       # Embedding mean
            (embedding_var_stress, 0.08),   # Embedding variance
            (embedding_max_stress, 0.05)    # Embedding max
        ]
        
        # Calculate weighted sum
        stress_score = sum(component * weight for component, weight in stress_components)
        
        # Apply sigmoid-like transformation for better distribution
        # This makes the score more sensitive in the middle range
        stress_score = 1 / (1 + np.exp(-10 * (stress_score - 0.5)))
        
        # Clip to [0.0, 1.0] range
        stress_score = max(0.0, min(1.0, stress_score))
        
        logger.debug(
            "Stress score calculated",
            stress_score=stress_score,
            pitch_stress=pitch_stress,
            energy_stress=energy_stress,
            spectral_stress=spectral_stress,
            embedding_stress=embedding_stress
        )
        
        return stress_score
    
    async def process_audio_stream(
        self,
        audio_data: bytes,
        user_id: str
    ) -> VoiceAnalysisResult:
        """
        Process audio stream end-to-end.
        
        Orchestrates validation, preprocessing, feature extraction,
        and stress calculation with timeout enforcement.
        
        Args:
            audio_data: Raw audio bytes
            user_id: User identifier
            
        Returns:
            VoiceAnalysisResult with features and stress score
            
        Raises:
            InvalidAudioError: If audio is invalid
            ProcessingTimeoutError: If processing exceeds 5 seconds
            ModelUnavailableError: If models are not loaded
            
        Requirements: 1.2, 2.1, 2.2, 2.3
        """
        if not self.models_loaded:
            raise ModelUnavailableError("Audio processing models not loaded")
        
        start_time = time.time()
        
        try:
            # Validate audio
            self.validate_audio(audio_data)
            
            # Preprocess audio
            audio = self.preprocess_audio(audio_data)
            audio_duration = len(audio) / self.target_sample_rate
            
            # Check timeout
            if time.time() - start_time > settings.processing_timeout_seconds:
                raise ProcessingTimeoutError("Audio preprocessing exceeded timeout")
            
            # Extract features
            features = self.extract_features(audio)
            
            # Check timeout
            if time.time() - start_time > settings.processing_timeout_seconds:
                raise ProcessingTimeoutError("Feature extraction exceeded timeout")
            
            # Calculate stress score
            stress_score = self.calculate_stress_score(features)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            # Check final timeout
            if processing_time > settings.processing_timeout_seconds * 1000:
                raise ProcessingTimeoutError(
                    f"Total processing time {processing_time}ms exceeded timeout"
                )
            
            # Create result (linguistic summary will be added later)
            result = VoiceAnalysisResult(
                user_id=user_id,
                stress_score=stress_score,
                linguistic_summary=LinguisticSummary(
                    themes=[],
                    emotions={"stress": stress_score, "anxiety": 0.0, "calmness": 0.0},
                    patterns=[]
                ),
                audio_duration_seconds=audio_duration,
                processing_time_ms=processing_time,
                timestamp=datetime.now()
            )
            
            logger.info(
                "Audio processing complete",
                user_id=user_id,
                stress_score=stress_score,
                processing_time_ms=processing_time,
                audio_duration_seconds=audio_duration
            )
            
            return result
            
        except (InvalidAudioError, ProcessingTimeoutError, ModelUnavailableError):
            raise
        except Exception as e:
            logger.error(
                "Audio processing failed",
                user_id=user_id,
                error=str(e)
            )
            raise


# Global processor instance
_processor_instance: Optional[AudioProcessor] = None


async def get_processor() -> AudioProcessor:
    """Get global AudioProcessor instance."""
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = AudioProcessor()
        await _processor_instance.initialize()
    return _processor_instance
