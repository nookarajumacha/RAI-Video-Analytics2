# Development Roadmap: 10 Progressive Phases

```
                  ┌────────────────────────────────────────┐
                  │ 1. Problem & Competitor Research       │
                  └──────────────────┬─────────────────────┘
                                     │
                  ┌──────────────────▼─────────────────────┐
                  │ 2. Define Product & MVP Requirements   │
                  └──────────────────┬─────────────────────┘
                                     │
                  ┌──────────────────▼─────────────────────┐
                  │ 3. Weapon Dataset Collection & Labels  │
                  └──────────────────┬─────────────────────┘
                                     │
                  ┌──────────────────▼─────────────────────┐
                  │ 4. Computer Vision Model Architecture   │
                  └──────────────────┬─────────────────────┘
                                     │
                  ┌──────────────────▼─────────────────────┐
                  │ 5. Model Fine-Tuning & Validation      │
                  └──────────────────┬─────────────────────┘
                                     │
                  ┌──────────────────▼─────────────────────┐
                  │ 6. Image Benchmark & Stress Testing    │
                  └──────────────────┬─────────────────────┘
                                     │
                  ┌──────────────────▼─────────────────────┐
                  │ 7. Real-Time Camera Detection Engine   │
                  └──────────────────┬─────────────────────┘
                                     │
                  ┌──────────────────▼─────────────────────┐
                  │ 8. Audio / Visual / Alert Integration  │
                  └──────────────────┬─────────────────────┘
                                     │
                  ┌──────────────────▼─────────────────────┐
                  │ 9. Edge AI Optimization (Jetson/Pi/NPU)│
                  └──────────────────┬─────────────────────┘
                                     │
                  ┌──────────────────▼─────────────────────┐
                  │ 10. Smart Glasses / Wearable Hardware  │
                  └────────────────────────────────────────┘
```

---

## Phase Checklist & Criteria

### Phase 1: Problem & Market Research
- [x] Investigate commercial landscape (ZeroEyes, Vaidio, Axon).
- [x] Identify critical differentiators (Wearable vs fixed, direct guard alert vs SOC).
- [x] Define Target Users and Value Proposition.

### Phase 2: MVP Product Definition
- [x] Scope: Visible firearms & knives only.
- [x] Exclude facial recognition, drug detection, and concealed scanning.
- [x] System specifications & requirements finalized.

### Phase 3: Dataset Pipeline
- [ ] Select open-access datasets (e.g., Roboflow Weapon Detection, Kaggle Gun/Knife datasets).
- [ ] Verify licensing (commercial/academic friendly).
- [ ] Dataset hygiene: de-duplication, format conversion to YOLO format (`images/` and `labels/`).
- [ ] 70/20/10 Train/Val/Test split.

### Phase 4: Model Selection & Architecture
- [ ] Select lightweight detector: YOLOv8n / YOLOv8s / YOLOv11n for real-time edge speed (>30 FPS).
- [ ] Establish input resolutions (640x640 vs 480x480 for edge devices).

### Phase 5: Model Training & Evaluation
- [ ] Fine-tune weights on dataset using `training/train.py`.
- [ ] Evaluate metrics: mAP@0.5, mAP@0.5:0.95, Precision, Recall, F1-Score.
- [ ] Measure false positive rates on negative images (people holding phones, wallets, drills).

### Phase 6: Image Benchmark & Robustness Testing
- [ ] Evaluate against tough scenarios: low light, motion blur, partial occlusion, varying distances.
- [ ] Run automated batch image testing via `detection/image_detection.py`.

### Phase 7: Real-Time Camera Detection
- [ ] Integrate OpenCV video capture stream via `hardware/camera.py`.
- [ ] Real-time bounding box projection and latency monitoring (>25 FPS on laptop).

### Phase 8: Alert & Verification Dispatcher
- [ ] Audio alert: Text-to-speech warning ("Potential firearm detected").
- [ ] Visual HUD: Flashing perimeter border and threat label.
- [ ] Anti-spam cooldown timer to avoid alert flooding.

### Phase 9: Edge AI Acceleration
- [ ] Export weights to ONNX / TensorRT / OpenVINO format.
- [ ] Benchmark on embedded target (e.g., Raspberry Pi 5 with AI Kit / NVIDIA Jetson Orin Nano).

### Phase 10: Wearable / Smart Glasses Form Factor
- [ ] Integrate wearable camera (USB micro-camera / ESP32-CAM / smart-glasses module).
- [ ] Transmit alerts to discreet earpiece or heads-up display.
