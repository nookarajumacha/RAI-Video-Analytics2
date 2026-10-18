"""Central Alert Dispatcher orchestrating audio, visual alerts, and event logging.
"""

import os
import time
import logging
from typing import Dict, Any, List
import cv2

from alerts.audio import AudioAlertSystem
from alerts.visual import VisualHUD

logger = logging.getLogger("AlertDispatcher")

class AlertDispatcher:
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get("alerts", {})
        self.cooldown = self.config.get("cooldown_seconds", 3.0)
        
        # Audio system
        audio_cfg = self.config.get("audio", {})
        self.audio = AudioAlertSystem(
            enabled=audio_cfg.get("enabled", True),
            speech_enabled=audio_cfg.get("speech_warning", True),
            voice_rate=audio_cfg.get("voice_rate", 160),
            volume=audio_cfg.get("volume", 1.0)
        )
        
        # Visual HUD
        visual_cfg = self.config.get("visual", {})
        self.visual = VisualHUD(
            show_hud=visual_cfg.get("show_hud", True),
            flash_on_threat=visual_cfg.get("flash_screen_on_threat", True)
        )
        
        # Logging & Snapshot saving
        log_cfg = self.config.get("logging", {})
        self.log_enabled = log_cfg.get("enabled", True)
        self.save_snapshots = log_cfg.get("save_threat_snapshots", True)
        self.snapshot_dir = log_cfg.get("log_dir", "logs/detections")
        if self.save_snapshots:
            os.makedirs(self.snapshot_dir, exist_ok=True)
            
        self._last_snapshot_time = 0.0

    def process_detections(self, frame, detections: List[Dict[str, Any]], fps: float = 0.0):
        """Processes detections: triggers audio warning and logs snapshot if a threat exists."""
        threats = [d for d in detections if d.get("is_threat", False)]

        if threats:
            # Pick highest confidence threat for audible alert
            top_threat = max(threats, key=lambda x: x["confidence"])
            threat_name = top_threat["label"]
            confidence = top_threat["confidence"]

            # Trigger Audio Alert (handles cooldown internally)
            self.audio.trigger_warning(threat_name, confidence, cooldown=self.cooldown)

            # Save snapshot if enabled and cooled down
            now = time.time()
            if self.save_snapshots and (now - self._last_snapshot_time >= self.cooldown):
                self._save_incident_snapshot(frame, threat_name, confidence)
                self._last_snapshot_time = now

        # Render visual HUD
        return self.visual.draw_hud(frame, detections, fps=fps)

    def _save_incident_snapshot(self, frame, threat_name: str, confidence: float):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{self.snapshot_dir}/threat_{threat_name}_{timestamp}_{int(confidence*100)}pct.jpg"
        try:
            cv2.imwrite(filename, frame)
            logger.info(f"Threat incident snapshot saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to save incident snapshot: {e}")
