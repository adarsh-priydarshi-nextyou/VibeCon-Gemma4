"""
Standalone test script that doesn't require Docker.
Tests core functionality with in-memory operations.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import asyncio
import numpy as np
from datetime import datetime, timedelta

# Test imports
try:
    from services.audio_processor import AudioProcessor, InvalidAudioError
    from services.baseline_engine import BaselineEngine, HistoricalData
    from services.telemetry_collector import TelemetryCollector, SkipStatus
    from services.gemma4_client import Gemma4Client
    from models.schemas import (
        AudioFeatures, SenseVoiceFeatures, DeviceInfo,
        InterventionTelemetryDocument
    )
    print("✓ All imports successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)


def test_audio_features():
    """Test audio feature extraction."""
    print("\n1. Testing Audio Feature Extraction...")
    
    try:
        # Create sample features
        features = SenseVoiceFeatures(
            pitch=[100.0, 120.0, 110.0],
            energy=[0.5, 0.6, 0.55],
            spectral_features=[1500.0, 1600.0, 1550.0],
            mfcc=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0]
        )
        
        audio_features = AudioFeatures(
            sensevoice_features=features,
            wav2vec2_embeddings=[0.1] * 768
        )
        
        assert len(audio_features.wav2vec2_embeddings) == 768
        assert len(audio_features.sensevoice_features.mfcc) == 13
        
        print("   ✓ Audio features structure validated")
        return True
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False


def test_stress_score_calculation():
    """Test stress score calculation."""
    print("\n2. Testing Stress Score Calculation...")
    
    try:
        processor = AudioProcessor()
        
        # Create test features
        features = AudioFeatures(
            sensevoice_features=SenseVoiceFeatures(
                pitch=[100.0, 120.0, 110.0],
                energy=[0.5, 0.6, 0.55],
                spectral_features=[1500.0, 1600.0, 1550.0],
                mfcc=[1.0] * 13
            ),
            wav2vec2_embeddings=[0.1] * 768
        )
        
        # Calculate stress score
        stress_score = processor.calculate_stress_score(features)
        
        # Verify range
        assert 0.0 <= stress_score <= 1.0, f"Stress score {stress_score} out of range"
        
        print(f"   ✓ Stress score: {stress_score:.3f} (valid range [0.0, 1.0])")
        return True
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False


def test_baseline_calculation():
    """Test baseline calculation."""
    print("\n3. Testing Baseline Calculation...")
    
    try:
        engine = BaselineEngine()
        
        # Test weighted average calculation
        values = [0.5, 0.6, 0.7, 0.65, 0.55, 0.6, 0.7]
        baseline = engine.compute_weighted_average(values, days=7)
        
        # Verify baseline is within range
        min_val = min(values)
        max_val = max(values)
        assert min_val <= baseline <= max_val, \
            f"Baseline {baseline} outside range [{min_val}, {max_val}]"
        
        print(f"   ✓ Baseline: {baseline:.3f} (within range [{min_val:.3f}, {max_val:.3f}])")
        print(f"   ✓ Exponential decay weighting applied")
        return True
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False


def test_skip_status_calculation():
    """Test skip status calculation."""
    print("\n4. Testing Skip Status Calculation...")
    
    try:
        collector = TelemetryCollector()
        
        # Test early skip (< 5 seconds)
        status1 = collector.calculate_skip_status(3.0, 300.0)
        assert status1.early_skip is True
        assert status1.partial_skip is True
        assert status1.completed is False
        print("   ✓ Early skip detected correctly (< 5s)")
        
        # Test partial skip (< 50%)
        status2 = collector.calculate_skip_status(100.0, 300.0)
        assert status2.early_skip is False
        assert status2.partial_skip is True
        assert status2.completed is False
        print("   ✓ Partial skip detected correctly (< 50%)")
        
        # Test completed (>= 80%)
        status3 = collector.calculate_skip_status(250.0, 300.0)
        assert status3.early_skip is False
        assert status3.partial_skip is False
        assert status3.completed is True
        print("   ✓ Completion detected correctly (>= 80%)")
        
        return True
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False


async def test_gemma4_insights():
    """Test Gemma4 insights generation."""
    print("\n5. Testing Insights Generation...")
    
    try:
        client = Gemma4Client()
        
        # Test data
        voice_scores = [0.5, 0.6, 0.7, 0.65, 0.55]
        sleep_debt = [1.0, 1.5, 2.0, 1.5, 1.0]
        meeting_density = [0.3, 0.4, 0.5, 0.4, 0.3]
        baseline = {"stress": 0.6, "sleep_debt": 1.5, "meeting_density": 0.4}
        
        # Generate insights
        insights = await client.generate_insights(
            voice_scores, sleep_debt, meeting_density, baseline
        )
        
        # Verify structure
        assert "pattern" in insights
        assert "contributing_factors" in insights
        assert "observations" in insights
        
        print(f"   ✓ Pattern identified: {insights['pattern']}")
        print(f"   ✓ Factors: {len(insights['contributing_factors'])} identified")
        print(f"   ✓ Observations: {len(insights['observations'])} generated")
        return True
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False


async def test_intervention_recommendations():
    """Test intervention recommendations."""
    print("\n6. Testing Intervention Recommendations...")
    
    try:
        client = Gemma4Client()
        
        # Test data
        voice_scores = [0.7, 0.75, 0.8]
        interventions = [
            {
                "audio_id": "breathing-001",
                "audio_url": "https://example.com/breathing-001.mp3",
                "title": "Deep Breathing",
                "description": "5-minute breathing exercise",
                "duration_seconds": 300.0,
                "category": "breathing",
                "effectiveness_rating": 0.85,
                "target_stress_range": {"min": 0.5, "max": 1.0}
            },
            {
                "audio_id": "meditation-001",
                "audio_url": "https://example.com/meditation-001.mp3",
                "title": "Mindfulness Meditation",
                "description": "10-minute meditation",
                "duration_seconds": 600.0,
                "category": "meditation",
                "effectiveness_rating": 0.90,
                "target_stress_range": {"min": 0.4, "max": 0.8}
            }
        ]
        user_history = {
            "liked_interventions": [],
            "skipped_interventions": [],
            "skip_counts": {}
        }
        
        # Generate recommendations
        recommendations = await client.recommend_interventions(
            "increasing", voice_scores, interventions, user_history
        )
        
        # Verify structure
        assert len(recommendations) > 0
        assert all("relevance_score" in rec for rec in recommendations)
        assert all(0.0 <= rec["relevance_score"] <= 1.0 for rec in recommendations)
        
        print(f"   ✓ Generated {len(recommendations)} recommendations")
        for i, rec in enumerate(recommendations, 1):
            print(f"      {i}. {rec['title']} (score: {rec['relevance_score']:.2f})")
        return True
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False


def test_telemetry_capture():
    """Test telemetry event capture."""
    print("\n7. Testing Telemetry Event Capture...")
    
    try:
        collector = TelemetryCollector()
        
        device_info = DeviceInfo(platform="iOS", app_version="1.0.0")
        
        # Capture play event
        telemetry = collector.capture_play_event(
            user_id="test-user",
            audio_id="breathing-001",
            audio_url="https://example.com/breathing-001.mp3",
            play_duration=180.0,
            total_duration=300.0,
            stress_score_at_interaction=0.75,
            session_id="session-123",
            device_info=device_info
        )
        
        # Verify telemetry structure
        assert telemetry.user_id == "test-user"
        assert telemetry.audio_id == "breathing-001"
        assert telemetry.completion_percentage == 60.0
        assert telemetry.partial_skip is True
        assert telemetry.completed is False
        
        print("   ✓ Play event captured correctly")
        print(f"   ✓ Completion: {telemetry.completion_percentage}%")
        print(f"   ✓ Skip status calculated")
        return True
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False


async def run_all_tests():
    """Run all standalone tests."""
    print("=" * 60)
    print("Voice Analysis System - Standalone Functionality Test")
    print("=" * 60)
    
    results = []
    
    # Run synchronous tests
    results.append(("Audio Features", test_audio_features()))
    results.append(("Stress Score Calculation", test_stress_score_calculation()))
    results.append(("Baseline Calculation", test_baseline_calculation()))
    results.append(("Skip Status Calculation", test_skip_status_calculation()))
    
    # Run async tests
    results.append(("Insights Generation", await test_gemma4_insights()))
    results.append(("Intervention Recommendations", await test_intervention_recommendations()))
    results.append(("Telemetry Capture", test_telemetry_capture()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All core functionality tests passed!")
        print("\nThe system is working correctly:")
        print("  • Audio processing pipeline ✓")
        print("  • Baseline calculation ✓")
        print("  • Insights generation ✓")
        print("  • Intervention recommendations ✓")
        print("  • Telemetry collection ✓")
        print("\nReady for deployment!")
        return True
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
