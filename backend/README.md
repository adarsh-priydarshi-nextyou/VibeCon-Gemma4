# Voice Analysis and Intervention System - Backend

Backend services for the Voice Analysis and Intervention System, including audio processing, AI-driven analysis, and data persistence.

## Architecture

- **Audio_Processor**: Extracts audio features using SenseVoice and wav2vec2 models
- **Linguistic_Analyzer**: Generates linguistic summaries using Gemma4
- **Insight_Generator**: Creates personalized insights from historical data
- **Intervention_Recommender**: Suggests audio interventions based on user context
- **Baseline_Engine**: Calculates rolling 7-day baseline metrics
- **Telemetry_Collector**: Captures user interaction data
- **Voice_Storage**: MongoDB database for persistent storage

## Setup

### Prerequisites

- Python 3.10+
- MongoDB 6.0+
- CUDA-capable GPU (recommended for model inference)

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Set up MongoDB:
```bash
# Start MongoDB with encryption at rest
mongod --enableEncryption --encryptionKeyFile /path/to/keyfile
```

### Running the Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

API documentation available at `http://localhost:8000/docs`

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration management
├── logger.py               # Structured logging setup
├── requirements.txt        # Python dependencies
├── models/                 # Data models and schemas
├── services/               # Business logic services
│   ├── audio_processor.py
│   ├── linguistic_analyzer.py
│   ├── baseline_engine.py
│   ├── insight_generator.py
│   ├── intervention_recommender.py
│   └── telemetry_collector.py
├── storage/                # Database layer
│   └── voice_storage.py
├── utils/                  # Utility functions
│   ├── retry.py
│   ├── circuit_breaker.py
│   └── security.py
└── tests/                  # Test suite
    ├── unit/
    ├── integration/
    └── property/
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run property-based tests only
pytest -m property_test

# Run specific test file
pytest tests/unit/test_audio_processor.py
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## API Endpoints

### Audio Processing
- `POST /api/audio/process` - Process audio stream and return analysis

### Insights
- `GET /api/insights/{user_id}` - Get personalized insights

### Interventions
- `GET /api/interventions/{user_id}` - Get intervention recommendations
- `POST /api/telemetry` - Record intervention telemetry

### Health
- `GET /health` - Health check endpoint

## Security

- All data processing occurs locally
- TLS encryption for network communication
- MongoDB encryption at rest
- JWT authentication for API endpoints
- User identifier anonymization

## Performance

- Audio processing: < 5 seconds
- Linguistic analysis: < 3 seconds
- Insight generation: < 5 seconds
- Intervention recommendations: < 5 seconds
- Baseline calculation: < 1 second

## License

Proprietary - All rights reserved
