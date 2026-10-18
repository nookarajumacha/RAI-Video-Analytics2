# 🛡️ Wearable AI Security Assistant

> **Production-Quality MVP: AI-Powered Wearable Visual Threat Detection & Situational Awareness for Patrol Officers**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-teal.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.3+-61DAFB.svg)](https://react.dev/)
[![Ultralytics YOLO](https://img.shields.io/badge/YOLO-v8%20%2F%20v11-orange.svg)](https://docs.ultralytics.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Local%20Audit-lightgrey.svg)](https://sqlite.org/)

---

## 1. 🎯 Project Purpose

The **Wearable AI Security Assistant** is a real-time computer vision and situational awareness system designed for authorized security personnel, campus safety teams, and patrol officers. 

By analyzing live video captured from an officer's body camera or wearable glasses, the system identifies **visually identifiable threats (specifically Firearms and Knives)** in real time and alerts the officer via discreet heads-up audio and visual signals.

### ⚠️ Strict Ethical & Operational Boundaries
- **No Autonomous Policing:** The AI provides alerts solely as a **"Potential Threat"** advisory. Human verification is always required before action.
- **Zero Facial Recognition:** Biometric scanning or individual identity matching is permanently excluded by design.
- **No Concealed Weapon Claims:** Optical cameras can only identify exposed, visible objects. We make zero claims regarding concealed x-ray detection.
- **No Drug Detection Claims:** Optical video cannot determine whether a pouch or container contains chemical substances.
- **Privacy-First Local Processing:** Inference runs on the local edge/device. No persistent bulk video footage is streamed to third-party clouds.

---

## 2. 🏛️ System Architecture

```
                      +-----------------------------+
                      |       PHYSICAL WORLD        |
                      +-----------------------------+
                                     |
                                     v
                      +-----------------------------+
                      |   Camera / Wearable Lens    |
                      +-----------------------------+
                                     |
                             [Raw Video Frames]
                                     |
                                     v
                      +-----------------------------+
                      |   OpenCV Video Capture      |
                      |  - 2K QHD (2560x1440) 60 FPS|
                      |  - DirectShow MJPG Hardware |
                      |  - Decoupled frame queue    |
                      +-----------------------------+
                                     |
                                     v
                      +-----------------------------+
                      |     Frame Preprocessing     |
                      |  - 640x640 Letterboxing     |
                      +-----------------------------+
                                     |
                                     v
                      +-----------------------------+
                      |     YOLO Threat Model       |
                      |  - Single-stage regression  |
                      |  - Clean BaseDetector API   |
                      +-----------------------------+
                                     |
                                     v
                      +-----------------------------+
                      |    Confidence Filtering     |
                      |  - Gate: Configurable %     |
                      |  - Area / Noise Filter      |
                      +-----------------------------+
                                     |
                                     v
                      +-----------------------------+
                      |    Threat Classification    |
                      |  - Firearm / Knife Mapping  |
                      +-----------------------------+
                                     |
                                     v
                      +-----------------------------+
                      |        Alert Engine         |
                      |  - 3s Anti-Spam Cooldown    |
                      |  - Audio Voice Synthesizer  |
                      |  - Local SQLite Event Log   |
                      +-----------------------------+
                                     |
                     +---------------+---------------+
                     |                               |
                     v                               v
       +----------------------------+  +----------------------------+
       |   WebSocket Event Stream   |  |   Live MJPEG Video Feed    |
       |  (ws://127.0.0.1:8000/ws)  |  |  (/api/camera/stream)      |
       +----------------------------+  +----------------------------+
                     \                               /
                      \                             /
                       v                           v
              +-----------------------------------------------+
              |            React Officer Dashboard            |
              |     - Live Camera Feed with Tactical HUD      |
              |     - Threat Assessment Status Badge          |
              |     - Start / Stop Camera Controls            |
              |     - Confidence Threshold Slider             |
              |     - Local Detection History & Verification  |
              +-----------------------------------------------+
```

---

## 3. 📁 Complete Project Structure

```
idea 1/
│
├── backend/
│   ├── main.py                # FastAPI entry point, CORS, WebSockets & lifespan
│   │
│   ├── api/
│   │   ├── camera.py          # Camera Start/Stop controls & MJPEG streaming route
│   │   ├── detection.py       # Detection status & static frame upload test
│   │   ├── alerts.py          # Alert toggle, threshold updates & test trigger
│   │   └── history.py         # Local SQLite audit log & human verification updates
│   │
│   ├── detection/
│   │   ├── detector.py        # BaseDetector interface, YOLO ThreatDetector, mock fallback
│   │   ├── preprocessing.py   # Letterbox resizing and aspect-ratio normalization
│   │   └── postprocessing.py  # Confidence filtering, size thresholds & threat tagging
│   │
│   ├── alerts/
│   │   ├── audio_alert.py     # Thread-safe text-to-speech & acoustic tone warnings
│   │   └── alert_manager.py   # Cooldown debouncing, SQLite logging & WebSocket dispatch
│   │
│   ├── database/
│   │   ├── database.py        # SQLAlchemy engine & session manager
│   │   └── models.py          # DetectionEvent schema (ID, Object, Conf, Status, Verification)
│   │
│   ├── hardware/
│   │   └── camera.py          # 60 FPS DirectShow threaded camera reader
│   │
│   ├── config/
│   │   └── settings.py        # Pydantic v2 BaseSettings configuration
│   │
│   ├── tests/
│   │   └── test_backend.py    # Comprehensive test suite (9 passing tests)
│   │
│   └── requirements.txt       # Backend dependencies
│
├── frontend/
│   ├── package.json           # React 18, Vite dependencies
│   ├── vite.config.js         # Dev server with proxy to backend :8000
│   ├── index.html             # Tactical dark HUD container
│   │
│   └── src/
│       ├── main.jsx           # React DOM root
│       ├── App.jsx            # Top-level view container
│       ├── index.css          # Tactical glassmorphism design system
│       │
│       ├── components/
│       │   ├── CameraFeed.jsx        # Live MJPEG stream with HUD badges
│       │   ├── DetectionOverlay.jsx  # Current threat status & action required
│       │   ├── AlertPanel.jsx        # Alert channel settings & test trigger
│       │   ├── DetectionHistory.jsx  # SQLite event audit table with verification actions
│       │   └── SystemStatus.jsx      # Telemetry, camera toggle & confidence slider
│       │
│       ├── pages/
│       │   └── Dashboard.jsx         # Main Officer Control Center
│       │
│       └── services/
│           └── websocket.js          # Auto-reconnecting WebSocket client
│
├── models/
│   ├── pretrained/            # Base YOLO checkpoints (yolov8n.pt)
│   └── trained/               # Specialized weapon weights (weapon_threat_yolov8.pt)
│
├── docs/
│   ├── COMPETITOR_RESEARCH.md # ZeroEyes, Vaidio, Axon comparison & USP analysis
│   ├── ETHICS_AND_PRIVACY.md  # Explicit boundaries (No facial recognition, human verification)
│   ├── ROADMAP.md             # The 10-phase development plan & milestone checklists
│   └── ARCHITECTURE.md        # Technical dataflow and pipeline diagrams
│
├── security_assistant.db      # Local SQLite database
├── requirements.txt           # Workspace requirements
└── README.md                  # Master documentation
```

---

## 4. ⚙️ Installation & Setup

### Prerequisites
- Python 3.10+ (Tested on Python 3.11)
- Node.js 18+ and npm

### Step 1: Python Environment Setup
```powershell
# In the workspace root:
python -m venv venv
.\venv\Scripts\activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

### Step 2: Frontend Setup
```powershell
# Navigate to frontend and install npm packages:
cd frontend
npm install
cd ..
```

---

## 5. 🚀 How to Run the Application

### Option A: Run Backend & Frontend Concurrently

**Terminal 1 (Backend - FastAPI Server):**
```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- API is live at: `http://127.0.0.1:8000`
- Interactive Swagger docs at: `http://127.0.0.1:8000/docs`

**Terminal 2 (Frontend - React Dashboard):**
```powershell
cd frontend
npm run dev
```
- Open browser at: **`http://127.0.0.1:5173`**

---

## 6. 📷 How to Connect a Webcam / Camera

By default, the backend connects to laptop webcam index `0`.

To change the camera source (e.g. to an external USB camera or RTSP security camera stream):
- **Environment Variable:** Set `CAMERA_SOURCE=1` or `CAMERA_SOURCE=rtsp://user:pass@ip:port/stream`
- **Or in `.env`:**
  ```ini
  CAMERA_SOURCE=1
  ```
- In the React Dashboard, click **"▶ Start Camera"** to initialize the capture stream.

---

## 7. 🧠 Where to Place / Load Trained YOLO Models

The detector uses a clean pluggable interface defined in [`backend/detection/detector.py`](file:///c:/Users/Raju/Downloads/idea%201/backend/detection/detector.py).

To load a custom-trained model:
1. Place your exported PyTorch weights (`best.pt`) into:
   ```
   models/trained/weapon_threat_yolov8.pt
   ```
2. Or specify a custom path in your `.env` file:
   ```ini
   MODEL_PATH=models/trained/your_custom_model.pt
   ```
3. If no custom weights file is found, the system automatically falls back to `yolov8n.pt` or the built-in mock detector, ensuring zero crashes.

---

## 8. 🧪 Testing the Application

### Running Backend Unit & Integration Tests:
```powershell
pytest backend/tests/test_backend.py -v
```

**Test Coverage:**
- `test_model_loading_interface`: Verifies clean BaseDetector inheritance and mock fallbacks.
- `test_preprocessing`: Verifies letterbox sizing and scale factors.
- `test_threat_detection_service_with_mock`: Verifies latency calculation and response structure.
- `test_confidence_filtering`: Verifies that only targeted weapons above threshold pass through.
- `test_alert_cooldown_mechanism`: Verifies the 3-second debouncing timer stops alarm spam.
- `test_database_insert_and_verify`: Verifies SQLite CRUD operations and human verification states.
- `test_api_status_endpoints`: Verifies all REST routes and threshold updates.
- `test_api_history_endpoints`: Verifies event retrieval and verification logging.
- `test_websocket_connection`: Verifies active bi-directional WebSocket communication.

---

## 9. 🔐 Environment Variables

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `MODEL_PATH` | `models/trained/weapon_threat_yolov8.pt` | Path to fine-tuned weapon weights |
| `CAMERA_SOURCE` | `0` | Camera device index or RTSP URL |
| `DATABASE_URL` | `sqlite:///./security_assistant.db` | Local SQLite database URI |
| `HOST` | `127.0.0.1` | Backend bind address |
| `PORT` | `8000` | Backend API port |

---

## 10. ⚠️ Known Limitations & Next Steps for Model Training

### Current MVP Limitations:
1. **Visual Exposure Required:** Only visually unconcealed weapons can be identified.
2. **Environmental Occlusions:** Heavy smoke, severe motion blur, or poor illumination may reduce detection confidence.
3. **Hardware Platform:** Currently running on workstation/laptop CPU. On edge devices (Jetson Nano / Raspberry Pi 5), model quantization (ONNX / TensorRT INT8) is recommended.

### Next Steps for Training the Custom Weapon Model:
1. Assemble a balanced dataset containing 5,000+ annotated images of firearms (handguns, rifles) and edged weapons (knives, blades) alongside negative distractor images (phones, drills, wallets).
2. Execute the fine-tuning pipeline:
   ```powershell
   python training/train.py --data data/dataset.yaml --base yolov8s.pt --epochs 60 --batch 16
   ```
3. Evaluate metrics using:
   ```powershell
   python training/evaluate.py --weights models/trained/weapon_yolov8_best.pt
   ```
#   R A I - V i d e o - A n a l y t i c s 2  
 