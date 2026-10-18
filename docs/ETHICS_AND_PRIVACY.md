# Ethics, Privacy & Safety Guidelines

## Core Principles

The Wearable AI Security Assistant is designed as a **situational awareness decision-support tool**, not an autonomous policing or automated arrest mechanism.

---

## 1. What This System Does NOT Do (Explicit Boundaries)
- ❌ **No Facial Recognition:** The system does not recognize, identify, track, or index individual identities or biometric facial features.
- ❌ **No Concealed Weapon Claims:** A standard optical camera can only detect visually exposed objects. The system explicitly makes zero claims about concealed or holstered objects.
- ❌ **No Drug / Chemical Detection:** Visual cameras cannot verify chemical compounds or illicit substances in opaque packets, bottles, or pockets.
- ❌ **No Autonomous Action:** The AI will never dispatch lethal or non-lethal counter-actions automatically; it only elevates alerts to human guards.

---

## 2. Human-in-the-Loop Verification
- The AI's role is to catch peripheral threats and calculate confidence probabilities.
- All detections are categorized as **"Potential Threats"**, prompting the authorized guard to visually verify before reacting.
- Mitigates false positives (e.g., umbrellas, black wallets, toolboxes, drills, or phone cases misidentified under poor angles).

---

## 3. Privacy-First Edge Design
- **Local Inference:** Video frames are analyzed locally in device memory (RAM) and immediately discarded.
- **Zero Persistent Bulk Recording by Default:** Unlike surveillance body-cams that record 24/7 footage of innocent bystanders, this assistant operates in real-time inference mode without streaming mass footage to third-party clouds.
- **Auditable Alert Logging:** When a high-confidence threat is detected, only a timestamped snapshot of the bounding box and confidence score is retained for post-incident review.
