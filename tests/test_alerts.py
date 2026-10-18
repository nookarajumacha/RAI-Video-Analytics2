"""Unit tests for Alert Dispatcher logic and cooldown verification.
"""

import sys
import os
import time

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alerts.audio import AudioAlertSystem
from alerts.visual import VisualHUD
from alerts.notification import AlertDispatcher


def test_audio_cooldown():
    audio = AudioAlertSystem(enabled=True, speech_enabled=False)
    # First alert should trigger
    now = time.time()
    audio._last_alert_time = now - 5.0
    audio.trigger_warning("knife", 0.90, cooldown=3.0)
    assert audio._last_alert_time > now - 1.0

    # Immediate second call within cooldown should be ignored
    prev_time = audio._last_alert_time
    audio.trigger_warning("knife", 0.90, cooldown=3.0)
    assert audio._last_alert_time == prev_time

def test_visual_hud_initialization():
    hud = VisualHUD(show_hud=True, flash_on_threat=True)
    assert hud.show_hud is True
    assert hud.flash_on_threat is True

def test_alert_dispatcher_initialization():
    dummy_config = {
        "alerts": {
            "cooldown_seconds": 2.0,
            "audio": {"enabled": True, "speech_warning": False},
            "visual": {"show_hud": True, "flash_screen_on_threat": True},
            "logging": {"enabled": False, "save_threat_snapshots": False}
        }
    }
    dispatcher = AlertDispatcher(dummy_config)
    assert dispatcher.cooldown == 2.0
    assert dispatcher.audio.enabled is True

if __name__ == "__main__":
    print("Running tests...")
    test_audio_cooldown()
    test_visual_hud_initialization()
    test_alert_dispatcher_initialization()
    print("All tests passed successfully!")

