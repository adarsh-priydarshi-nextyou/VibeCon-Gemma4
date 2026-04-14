# VibeCon-Gemma4

**AI-Powered Voice Stress Analysis & Intervention System**

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18.2.0-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.104.1-green.svg)](https://fastapi.tiangolo.com/)

---

## 🎯 Overview

Real-time voice stress detection system using ML to analyze voice patterns, generate AI insights, and recommend personalized audio interventions.

**Key Features:**
- 🎤 Real-time voice analysis (10 audio components)
- 🤖 Gemma4 LLM for insights (TinyLlama 1.1B)
- 🎯 Personalized intervention recommendations
- 🔒 Privacy-first (device-based IDs, no registration)
- 📱 Multi-platform (Web + Mobile)

---

## 🚀 Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
python scripts/seed_interventions.py
python scripts/seed_contextual_data.py
python main.py  # http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev  # http://localhost:3000
```

### Mobile
```bash
cd mobile
npm install
npm run android
# Build APK: ./build-apk.sh
```

---

## 📊 System Flow

```
Voice Input → Audio Processing (10 features) → Stress Score (0-1) 
→ Gemma4 Summary → MongoDB Storage → Historical Analysis (7 days) 
→ Baseline Calculation → Insights (3-day context) 
→ Top 3 Interventions → User Feedback → Telemetry Loop
```

---

## 🏗️ Architecture

```
Web/Mobile App → FastAPI (Port 8000) → Audio Processor + Gemma4 LLM → MongoDB (6 Collections)
```

**Complete Documentation:** [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)

---

## 🔧 Configuration

**Fast Mode (Recommended):**
```python
# backend/config.py
enable_llm = False  # Statistical mode, <10ms
```

**AI Mode:**
```python
enable_llm = True  # Gemma4 LLM, 3-10s (slower)
```

---

## 📁 Structure

```
VibeCon-Gemma4/
├── backend/          # FastAPI + ML services
├── frontend/         # React web app
├── mobile/           # React Native app
└── SYSTEM_ARCHITECTURE.md  # Complete docs
```

---

## 🧪 Testing

```bash
cd backend
python scripts/final_verification.py
```

Expected: ✅ All 10 steps verified

---

## 📈 Performance

| Operation | Time |
|-----------|------|
| Audio Processing | 10-50ms |
| Statistical Mode | <10ms |
| LLM Mode | 3-10s |

---

## 🗄️ Database

**MongoDB Collections:**
1. voice_analysis - Features & scores
2. insights - AI-generated patterns
3. baselines - 7-day rolling averages
4. interventions - Audio library
5. intervention_telemetry - User feedback
6. contextual_data - Sleep & meetings

---

## 🔌 API Endpoints

- `POST /api/audio/process` - Process voice
- `GET /api/insights/{user_id}` - Get insights
- `GET /api/interventions/{user_id}` - Get recommendations
- `POST /api/telemetry/play` - Record interaction
- `POST /api/telemetry/feedback` - Record feedback

---

## 🤖 ML Models

**Audio:** librosa 0.10.1 (10 components)  
**LLM:** TinyLlama 1.1B (2.2GB, optional)

---

## 📱 Mobile APK

```bash
cd mobile
./build-apk.sh
# Output: mobile/android/app/build/outputs/apk/release/app-release.apk
```

---

## 🐳 Docker

```bash
docker-compose up -d
```

---

## 📝 Documentation

**[SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)** - Complete system documentation with:
- Detailed architecture diagrams
- Data flow sequences
- Service descriptions
- Database schemas
- API specifications
- Codebase structure

---

## 🎯 Status

✅ Backend - Fully operational  
✅ Frontend - Complete UI  
✅ Mobile - APK available  
✅ Database - 6 collections  
✅ ML Models - Audio + LLM  
✅ Testing - All verified  

---

## 📧 Contact

Open an issue on GitHub for support.

---

**Repository:** https://github.com/adarsh-priydarshi-nextyou/VibeCon-Gemma4

---

*Built for voice stress analysis and mental wellness*
