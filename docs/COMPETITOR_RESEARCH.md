# Phase 1: Competitor & Market Research

## Executive Summary
Existing commercial weapon-detection solutions predominantly analyze video streams from fixed CCTV infrastructure feeding into central Security Operations Centers (SOC). 
Our project introduces a transformative paradigm shift: **transitioning AI threat detection from fixed cameras into an officer-facing, wearable system with instantaneous, heads-up edge alerting.**

---

## Competitor Matrix

| Company / Product | Category | Primary Input | Target Threats | Wearable? | Latency / Alert Path | Facial Recognition | Key Distinction from Our Solution |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ZeroEyes** | Commercial AI Surveillance | Fixed IP CCTV | Visible Firearms, Knives | ❌ No | AI -> Central SOC Human Analyst -> Client (3-5s) | ❌ No | Dependent on fixed infrastructure and central human verification desks before sending alert to site. |
| **Vaidio / VAIBS** | Video Analytics Platform | Fixed IP CCTV | Weapons, Intrusion, Vehicles | ❌ No | Central VMS / SOC alerts | Optional | Broad enterprise video analytics platform, not wearable or mobile for individual security guards. |
| **Axon (Taser / Body 3)** | Police Body-Worn Camera | Wearable Camera | Recording & Evidence Management | ✅ Yes | Uploads video to Evidence.com; limited real-time local threat AI | ❌ Restrained | Primary goal is evidentiary video recording and officer accountability, not autonomous real-time threat detection HUD. |
| **Ray-Ban Meta / Consumer Smart Glasses** | Consumer Wearable | Glasses Camera | General VQA, Assistant queries | ✅ Yes | Cloud LLM queries (several seconds latency) | ❌ No | General lifestyle product; lacks high-FPS real-time weapon detection models and ruggedized security UX. |
| **Our Solution: Wearable AI Assistant** | **Wearable Edge AI Assistant** | **Body / Glasses Camera** | **Visible Firearms & Knives** | **✅ Yes** | **Direct on-device audio/visual alert to officer (<100ms)** | **❌ Strictly Excluded** | **Mobile, hands-free, wearable situational awareness tool giving immediate personal alerts directly to the guard.** |

---

## Market Gap
1. **Blind Spots in Fixed Cameras:** Traditional CCTV systems have blind spots, low resolution at long distances, and fixed angles. An active patrol officer moves where incidents actually happen.
2. **Alert Latency:** A standard CCTV-to-SOC pipeline takes 5 to 30 seconds for a human operator or central server to dispatch an alert. In active threat scenarios, seconds save lives.
3. **Situational Awareness:** A wearable AI assistant acts as a digital "second pair of eyes", alerting the officer even when a threat appears in their peripheral view or when looking across crowded spaces.

---

## Target Audience
- **Campus & School Security Personnel:** Rapid reaction in active shooter mitigation.
- **Shopping Mall & Airport Patrollers:** Constant foot patrols in high-density foot traffic.
- **Private Event & Concert Security:** Temporary venues lacking permanent high-density CCTV infrastructure.
- **Industrial & Critical Infrastructure Guards:** High-risk entry checkpoints and perimeter walks.

---

## Unique Selling Proposition (USP)
> *"Real-time visual threat detection directly in the guard's field of view — hands-free, private, and running low-latency on the edge."*
