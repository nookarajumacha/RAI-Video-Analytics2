"""Alert Manager with Debouncing, Cooldown Timers, and Local Audit Logging.
"""

import time
import json
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timezone

from backend.config.settings import settings
from backend.alerts.audio_alert import AudioAlertSystem
from backend.database.database import SessionLocal
from backend.database.models import DetectionEvent

logger = logging.getLogger("AlertManager")

class AlertManager:
    def __init__(self):
        self.cooldown_seconds = settings.ALERT_COOLDOWN_SECONDS
        self.alerts_enabled = settings.AUDIO_ALERTS_ENABLED_DEFAULT
        self.confidence_threshold = settings.DEFAULT_CONFIDENCE_THRESHOLD
        
        self.audio = AudioAlertSystem(
            enabled=self.alerts_enabled,
            speech_enabled=settings.SPEECH_WARNING_ENABLED
        )
        
        # Threat cooldown tracking: {object_type: last_alert_epoch_seconds}
        self._last_alert_times: Dict[str, float] = {}
        
        # Callbacks for WebSocket broadcasting
        self._listeners: List[Callable[[Dict[str, Any]], None]] = []

    def set_alerts_enabled(self, enabled: bool):
        self.alerts_enabled = enabled
        self.audio.enabled = enabled
        logger.info(f"Alerts enabled status updated to: {enabled}")

    def set_confidence_threshold(self, threshold: float):
        self.confidence_threshold = max(0.1, min(0.99, threshold))
        logger.info(f"Confidence threshold updated to: {self.confidence_threshold:.2f}")

    def register_listener(self, callback: Callable[[Dict[str, Any]], None]):
        """Register a callback for real-time WebSocket notifications."""
        self._listeners.append(callback)

    def unregister_listener(self, callback: Callable[[Dict[str, Any]], None]):
        if callback in self._listeners:
            self._listeners.remove(callback)

    def process_threats(self, threats: List[Dict[str, Any]], source: str = "camera_0") -> List[Dict[str, Any]]:
        """Processes a list of detected threats from the vision pipeline.
        Enforces cooldown and logs events to SQLite.
        """
        now = time.time()
        triggered_events = []

        for threat in threats:
            obj_type = threat.get("object_type", "unknown").lower()
            confidence = threat.get("confidence", 0.0)
            bbox = threat.get("bbox", [])

            # Check threshold
            if confidence < self.confidence_threshold:
                continue

            last_time = self._last_alert_times.get(obj_type, 0.0)
            is_cooling_down = (now - last_time) < self.cooldown_seconds

            alert_status = "SUPPRESSED_COOLDOWN" if is_cooling_down else "TRIGGERED"

            # Create database audit record
            event_id = None
            try:
                with SessionLocal() as db:
                    event = DetectionEvent(
                        object_type=obj_type,
                        confidence=confidence,
                        timestamp=datetime.now(timezone.utc),
                        source=source,
                        alert_status=alert_status,
                        bounding_box=json.dumps(bbox),
                        human_verification="PENDING"
                    )
                    db.add(event)
                    db.commit()
                    db.refresh(event)
                    event_id = event.id
            except Exception as e:
                logger.error(f"Failed to record detection event to SQLite: {e}")

            event_payload = {
                "id": event_id,
                "object_type": obj_type,
                "display_name": threat.get("label", obj_type.title()),
                "confidence": round(confidence, 4),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": source,
                "alert_status": alert_status,
                "bounding_box": bbox,
                "human_verification": "PENDING"
            }

            if not is_cooling_down:
                self._last_alert_times[obj_type] = now
                if self.alerts_enabled:
                    self.audio.play_warning(obj_type, confidence)

            triggered_events.append(event_payload)

            # Broadcast to real-time WebSocket listeners
            for listener in list(self._listeners):
                try:
                    listener(event_payload)
                except Exception as ex:
                    logger.debug(f"Error notifying listener: {ex}")

        return triggered_events

alert_manager = AlertManager()
