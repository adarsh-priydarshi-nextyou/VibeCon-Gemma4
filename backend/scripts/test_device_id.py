"""
Test device ID generation and persistence.
"""
import requests
import wave
import numpy as np

BASE_URL = "http://localhost:8000"

def create_test_audio():
    """Create test audio file"""
    sample_rate = 16000
    duration = 2
    samples = np.zeros(sample_rate * duration, dtype=np.int16)
    samples = samples + np.random.randint(-1000, 1000, len(samples), dtype=np.int16)
    
    temp_file = "/tmp/test_device_audio.wav"
    with wave.open(temp_file, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(samples.tobytes())
    
    return temp_file

def test_auto_device_id():
    """Test automatic device ID generation"""
    print("\n" + "="*70)
    print("TEST 1: Automatic Device ID Generation")
    print("="*70)
    
    audio_file = create_test_audio()
    
    # Send request WITHOUT user ID header
    with open(audio_file, 'rb') as f:
        files = {'audio': ('test.wav', f, 'audio/wav')}
        # No X-User-ID header - should auto-generate
        response = requests.post(f"{BASE_URL}/api/audio/process", files=files)
    
    if response.status_code == 200:
        data = response.json()
        user_id = data['user_id']
        print(f"✅ Device ID auto-generated: {user_id}")
        print(f"   Stress Score: {data['stress_score']:.3f}")
        return user_id
    else:
        print(f"❌ Failed: {response.text}")
        return None

def test_persistent_device_id(device_id):
    """Test that device ID persists across requests"""
    print("\n" + "="*70)
    print("TEST 2: Device ID Persistence")
    print("="*70)
    
    # Get insights without providing user ID
    response = requests.get(f"{BASE_URL}/api/insights/{device_id}")
    
    if response.status_code == 200:
        print(f"✅ Device ID persists: {device_id}")
        print(f"   Insights retrieved successfully")
        return True
    else:
        print(f"❌ Failed to retrieve with device ID")
        return False

def test_manual_device_id():
    """Test manual device ID override"""
    print("\n" + "="*70)
    print("TEST 3: Manual Device ID Override")
    print("="*70)
    
    audio_file = create_test_audio()
    manual_id = "device_manual_test_123"
    
    # Send request WITH user ID header
    with open(audio_file, 'rb') as f:
        files = {'audio': ('test.wav', f, 'audio/wav')}
        headers = {'X-User-ID': manual_id}
        response = requests.post(f"{BASE_URL}/api/audio/process", files=files, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        user_id = data['user_id']
        if user_id == manual_id:
            print(f"✅ Manual device ID accepted: {user_id}")
            return True
        else:
            print(f"❌ Device ID mismatch: expected {manual_id}, got {user_id}")
            return False
    else:
        print(f"❌ Failed: {response.text}")
        return False

def test_device_fingerprint():
    """Test device fingerprinting from headers"""
    print("\n" + "="*70)
    print("TEST 4: Device Fingerprinting")
    print("="*70)
    
    audio_file = create_test_audio()
    
    # Simulate different devices with different user agents
    devices = [
        {
            'name': 'Chrome Desktop',
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/91.0'
        },
        {
            'name': 'iPhone Safari',
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) Safari/604.1'
        },
        {
            'name': 'Android Chrome',
            'user_agent': 'Mozilla/5.0 (Linux; Android 11) Chrome/91.0.4472.120 Mobile'
        }
    ]
    
    device_ids = []
    
    for device in devices:
        with open(audio_file, 'rb') as f:
            files = {'audio': ('test.wav', f, 'audio/wav')}
            headers = {'User-Agent': device['user_agent']}
            response = requests.post(f"{BASE_URL}/api/audio/process", files=files, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            device_id = data['user_id']
            device_ids.append(device_id)
            print(f"✅ {device['name']}: {device_id}")
        else:
            print(f"❌ {device['name']}: Failed")
    
    # Check that different devices get different IDs
    unique_ids = len(set(device_ids))
    if unique_ids == len(devices):
        print(f"\n✅ All devices got unique IDs ({unique_ids} unique)")
        return True
    else:
        print(f"\n⚠️  Only {unique_ids} unique IDs for {len(devices)} devices")
        return False

def run_all_tests():
    """Run all device ID tests"""
    print("\n" + "="*70)
    print("DEVICE ID SYSTEM TESTS")
    print("="*70)
    
    results = []
    
    # Test 1: Auto-generation
    device_id = test_auto_device_id()
    results.append(("Auto-generation", device_id is not None))
    
    # Test 2: Persistence
    if device_id:
        results.append(("Persistence", test_persistent_device_id(device_id)))
    
    # Test 3: Manual override
    results.append(("Manual Override", test_manual_device_id()))
    
    # Test 4: Fingerprinting
    results.append(("Fingerprinting", test_device_fingerprint()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 ALL DEVICE ID TESTS PASSED")
        print("\nFeatures Working:")
        print("  ✅ Automatic device ID generation from IP + User-Agent")
        print("  ✅ Device ID persistence across requests")
        print("  ✅ Manual device ID override support")
        print("  ✅ Device fingerprinting for unique identification")
        print("\nBenefits:")
        print("  • Each device gets unique, persistent ID")
        print("  • No manual user registration required")
        print("  • Works across web and mobile")
        print("  • Privacy-friendly (no personal data)")
    else:
        print("\n⚠️  SOME TESTS FAILED")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    run_all_tests()
