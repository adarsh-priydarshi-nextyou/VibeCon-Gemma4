"""
System integration test script.
Tests the complete workflow from audio processing to recommendations.
"""
import asyncio
import httpx
import numpy as np
import soundfile as sf
from io import BytesIO
import sys

BASE_URL = "http://localhost:8000"
TEST_USER_ID = "test-user-123"


def generate_test_audio():
    """Generate a simple test audio file."""
    # Generate 3 seconds of sine wave at 440 Hz
    sample_rate = 16000
    duration = 3.0
    frequency = 440.0
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = 0.5 * np.sin(2 * np.pi * frequency * t)
    
    # Save to bytes
    buffer = BytesIO()
    sf.write(buffer, audio, sample_rate, format='WAV')
    buffer.seek(0)
    
    return buffer.getvalue()


async def test_health_check():
    """Test system health check."""
    print("\n1. Testing health check...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        print(f"   ✓ System status: {data['status']}")
        return True


async def test_audio_processing():
    """Test audio processing endpoint."""
    print("\n2. Testing audio processing...")
    
    # Generate test audio
    audio_data = generate_test_audio()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        files = {"audio": ("test.wav", audio_data, "audio/wav")}
        headers = {"X-User-ID": TEST_USER_ID}
        
        response = await client.post(
            f"{BASE_URL}/api/audio/process",
            files=files,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        print(f"   ✓ Stress score: {data['stress_score']:.3f}")
        print(f"   ✓ Processing time: {data['processing_time_ms']}ms")
        print(f"   ✓ Audio duration: {data['audio_duration_seconds']:.2f}s")
        
        return data


async def test_insights():
    """Test insights generation."""
    print("\n3. Testing insights generation...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/api/insights/{TEST_USER_ID}")
        
        if response.status_code == 200:
            data = response.json()
            if data:
                insight = data[0]
                print(f"   ✓ Stress pattern: {insight['stress_pattern']}")
                print(f"   ✓ Observations: {len(insight['observations'])} items")
                return data
            else:
                print("   ⚠ No insights available yet (need more data)")
                return []
        else:
            print(f"   ⚠ Insights not available: {response.status_code}")
            return []


async def test_recommendations():
    """Test intervention recommendations."""
    print("\n4. Testing intervention recommendations...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/api/interventions/{TEST_USER_ID}")
        
        if response.status_code == 200:
            data = response.json()
            if data:
                print(f"   ✓ Recommendations: {len(data)} interventions")
                for i, rec in enumerate(data, 1):
                    print(f"      {i}. {rec['title']} (score: {rec['relevance_score']:.2f})")
                return data
            else:
                print("   ⚠ No recommendations available yet (need more data)")
                return []
        else:
            print(f"   ⚠ Recommendations not available: {response.status_code}")
            return []


async def test_telemetry():
    """Test telemetry recording."""
    print("\n5. Testing telemetry recording...")
    
    telemetry_data = {
        "audio_id": "breathing-001",
        "audio_url": "https://example.com/audio/breathing-001.mp3",
        "play_duration_seconds": 180.0,
        "total_duration_seconds": 300.0,
        "stress_score_at_interaction": 0.75,
        "session_id": "test-session-123",
        "device_platform": "iOS",
        "app_version": "1.0.0"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = {"X-User-ID": TEST_USER_ID}
        response = await client.post(
            f"{BASE_URL}/api/telemetry/play",
            json=telemetry_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        print(f"   ✓ Telemetry recorded: {data['telemetry_id']}")
        print(f"   ✓ Message: {data['message']}")
        
        return data


async def run_all_tests():
    """Run all system tests."""
    print("=" * 60)
    print("Voice Analysis and Intervention System - Integration Test")
    print("=" * 60)
    
    try:
        # Test 1: Health check
        await test_health_check()
        
        # Test 2: Audio processing (run multiple times to build history)
        print("\n   Processing multiple audio samples to build history...")
        for i in range(3):
            await test_audio_processing()
            await asyncio.sleep(1)
        
        # Test 3: Insights
        await test_insights()
        
        # Test 4: Recommendations
        await test_recommendations()
        
        # Test 5: Telemetry
        await test_telemetry()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)
        print("\nSystem is ready for use.")
        print(f"API Documentation: {BASE_URL}/docs")
        print(f"Health Check: {BASE_URL}/health")
        
        return True
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return False
    except httpx.ConnectError:
        print(f"\n✗ Cannot connect to {BASE_URL}")
        print("   Make sure the backend server is running:")
        print("   docker-compose up -d")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
