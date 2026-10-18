"""Comprehensive test suite covering:
1. Model loading & interface
2. Detection processing & preprocessing
3. Confidence filtering & threat classification
4. Alert cooldown & debouncing
5. SQLite Database operations
6. FastAPI REST endpoints & WebSocket
"""

import sys
import os
import pytest
import numpy as np
from datetime import datetime, timezone
from fastapi.testclient import TestClient

# Ensure root workspace is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.config.settings import settings
from backend.database.database import init_db, SessionLocal
from backend.database.models import DetectionEvent
from backend.detection.detector import BaseDetector, MockDemoDetector, ThreatDetectionService, YOLOThreatDetector
from backend.detection.preprocessing import preprocess_frame
from backend.detection.postprocessing import filter_and_classify_detections
from backend.alerts.alert_manager import AlertManager
from backend.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()
    with SessionLocal() as db:
        db.query(DetectionEvent).delete()
        db.commit()

# 1. Model Loading Test
def test_model_loading_interface():
    mock_detector = MockDemoDetector()
    assert isinstance(mock_detector, BaseDetector)
    info = mock_detector.get_model_info()
    assert info["is_loaded"] is True
    assert info["type"] == "MockDemoDetector"

# 2. Preprocessing & Detection Test
def test_preprocessing():
    dummy_img = np.zeros((480, 640, 3), dtype=np.uint8)
    canvas, scale, padding = preprocess_frame(dummy_img, target_size=640)
    assert canvas.shape == (640, 640, 3)
    assert scale > 0

def test_threat_detection_service_with_mock():
    mock_detector = MockDemoDetector()
    service = ThreatDetectionService(detector=mock_detector)
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    res = service.process_frame(frame, confidence_threshold=0.5)
    assert "detections" in res
    assert "latency_ms" in res
    assert res["status"] == "No potential threat detected"

# 3. Confidence Filtering & Classification Test
def test_confidence_filtering():
    raw_candidates = [
        {"class_name": "gun", "confidence": 0.88, "bbox": [100, 100, 300, 300]},
        {"class_name": "knife", "confidence": 0.35, "bbox": [50, 50, 150, 150]},  # Below threshold
        {"class_name": "umbrella", "confidence": 0.95, "bbox": [20, 20, 200, 200]} # Not a threat
    ]
    filtered = filter_and_classify_detections(
        raw_detections=raw_candidates,
        confidence_threshold=0.50,
        frame_width=1280,
        frame_height=720
    )
    assert len(filtered) == 1
    assert filtered[0]["label"] == "Firearm"
    assert filtered[0]["status"] == "Potential Threat"
    assert filtered[0]["action"] == "Human verification required"

# 4. Alert Cooldown & Debouncing Test
def test_alert_cooldown_mechanism():
    mgr = AlertManager()
    mgr.set_alerts_enabled(False) # Mute audio for test
    mgr.cooldown_seconds = 2.0

    threat = [{"object_type": "firearm", "label": "Firearm", "confidence": 0.92, "bbox": [10, 10, 50, 50]}]

    # 1st detection -> TRIGGERED
    events_1 = mgr.process_threats(threat)
    assert len(events_1) == 1
    assert events_1[0]["alert_status"] == "TRIGGERED"

    # Immediate 2nd detection -> SUPPRESSED_COOLDOWN
    events_2 = mgr.process_threats(threat)
    assert len(events_2) == 1
    assert events_2[0]["alert_status"] == "SUPPRESSED_COOLDOWN"

# 5. Database Operations Test
def test_database_insert_and_verify():
    with SessionLocal() as db:
        event = DetectionEvent(
            object_type="knife",
            confidence=0.85,
            source="camera_0",
            alert_status="TRIGGERED",
            human_verification="PENDING"
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        event_id = event.id

        # Read back
        fetched = db.query(DetectionEvent).filter(DetectionEvent.id == event_id).first()
        assert fetched is not None
        assert fetched.object_type == "knife"

        # Update verification
        fetched.human_verification = "CONFIRMED"
        db.commit()

        updated = db.query(DetectionEvent).filter(DetectionEvent.id == event_id).first()
        assert updated.human_verification == "CONFIRMED"

# 6. API Endpoints Test
def test_api_status_endpoints():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "ONLINE"

    res_detection = client.get("/api/detection/status")
    assert res_detection.status_code == 200
    assert "monitored_threats" in res_detection.json()

    res_alerts = client.get("/api/alerts/config")
    assert res_alerts.status_code == 200
    assert "confidence_threshold" in res_alerts.json()

    # Toggle alerts
    res_toggle = client.post("/api/alerts/toggle", json={"enabled": False})
    assert res_toggle.status_code == 200
    assert res_toggle.json()["alerts_enabled"] is False

    # Update threshold
    res_thresh = client.post("/api/alerts/threshold", json={"threshold": 0.65})
    assert res_thresh.status_code == 200
    assert res_thresh.json()["confidence_threshold"] == 0.65

def test_api_history_endpoints():
    # Insert dummy event
    with SessionLocal() as db:
        ev = DetectionEvent(object_type="firearm", confidence=0.91, alert_status="TRIGGERED")
        db.add(ev)
        db.commit()
        db.refresh(ev)
        ev_id = ev.id

    # GET history
    res = client.get("/api/history")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert data[0]["id"] == ev_id

    # Verify event
    res_verify = client.post(f"/api/history/{ev_id}/verify", json={"human_verification": "CONFIRMED"})
    assert res_verify.status_code == 200
    assert res_verify.json()["human_verification"] == "CONFIRMED"

# 7. WebSocket Test
def test_websocket_connection():
    with client.websocket_connect("/ws") as websocket:
        websocket.send_text("ping")
        data = websocket.receive_text()
        assert data == "pong"
