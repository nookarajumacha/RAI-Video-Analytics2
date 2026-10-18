"""FastAPI Backend Application for Wearable AI Security Assistant.
Provides REST endpoints and WebSocket channels for the React Dashboard.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.config.settings import settings
from backend.database.database import init_db
from backend.alerts.alert_manager import alert_manager
from backend.api.camera import router as camera_router, camera_manager
from backend.api.detection import router as detection_router
from backend.api.alerts import router as alerts_router
from backend.api.history import router as history_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("SecurityBackend")

class ConnectionManager:
    """Manages active WebSocket connections to the React Dashboard."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._loop = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Remaining: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.debug(f"Failed to send to client: {e}")
                self.disconnect(connection)

ws_manager = ConnectionManager()

# Background telemetry ticker for WebSocket clients
async def telemetry_broadcaster():
    while True:
        try:
            if ws_manager.active_connections:
                telemetry = {
                    "type": "TELEMETRY",
                    "camera_active": camera_manager.is_active,
                    "camera_fps": camera_manager.fps,
                    "camera_resolution": camera_manager.resolution,
                    "stream_profile": "2K QHD @ 60 FPS",
                    "alerts_enabled": alert_manager.alerts_enabled,
                    "confidence_threshold": round(alert_manager.confidence_threshold, 2),
                    "ai_status": "RUNNING",
                    "status_text": "ACTIVE (2K 60 FPS)" if camera_manager.is_active else "STANDBY"
                }
                await ws_manager.broadcast(telemetry)
        except Exception as e:
            logger.debug(f"Telemetry broadcast error: {e}")
        await asyncio.sleep(1.0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize SQLite tables
    logger.info("Initializing SQLite database...")
    init_db()

    # Hook AlertManager callbacks to broadcast events over WebSocket
    loop = asyncio.get_event_loop()
    def on_threat_alert(event_payload):
        asyncio.run_coroutine_threadsafe(
            ws_manager.broadcast({"type": "THREAT_ALERT", "data": event_payload}),
            loop
        )
    alert_manager.register_listener(on_threat_alert)

    # Start telemetry background task
    telemetry_task = asyncio.create_task(telemetry_broadcaster())
    logger.info(f"{settings.PROJECT_NAME} v{settings.VERSION} backend started.")

    yield

    # Shutdown
    telemetry_task.cancel()
    alert_manager.unregister_listener(on_threat_alert)
    camera_manager.stop()
    logger.info("Backend safely shutdown.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for Wearable AI Visual Threat Detection Assistant",
    lifespan=lifespan
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API Routers
app.include_router(camera_router)
app.include_router(detection_router)
app.include_router(alerts_router)
app.include_router(history_router)

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "ONLINE",
        "camera_active": camera_manager.is_active,
        "docs_url": "/docs"
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection open and receive optional client heartbeats / commands
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.debug(f"WebSocket session closed: {e}")
        ws_manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=False)
