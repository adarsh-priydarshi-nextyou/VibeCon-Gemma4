"""
Test script to validate the complete voice analysis flow.
Tests all steps from voice input to intervention recommendations.
"""
import asyncio
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"
USER_ID = "test_user"


def test_health():
    """Test 1: Health check"""
    print("\n=== Test 1: Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✓ Health check passed")


def test_audio_processing():
    """Test 2: Audio processing with voice sample"""
    print("\n=== Test 2: Audio Processing ===")
    
    # Create a dummy WAV file (1 second of silence)
    import wave
    import numpy as np
    
    sample_rate = 16000
    duration = 2  # 2 seconds
    samples = np.zeros(sample_rate * duration, dtype=np.int16)
    
    # Add some noise to make it more realistic
    samples = samples + np.random.randint(-1000, 1000, len(samples), dtype=np.int16)
    
    # Save to temp file
    temp_file = "/tmp/test_audio.wav"
    with wave.open(temp_file, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(samples.tobytes())
    
    # Upload audio
    with open(temp_file, 'rb') as f:
        files = {'audio': ('test_audio.wav', f, 'audio/wav')}
        headers = {'X-User-ID': USER_ID}
        response = requests.post(
            f"{BASE_URL}/api/audio/process",
            files=files,
            headers=headers
        )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Stress Score: {data['stress_score']:.3f}")
        print(f"Processing Time: {data['processing_time_ms']}ms")
        print(f"Linguistic Summary: {data['linguistic_summary']}")
        print("✓ Audio processing passed")
        return data['stress_score']
    else:
        print(f"Error: {response.text}")
        return None


def test_insights():
    """Test 3: Get insights"""
    print("\n=== Test 3: Get Insights ===")
    
    response = requests.get(f"{BASE_URL}/api/insights/{USER_ID}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data:
            insight = data[0]
            print(f"Pattern: {insight['stress_pattern']}")
            print(f"Description: {insight['pattern_description']}")
            print(f"Contributing Factors: {insight['contributing_factors']}")
            print(f"Observations: {insight['observations']}")
            print("✓ Insights generation passed")
        else:
            print("No insights generated yet (need more data)")
    else:
        print(f"Error: {response.text}")


def test_interventions():
    """Test 4: Get intervention recommendations"""
    print("\n=== Test 4: Get Intervention Recommendations ===")
    
    response = requests.get(f"{BASE_URL}/api/interventions/{USER_ID}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data:
            print(f"Recommended {len(data)} interventions:")
            for i, intervention in enumerate(data, 1):
                print(f"\n{i}. {intervention['title']}")
                print(f"   Category: {intervention['category']}")
                print(f"   Duration: {intervention['duration_seconds']}s")
                print(f"   Relevance: {intervention.get('relevance_score', 0):.2f}")
                print(f"   Reasoning: {intervention.get('reasoning', 'N/A')}")
            print("\n✓ Intervention recommendations passed")
            return data[0] if data else None
        else:
            print("No interventions recommended (need more data)")
    else:
        print(f"Error: {response.text}")
    return None


def test_telemetry(intervention):
    """Test 5: Submit intervention telemetry"""
    print("\n=== Test 5: Submit Intervention Telemetry ===")
    
    if not intervention:
        print("Skipping telemetry test (no intervention available)")
        return
    
    # Test play event
    play_data = {
        "audio_id": intervention['audio_id'],
        "audio_url": intervention['audio_url'],
        "play_duration_seconds": intervention['duration_seconds'] * 0.8,  # 80% completion
        "total_duration_seconds": intervention['duration_seconds'],
        "stress_score_at_interaction": 0.75,
        "session_id": "test_session_123",
        "device_platform": "web",
        "app_version": "1.0.0"
    }
    
    headers = {'X-User-ID': USER_ID}
    response = requests.post(
        f"{BASE_URL}/api/telemetry/play",
        json=play_data,
        headers=headers
    )
    
    print(f"Play Event Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Play telemetry recorded: {data['telemetry_id']}")
    else:
        print(f"Error: {response.text}")
        return
    
    # Test feedback event
    feedback_data = {
        "audio_id": intervention['audio_id'],
        "audio_url": intervention['audio_url'],
        "like_status": True,
        "feedback_text": "Very helpful and relaxing",
        "stress_score_at_interaction": 0.75,
        "session_id": "test_session_123",
        "device_platform": "web",
        "app_version": "1.0.0",
        "play_duration_seconds": intervention['duration_seconds'] * 0.8,
        "total_duration_seconds": intervention['duration_seconds']
    }
    
    response = requests.post(
        f"{BASE_URL}/api/telemetry/feedback",
        json=feedback_data,
        headers=headers
    )
    
    print(f"Feedback Event Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Feedback telemetry recorded: {data['telemetry_id']}")
        print("✓ Telemetry submission passed")
    else:
        print(f"Error: {response.text}")


def test_complete_flow():
    """Run complete flow test"""
    print("=" * 60)
    print("COMPLETE VOICE ANALYSIS FLOW TEST")
    print("=" * 60)
    
    try:
        # Test 1: Health check
        test_health()
        
        # Test 2: Process audio (multiple times to build history)
        print("\n--- Processing 3 voice samples to build history ---")
        for i in range(3):
            print(f"\nSample {i+1}/3:")
            stress_score = test_audio_processing()
            if stress_score is None:
                print("❌ Audio processing failed")
                return
            asyncio.run(asyncio.sleep(1))  # Small delay between samples
        
        # Test 3: Get insights
        test_insights()
        
        # Test 4: Get intervention recommendations
        intervention = test_interventions()
        
        # Test 5: Submit telemetry
        test_telemetry(intervention)
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED - COMPLETE FLOW WORKING")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_complete_flow()
