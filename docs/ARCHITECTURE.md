# System Architecture & Technical Specifications

## High-Level Data Flow

```
+-----------------------------------------------------------+
|                      PHYSICAL WORLD                       |
+-----------------------------------------------------------+
                              |
                              v
                  +-----------------------+
                  |  Wearable Lens / Cam  |
                  +-----------------------+
                              |
                    [Raw Video Frames]
                              |
                              v
         +-----------------------------------------+
         |     Pre-processing (OpenCV Engine)     |
         |  - Frame resizing (640x640)             |
         |  - Letterboxing & Color Normalization   |
         +-----------------------------------------+
                              |
                              v
         +-----------------------------------------+
         |      Edge AI Inference (YOLO Model)     |
         |  - Single-stage bounding box regression |
         |  - Multi-class confidence calculation   |
         |  - Non-Maximum Suppression (IoU: 0.45)  |
         +-----------------------------------------+
                              |
            +-----------------+-----------------+
            |                                   |
            v                                   v
      [No Threat]                       [Threat Detected]
            |                                   |
    (Continue Stream)              [Confidence >= Threshold?]
                                                |
                                                v
                               +---------------------------------+
                               |    Alert Dispatcher & HUD       |
                               |  - Audio: Discreet Earpiece     |
                               |  - Visual: Red Border HUD Glow  |
                               |  - Snapshot: Timestamped Event  |
                               +---------------------------------+
                                                |
                                                v
                               +---------------------------------+
                               |   Human Verification Loop       |
                               |  (Officer Assesses Threat)      |
                               +---------------------------------+
```

---

## Software Component Layout

| Module | Location | Purpose |
| :--- | :--- | :--- |
| **Configuration** | `config/config.yaml` | Thresholds, class mappings, audio flags, camera indices. |
| **Inference Engine** | `detection/detector.py` | Model loader, frame inference, threat filtering. |
| **Live Stream** | `detection/camera_detection.py` | Real-time loop tying camera feed to HUD and alerts. |
| **Batch Image** | `detection/image_detection.py` | Single image and folder validation testing. |
| **Alert Engine** | `alerts/notification.py` | Cooldown timers, audio dispatch, visual overlay. |
| **Hardware Abstraction** | `hardware/camera.py` | Webcam, USB cam, RTSP, or wearable sensor streams. |
| **Training Pipeline** | `training/train.py` | Fine-tuning YOLO weights on annotated weapon datasets. |
| **Dashboard** | `dashboard/app.py` | Web UI for live review, log history, and demo presentations. |
