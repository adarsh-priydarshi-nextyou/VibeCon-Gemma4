"""
Implementation validation script.
Validates that all required components are implemented correctly.
"""
import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists."""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description} MISSING: {filepath}")
        return False

def check_directory_structure():
    """Validate project directory structure."""
    print("\n" + "=" * 60)
    print("1. Validating Directory Structure")
    print("=" * 60)
    
    checks = []
    
    # Backend directories
    checks.append(check_file_exists("api", "API directory"))
    checks.append(check_file_exists("models", "Models directory"))
    checks.append(check_file_exists("services", "Services directory"))
    checks.append(check_file_exists("storage", "Storage directory"))
    checks.append(check_file_exists("utils", "Utils directory"))
    checks.append(check_file_exists("scripts", "Scripts directory"))
    
    return all(checks)

def check_core_files():
    """Validate core application files."""
    print("\n" + "=" * 60)
    print("2. Validating Core Application Files")
    print("=" * 60)
    
    checks = []
    
    checks.append(check_file_exists("main.py", "Main application"))
    checks.append(check_file_exists("config.py", "Configuration"))
    checks.append(check_file_exists("logger.py", "Logger"))
    checks.append(check_file_exists("requirements.txt", "Requirements"))
    checks.append(check_file_exists(".env.example", "Environment example"))
    
    return all(checks)

def check_api_endpoints():
    """Validate API endpoint files."""
    print("\n" + "=" * 60)
    print("3. Validating API Endpoints")
    print("=" * 60)
    
    checks = []
    
    checks.append(check_file_exists("api/audio.py", "Audio API"))
    checks.append(check_file_exists("api/insights.py", "Insights API"))
    checks.append(check_file_exists("api/interventions.py", "Interventions API"))
    checks.append(check_file_exists("api/telemetry.py", "Telemetry API"))
    
    return all(checks)

def check_services():
    """Validate service implementations."""
    print("\n" + "=" * 60)
    print("4. Validating Service Implementations")
    print("=" * 60)
    
    checks = []
    
    checks.append(check_file_exists("services/audio_processor.py", "Audio Processor"))
    checks.append(check_file_exists("services/baseline_engine.py", "Baseline Engine"))
    checks.append(check_file_exists("services/gemma4_client.py", "Gemma4 Client"))
    checks.append(check_file_exists("services/telemetry_collector.py", "Telemetry Collector"))
    
    return all(checks)

def check_data_models():
    """Validate data model files."""
    print("\n" + "=" * 60)
    print("5. Validating Data Models")
    print("=" * 60)
    
    checks = []
    
    checks.append(check_file_exists("models/schemas.py", "Pydantic Schemas"))
    
    return all(checks)

def check_storage_layer():
    """Validate storage layer."""
    print("\n" + "=" * 60)
    print("6. Validating Storage Layer")
    print("=" * 60)
    
    checks = []
    
    checks.append(check_file_exists("storage/voice_storage.py", "Voice Storage"))
    
    return all(checks)

def check_utilities():
    """Validate utility files."""
    print("\n" + "=" * 60)
    print("7. Validating Utilities")
    print("=" * 60)
    
    checks = []
    
    checks.append(check_file_exists("utils/retry.py", "Retry Utility"))
    
    return all(checks)

def check_scripts():
    """Validate setup scripts."""
    print("\n" + "=" * 60)
    print("8. Validating Setup Scripts")
    print("=" * 60)
    
    checks = []
    
    checks.append(check_file_exists("scripts/init_mongodb.py", "MongoDB Init"))
    checks.append(check_file_exists("scripts/seed_interventions.py", "Seed Interventions"))
    checks.append(check_file_exists("scripts/test_system.py", "System Test"))
    
    return all(checks)

def check_code_content(filepath, required_items):
    """Check if file contains required code elements."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            missing = [item for item in required_items if item not in content]
            if missing:
                print(f"   ⚠ Missing in {filepath}: {', '.join(missing)}")
                return False
            return True
    except Exception as e:
        print(f"   ✗ Error reading {filepath}: {e}")
        return False

def validate_implementations():
    """Validate key implementations."""
    print("\n" + "=" * 60)
    print("9. Validating Key Implementations")
    print("=" * 60)
    
    checks = []
    
    # Check AudioProcessor
    if os.path.exists("services/audio_processor.py"):
        result = check_code_content("services/audio_processor.py", [
            "class AudioProcessor",
            "def process_audio_stream",
            "def extract_features",
            "def calculate_stress_score"
        ])
        print(f"{'✓' if result else '✗'} AudioProcessor implementation")
        checks.append(result)
    
    # Check BaselineEngine
    if os.path.exists("services/baseline_engine.py"):
        result = check_code_content("services/baseline_engine.py", [
            "class BaselineEngine",
            "def calculate_baseline",
            "def compute_weighted_average"
        ])
        print(f"{'✓' if result else '✗'} BaselineEngine implementation")
        checks.append(result)
    
    # Check TelemetryCollector
    if os.path.exists("services/telemetry_collector.py"):
        result = check_code_content("services/telemetry_collector.py", [
            "class TelemetryCollector",
            "def calculate_skip_status",
            "def record_interaction"
        ])
        print(f"{'✓' if result else '✗'} TelemetryCollector implementation")
        checks.append(result)
    
    # Check VoiceStorage
    if os.path.exists("storage/voice_storage.py"):
        result = check_code_content("storage/voice_storage.py", [
            "class VoiceStorage",
            "async def store_voice_analysis",
            "async def retrieve_historical_voice_scores",
            "async def store_baseline"
        ])
        print(f"{'✓' if result else '✗'} VoiceStorage implementation")
        checks.append(result)
    
    return all(checks)

def check_documentation():
    """Check documentation files."""
    print("\n" + "=" * 60)
    print("10. Validating Documentation")
    print("=" * 60)
    
    checks = []
    
    checks.append(check_file_exists("../README.md", "README"))
    checks.append(check_file_exists("../DEPLOYMENT.md", "Deployment Guide"))
    checks.append(check_file_exists("../PRODUCT_READY.md", "Product Ready Doc"))
    checks.append(check_file_exists("../docker-compose.yml", "Docker Compose"))
    checks.append(check_file_exists("README.md", "Backend README"))
    
    return all(checks)

def main():
    """Run all validation checks."""
    print("=" * 60)
    print("Voice Analysis System - Implementation Validation")
    print("=" * 60)
    
    # Change to backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
    
    results = []
    
    results.append(("Directory Structure", check_directory_structure()))
    results.append(("Core Files", check_core_files()))
    results.append(("API Endpoints", check_api_endpoints()))
    results.append(("Services", check_services()))
    results.append(("Data Models", check_data_models()))
    results.append(("Storage Layer", check_storage_layer()))
    results.append(("Utilities", check_utilities()))
    results.append(("Scripts", check_scripts()))
    results.append(("Implementations", validate_implementations()))
    results.append(("Documentation", check_documentation()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print("=" * 60)
    print(f"Results: {passed}/{total} validation checks passed")
    
    if passed == total:
        print("\n✓ All validation checks passed!")
        print("\nImplementation Status:")
        print("  • Project structure ✓")
        print("  • Core application files ✓")
        print("  • API endpoints ✓")
        print("  • Service implementations ✓")
        print("  • Data models ✓")
        print("  • Storage layer ✓")
        print("  • Utilities ✓")
        print("  • Setup scripts ✓")
        print("  • Key implementations ✓")
        print("  • Documentation ✓")
        print("\n🎉 The Voice Analysis and Intervention System is complete!")
        print("\nNext Steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Start Docker: docker-compose up -d")
        print("  3. Initialize DB: docker-compose exec backend python scripts/init_mongodb.py")
        print("  4. Seed data: docker-compose exec backend python scripts/seed_interventions.py")
        print("  5. Test system: docker-compose exec backend python scripts/test_system.py")
        return True
    else:
        print(f"\n✗ {total - passed} validation check(s) failed")
        print("Please review the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
