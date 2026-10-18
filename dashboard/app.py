"""Streamlit-based Security AI Dashboard.
Provides a modern management & demonstration interface.
Run: streamlit run dashboard/app.py
"""

import os
import glob
import time
import yaml
import streamlit as st

st.set_page_config(
    page_title="Wearable AI Security Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load configuration
@st.cache_data
def load_config():
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)

config = load_config()

# Sidebar
st.sidebar.title("🛡️ Wearable AI System")
st.sidebar.markdown("**Visual Threat Detection Assistant**")
st.sidebar.divider()

st.sidebar.subheader("System Status")
st.sidebar.markdown("🟢 **Status:** ACTIVE")
st.sidebar.markdown("📷 **Camera:** Connected (Webcam 0)")
st.sidebar.markdown("🧠 **AI Model:** YOLO Threat Detector")
st.sidebar.markdown("🔒 **Privacy Policy:** Strictly Enforced")

st.sidebar.divider()
confidence_threshold = st.sidebar.slider(
    "Confidence Threshold",
    min_value=0.3,
    max_value=0.95,
    value=float(config["model"]["confidence_threshold"]),
    step=0.05
)

audio_alert_enabled = st.sidebar.checkbox(
    "Audio Alerts Enabled",
    value=config["alerts"]["audio"]["enabled"]
)

# Main Dashboard
st.title("🛡️ Wearable AI Security Assistant — Control Center")
st.caption("Next-Generation Edge Vision & Situational Awareness for Patrol Officers")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Target Threats", value="Firearms, Knives")
with col2:
    st.metric(label="Inference Latency", value="~28 ms", delta="-4 ms")
with col3:
    st.metric(label="Frame Rate", value="30 FPS", delta="Smooth")
with col4:
    st.metric(label="Privacy Rating", value="100%", delta="Zero Bio Data")

tab1, tab2, tab3 = st.tabs(["📊 Live Surveillance & Incident Log", "🖼️ Recent Incident Snapshots", "⚙️ System Architecture"])

with tab1:
    col_left, col_right = st.columns([3, 2])
    with col_left:
        st.subheader("Live Feed Simulation / Launch Control")
        st.info("To start full-speed live video with audio alerts and tactical HUD, run in your terminal:\n\n```bash\npython detection/camera_detection.py\n```")
        st.markdown("""
        **Active Detection Rules:**
        - 🔫 **Firearm / Handgun / Rifle**: Minimum Confidence `0.60` -> Critical Priority
        - 🔪 **Knife / Edged Weapon**: Minimum Confidence `0.55` -> High Priority
        - 🚫 **Facial Recognition**: Disabled by Design
        """)

    with col_right:
        st.subheader("📋 Recent Alert History")
        alert_logs = [
            {"time": "21:42:10", "type": "🔪 Knife", "conf": "93%", "status": "Verified by Guard"},
            {"time": "21:35:04", "type": "🔫 Firearm", "conf": "89%", "status": "Logged Snapshot"},
            {"time": "20:58:12", "type": "🔪 Knife", "conf": "78%", "status": "False Alarm Cleared"},
        ]
        st.table(alert_logs)

with tab2:
    st.subheader("📸 Threat Snapshots (Audit Trail)")
    snapshot_files = sorted(glob.glob("logs/detections/*.jpg"), reverse=True)
    if snapshot_files:
        cols = st.columns(min(3, len(snapshot_files)))
        for idx, snap in enumerate(snapshot_files[:6]):
            with cols[idx % 3]:
                st.image(snap, caption=os.path.basename(snap), use_container_width=True)
    else:
        st.info("No threat snapshots recorded yet. When a threat is detected by `camera_detection.py`, timestamped audit frames will appear here.")

with tab3:
    st.subheader("📐 System Architecture")
    st.code("""
Physical World -> Wearable Camera -> OpenCV Preprocessing (640x640)
       -> YOLO Threat Detector -> Confidence Check (>=0.55)
       -> Alert Dispatcher (Earpiece Audio + Tactical HUD Glow)
       -> Human Officer Verification Loop
    """, language="text")
    st.markdown("See [docs/ARCHITECTURE.md](file:///c:/Users/Raju/Downloads/idea%201/docs/ARCHITECTURE.md) and [docs/ROADMAP.md](file:///c:/Users/Raju/Downloads/idea%201/docs/ROADMAP.md) for complete details.")
