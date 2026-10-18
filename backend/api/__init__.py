from backend.api.camera import router as camera_router
from backend.api.detection import router as detection_router
from backend.api.alerts import router as alerts_router
from backend.api.history import router as history_router

__all__ = ["camera_router", "detection_router", "alerts_router", "history_router"]
