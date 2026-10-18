"""Thread-safe audio alert mechanism supporting voice warnings and acoustic beeps.
"""

import threading
import time
import logging

logger = logging.getLogger("AudioAlert")

class AudioAlertSystem:
    def __init__(self, enabled: bool = True, speech_enabled: bool = True):
        self.enabled = enabled
        self.speech_enabled = speech_enabled

    def play_warning(self, threat_name: str, confidence: float):
        """Dispatches an audio warning asynchronously so inference is never blocked."""
        if not self.enabled:
            return

        threading.Thread(
            target=self._execute_audio,
            args=(threat_name, confidence),
            daemon=True
        ).start()

    def _execute_audio(self, threat_name: str, confidence: float):
        message = f"Warning: Potential {threat_name} detected."
        logger.warning(f"[AUDIO ALERT TRIGGERED] {message} (Confidence: {confidence * 100:.1f}%)")

        # 1. Attempt system speech engine
        if self.speech_enabled:
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.setProperty('rate', 165)
                engine.setProperty('volume', 1.0)
                engine.say(message)
                engine.runAndWait()
                return
            except Exception as e:
                logger.debug(f"pyttsx3 speech fallback triggered: {e}")

        # 2. Fallback to Windows system beep tone
        try:
            import winsound
            winsound.Beep(1200, 350)
        except Exception:
            pass
