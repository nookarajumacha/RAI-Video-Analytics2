"""Audio alerting module for Wearable AI Security Assistant.
Supports non-blocking spoken voice alerts and tone warnings.
"""

import threading
import time
import logging

logger = logging.getLogger("AudioAlert")

class AudioAlertSystem:
    def __init__(self, enabled: bool = True, speech_enabled: bool = True, voice_rate: int = 160, volume: float = 1.0):
        self.enabled = enabled
        self.speech_enabled = speech_enabled
        self.voice_rate = voice_rate
        self.volume = volume
        self._last_alert_time = 0.0

    def trigger_warning(self, threat_name: str, confidence: float, cooldown: float = 3.0):
        """Trigger an audio warning in a separate thread if cooldown has passed."""
        if not self.enabled:
            return

        now = time.time()
        if now - self._last_alert_time < cooldown:
            return  # Under cooldown

        self._last_alert_time = now
        threading.Thread(target=self._play_alert, args=(threat_name, confidence), daemon=True).start()

    def _play_alert(self, threat_name: str, confidence: float):
        message = f"Warning: Potential {threat_name} detected."
        logger.warning(f"[AUDIO ALERT] {message} (Confidence: {confidence * 100:.1f}%)")

        if self.speech_enabled:
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.setProperty('rate', self.voice_rate)
                engine.setProperty('volume', self.volume)
                engine.say(message)
                engine.runAndWait()
            except Exception as e:
                logger.error(f"Speech synthesis error: {e}")
                # Fallback to system acoustic beep on Windows
                try:
                    import winsound
                    winsound.Beep(1200, 400)
                except Exception:
                    pass
        else:
            try:
                import winsound
                winsound.Beep(1000, 300)
            except Exception:
                pass
