# PULSE — Member 5: Features Engineer Module

> Medicine Scanner · Emergency First Aid Guide · Email Emergency Alert

## 🔬 Overview

This module implements three core PULSE features:

1. **Medicine Scanner** — Photo → OpenCV preprocessing → Tesseract OCR → Gemini Vision AI → OpenFDA lookup → Drug interaction check
2. **Emergency First Aid Guide** — Voice transcription → Protocol matching (keyword + AI) → Step-by-step instructions with TTS
3. **Email Emergency Alert** — GPS coordinates → HTML email with Google Maps link (via Gmail SMTP)

## 📦 Project Structure

```
m5_features/
├── __init__.py              # Package init
├── config.py                # Environment configuration
├── main.py                  # FastAPI app entry point
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
│
├── ai/                      # AI client wrappers
│   ├── __init__.py
│   └── gemini_client.py     # Google Gemini Vision + Text client
│
├── scanner/                 # Medicine scanning pipeline
│   ├── __init__.py
│   ├── image_preprocessor.py    # OpenCV image processing
│   ├── ocr_extractor.py         # Tesseract OCR text extraction
│   ├── openfda_service.py       # FDA drug database lookup
│   ├── drug_interaction_checker.py  # Drug-drug interaction check
│   └── medicine_scanner.py      # Pipeline orchestrator
│
├── emergency/               # Emergency guide system
│   ├── __init__.py
│   ├── protocol_matcher.py  # Voice → protocol matching
│   └── email_alert.py      # Email GPS alert service (Gmail SMTP)
│
├── models/                  # Pydantic v2 schemas
│   ├── __init__.py
│   ├── scanner_models.py    # Medicine scanner API models
│   └── emergency_models.py  # Emergency guide API models
│
├── routes/                  # FastAPI endpoints
│   ├── __init__.py
│   ├── medicine_routes.py   # POST /api/medicine/scan
│   └── emergency_routes.py  # POST /api/emergency/identify, /alert
│
├── protocols/               # 15 emergency protocol JSONs
│   ├── cpr_adult.json
│   ├── cpr_child.json
│   ├── choking_adult.json
│   ├── choking_child.json
│   ├── stroke.json
│   ├── severe_bleeding.json
│   ├── burns.json
│   ├── allergic_reaction.json
│   ├── drowning.json
│   ├── seizure.json
│   ├── diabetic_emergency.json
│   ├── heart_attack.json
│   ├── poisoning.json
│   ├── fracture.json
│   └── electric_shock.json
│
└── tests/                   # Unit tests
    ├── __init__.py
    ├── test_scanner.py      # Scanner pipeline tests
    ├── test_emergency.py    # Emergency guide tests
    └── test_email_alert.py  # Email alert tests
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd m5_features
pip install -r requirements.txt
```

### 2. System Requirements

- **Tesseract OCR** must be installed as a system binary:
  - Windows: `winget install UB-Mannheim.TesseractOCR`
  - Mac: `brew install tesseract`
  - Linux: `sudo apt install tesseract-ocr`

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your values:
# - GEMINI_API_KEY (from aistudio.google.com)
# - ALERT_EMAIL (your Gmail address)
# - ALERT_EMAIL_PASSWORD (Gmail App Password — see .env.example)
```

### 4. Run the Server

```bash
cd m5_features
uvicorn main:app --reload --port 8000
```

### 5. Run Tests

```bash
python -m pytest tests/ -v
```

## 📡 API Endpoints

### Medicine Scanner

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/medicine/scan` | Scan a medicine image |
| `GET` | `/api/medicine/health` | Scanner health check |

### Emergency Guide

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/emergency/identify` | Match text to protocol |
| `POST` | `/api/emergency/alert` | Send Email GPS alert |
| `GET` | `/api/emergency/protocols` | List all 15 protocols |
| `GET` | `/api/emergency/protocols/{id}` | Get specific protocol |
| `GET` | `/api/emergency/health` | Emergency service health |

## 🧪 Technology Stack

| Component | Technology |
|-----------|------------|
| AI Engine | Google Gemini 1.5 Flash (Vision + Text) |
| OCR | Tesseract OCR + OpenCV preprocessing |
| Drug Data | OpenFDA API (free, no key) |
| Alerts | Gmail SMTP (free, built-in Python) |
| Framework | FastAPI + Pydantic v2 |
| HTTP Client | httpx (async) |

## 👤 Author

**Zajnan Aslam** — Member 5, Features Engineer  
PULSE · BWAI Hackathon 2026 · DHA Suffa University
