"""Alert Configuration API.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.alerts.alert_manager import alert_manager
from backend.config.settings import settings

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

class AlertConfigResponse(BaseModel):
    alerts_enabled: bool
    confidence_threshold: float
    cooldown_seconds: float
    speech_warning_enabled: bool

class ToggleAlertsRequest(BaseModel):
    enabled: bool

class UpdateThresholdRequest(BaseModel):
    threshold: float = Field(..., ge=0.1, le=0.99, description="Confidence threshold between 0.10 and 0.99")

@router.get("/config", response_model=AlertConfigResponse)
def get_alert_config():
    return AlertConfigResponse(
        alerts_enabled=alert_manager.alerts_enabled,
        confidence_threshold=round(alert_manager.confidence_threshold, 2),
        cooldown_seconds=alert_manager.cooldown_seconds,
        speech_warning_enabled=settings.SPEECH_WARNING_ENABLED
    )

@router.post("/toggle", response_model=AlertConfigResponse)
def toggle_alerts(req: ToggleAlertsRequest):
    alert_manager.set_alerts_enabled(req.enabled)
    return get_alert_config()

@router.post("/threshold", response_model=AlertConfigResponse)
def update_threshold(req: UpdateThresholdRequest):
    alert_manager.set_confidence_threshold(req.threshold)
    return get_alert_config()

@router.post("/test-trigger")
def test_trigger_alert():
    """Manual test trigger for verification."""
    mock_threat = [{
        "object_type": "knife",
        "label": "Knife",
        "confidence": 0.95,
        "bbox": [100, 100, 250, 250]
    }]
    events = alert_manager.process_threats(mock_threat, source="manual_test")
    return {"status": "TEST_TRIGGERED", "events": events}
