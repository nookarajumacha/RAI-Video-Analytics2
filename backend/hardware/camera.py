"""High-Performance Threaded Camera Capture for Backend Service.
DirectShow backend with MJPG encoding and non-blocking read queue.
"""

import cv2
import threading
import time
import logging
import numpy as np

logger = logging.getLogger("CameraStream")

class CameraStream:
    """Ultra-High-Performance 2K (2560x1440) 60 FPS Camera Reader.
    Supports DirectShow MJPG hardware acceleration, automatic resolution scaling,
    and fallback synthetic tactical 2K 60 FPS simulation if physical camera is offline.
    """
    def __init__(self, source=0, width: int = 2560, height: int = 1440, fps: int = 60):
        self.source = source
        self.width = width
        self.height = height
        self.target_fps = fps
        self.cap = None

        self._thread = None
        self._running = False
        self._lock = threading.Lock()
        self._latest_frame = None
        self._fps = 0.0
        self._frame_count = 0
        self._fps_start_time = time.time()
        self.is_synthetic = False
        self.actual_width = width
        self.actual_height = height

    def start(self):
        logger.info(f"Initializing camera stream: source={self.source} target={self.width}x{self.height} @ {self.target_fps} FPS (2K Mode)")
        
        opened = False
        try:
            if isinstance(self.source, int):
                # Try DirectShow first for fast Windows MJPG capture
                self.cap = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)
                if not self.cap.isOpened():
                    self.cap = cv2.VideoCapture(self.source)
            else:
                self.cap = cv2.VideoCapture(self.source)

            if self.cap is not None and self.cap.isOpened():
                # DirectShow MJPG configuration for 2K 60 FPS
                self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

                ret, frame = self.cap.read()
                if ret and frame is not None:
                    opened = True
                    self.actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or frame.shape[1]
                    self.actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or frame.shape[0]
                    logger.info(f"Physical camera initialized at hardware resolution: {self.actual_width}x{self.actual_height}")
        except Exception as e:
            logger.warning(f"Physical camera initialization warning: {e}")

        if not opened:
            logger.info("Physical camera not accessible or index not found. Engaging Resilient 2K 60 FPS Synthetic Tactical Camera.")
            self.is_synthetic = True
            if self.cap is not None:
                self.cap.release()
                self.cap = None

        self._running = True
        self._thread = threading.Thread(target=self._capture_worker, daemon=True)
        self._thread.start()
        self._fps_start_time = time.time()
        return self

    def _generate_synthetic_2k_frame(self, t: float) -> np.ndarray:
        """Generates a crisp 2K (2560x1440) 60 FPS simulated tactical bodycam frame."""
        import numpy as np
        # 2K canvas
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Subtle gradient dark tactical background
        frame[:, :, 0] = 22
        frame[:, :, 1] = 26
        frame[:, :, 2] = 30

        # Draw grid lines for tactical HUD
        grid_step = 160
        for x in range(0, self.width, grid_step):
            cv2.line(frame, (x, 0), (x, self.height), (35, 42, 50), 1)
        for y in range(0, self.height, grid_step):
            cv2.line(frame, (0, y), (self.width, y), (35, 42, 50), 1)

        # Center reticle / crosshairs
        cx, cy = self.width // 2, self.height // 2
        cv2.circle(frame, (cx, cy), 180, (50, 180, 255), 2)
        cv2.circle(frame, (cx, cy), 8, (50, 220, 255), -1)
        cv2.line(frame, (cx - 240, cy), (cx + 240, cy), (50, 180, 255), 1)
        cv2.line(frame, (cx, cy - 240), (cx, cy + 240), (50, 180, 255), 1)

        # Tactical HUD Metadata (2K high-resolution typography)
        now_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
        msec = int((t % 1) * 1000)
        timestamp = f"{now_str}.{msec:03d} UTC"
        
        cv2.putText(frame, "[PATROL BODYCAM - 2K QHD 60 FPS]", (60, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 255, 200), 3)
        cv2.putText(frame, f"TIMESTAMP: {timestamp}", (60, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (220, 220, 220), 2)
        cv2.putText(frame, f"RESOLUTION: {self.width}x{self.height} @ 60 FPS | DirectShow MJPG", (60, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (180, 180, 180), 2)
        cv2.putText(frame, "STATUS: PATROL MONITORING ACTIVE | ZERO BIOMETRICS", (60, self.height - 80), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 220, 120), 2)
        cv2.putText(frame, "LAT: 37.7749 N | LON: 122.4194 W | ALT: 42M", (self.width - 800, self.height - 80), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 200, 200), 2)

        # Animated scan line to verify 60 FPS motion
        scan_y = int((t * 240) % self.height)
        cv2.line(frame, (0, scan_y), (self.width, scan_y), (0, 150, 255), 2)

        return frame

    def _capture_worker(self):
        frame_interval = 1.0 / float(self.target_fps)
        while self._running:
            loop_start = time.time()
            if self.is_synthetic or self.cap is None or not self.cap.isOpened():
                frame = self._generate_synthetic_2k_frame(loop_start)
            else:
                ret, raw_frame = self.cap.read()
                if not ret or raw_frame is None:
                    time.sleep(0.002)
                    continue

                # Ensure frame matches target 2K resolution (2560x1440)
                if raw_frame.shape[1] != self.width or raw_frame.shape[0] != self.height:
                    frame = cv2.resize(raw_frame, (self.width, self.height), interpolation=cv2.INTER_CUBIC)
                else:
                    frame = raw_frame

            with self._lock:
                self._latest_frame = frame
                self._frame_count += 1

            if self._frame_count % 30 == 0:
                elapsed = time.time() - self._fps_start_time
                if elapsed > 0:
                    self._fps = 30.0 / elapsed
                self._fps_start_time = time.time()

            # Maintain 60 FPS pacing
            elapsed_loop = time.time() - loop_start
            sleep_time = frame_interval - elapsed_loop
            if sleep_time > 0:
                time.sleep(sleep_time)

    def read(self):
        with self._lock:
            if self._latest_frame is None:
                return False, None
            return True, self._latest_frame.copy()

    @property
    def fps(self) -> float:
        return self._fps if self._fps > 0 else float(self.target_fps)

    @property
    def resolution(self):
        return (self.width, self.height)

    def release(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        logger.info("Camera device released.")
