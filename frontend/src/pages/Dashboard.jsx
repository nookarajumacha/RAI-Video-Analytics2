import React, { useState, useEffect, useRef } from 'react';
import SystemStatus from '../components/SystemStatus';
import CameraFeed from '../components/CameraFeed';
import DetectionOverlay from '../components/DetectionOverlay';
import AlertPanel from '../components/AlertPanel';
import DetectionHistory from '../components/DetectionHistory';
import { wsService } from '../services/websocket';

const BACKEND_URL = 'http://127.0.0.1:8000';

export default function Dashboard() {
  const [cameraActive, setCameraActive] = useState(false);
  const [alertsEnabled, setAlertsEnabled] = useState(true);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.50);
  const [telemetry, setTelemetry] = useState({ camera_fps: 60.0 });
  const [currentThreat, setCurrentThreat] = useState(null);
  const [hasActiveThreat, setHasActiveThreat] = useState(false);
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isTesting, setIsTesting] = useState(false);

  const threatTimeoutRef = useRef(null);

  // Load initial state on mount
  useEffect(() => {
    fetchStatus();
    fetchAlertConfig();
    fetchHistory();

    // Connect WebSocket
    wsService.connect();
    const unsubscribe = wsService.subscribe((msg) => {
      if (msg.type === 'TELEMETRY') {
        setTelemetry(msg);
        setCameraActive(msg.camera_active);
        setAlertsEnabled(msg.alerts_enabled);
      } else if (msg.type === 'THREAT_ALERT') {
        handleThreatAlert(msg.data);
      }
    });

    return () => {
      unsubscribe();
      wsService.disconnect();
    };
  }, []);

  const handleThreatAlert = (data) => {
    setCurrentThreat(data);
    setHasActiveThreat(true);

    // Refresh history
    fetchHistory();

    // Reset visual threat alert banner after 4 seconds of silence
    if (threatTimeoutRef.current) clearTimeout(threatTimeoutRef.current);
    threatTimeoutRef.current = setTimeout(() => {
      setHasActiveThreat(false);
    }, 4000);
  };

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/camera/status`);
      if (res.ok) {
        const data = await res.json();
        setCameraActive(data.is_active);
      }
    } catch (e) {
      console.debug('Backend offline or initializing:', e);
    }
  };

  const fetchAlertConfig = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/alerts/config`);
      if (res.ok) {
        const data = await res.json();
        setAlertsEnabled(data.alerts_enabled);
        setConfidenceThreshold(data.confidence_threshold);
      }
    } catch (e) {
      console.debug('Error fetching alert config:', e);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/history?limit=25`);
      if (res.ok) {
        const data = await res.json();
        setHistory(data);
      }
    } catch (e) {
      console.debug('Error fetching history:', e);
    }
  };

  const toggleCamera = async () => {
    setIsLoading(true);
    const endpoint = cameraActive ? '/api/camera/stop' : '/api/camera/start';
    try {
      const res = await fetch(`${BACKEND_URL}${endpoint}`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setCameraActive(data.is_active);
      }
    } catch (e) {
      console.error('Camera toggle error:', e);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleAlerts = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/alerts/toggle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: !alertsEnabled })
      });
      if (res.ok) {
        const data = await res.json();
        setAlertsEnabled(data.alerts_enabled);
      }
    } catch (e) {
      console.error('Error toggling alerts:', e);
    }
  };

  const updateThreshold = async (val) => {
    setConfidenceThreshold(val);
    try {
      await fetch(`${BACKEND_URL}/api/alerts/threshold`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ threshold: val })
      });
    } catch (e) {
      console.error('Error updating threshold:', e);
    }
  };

  const triggerTestAlert = async () => {
    setIsTesting(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/alerts/test-trigger`, { method: 'POST' });
      if (res.ok) {
        fetchHistory();
      }
    } catch (e) {
      console.error('Error triggering test alert:', e);
    } finally {
      setIsTesting(false);
    }
  };

  const verifyEvent = async (id, status) => {
    try {
      await fetch(`${BACKEND_URL}/api/history/${id}/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ human_verification: status })
      });
      fetchHistory();
    } catch (e) {
      console.error('Verification update failed:', e);
    }
  };

  const clearHistory = async () => {
    if (window.confirm('Clear all logged detection records from local SQLite database?')) {
      try {
        await fetch(`${BACKEND_URL}/api/history`, { method: 'DELETE' });
        setHistory([]);
      } catch (e) {
        console.error('Clear history failed:', e);
      }
    }
  };

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '24px 20px' }}>
      {/* Header */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '26px' }}>🛡️</span>
            <h1 style={{ fontSize: '22px', fontWeight: '700', letterSpacing: '-0.02em' }}>
              Wearable AI Security Assistant
            </h1>
            <span style={{
              fontSize: '11px',
              padding: '2px 8px',
              borderRadius: '4px',
              backgroundColor: 'rgba(6,182,212,0.15)',
              color: 'var(--accent-cyan)',
              border: '1px solid rgba(6,182,212,0.3)',
              fontWeight: '600'
            }}>
              OFFICER HUD v1.0
            </span>
          </div>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>
            Real-Time Edge Visual Threat Detection & Situational Awareness for Patrol Officers
          </p>
        </div>
      </header>

      {/* Main Control & Telemetry Bar */}
      <SystemStatus
        telemetry={telemetry}
        cameraActive={cameraActive}
        alertsEnabled={alertsEnabled}
        confidenceThreshold={confidenceThreshold}
        onToggleCamera={toggleCamera}
        onToggleAlerts={toggleAlerts}
        onChangeThreshold={updateThreshold}
        isLoading={isLoading}
      />

      {/* Primary Video Feed & Alert Side Panel */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '20px' }}>
        <div>
          <CameraFeed
            cameraActive={cameraActive}
            telemetry={telemetry}
            hasActiveThreat={hasActiveThreat}
          />
          <DetectionOverlay
            currentThreat={currentThreat}
            hasActiveThreat={hasActiveThreat}
          />
        </div>

        <div>
          <AlertPanel
            alertsEnabled={alertsEnabled}
            onTriggerTestAlert={triggerTestAlert}
            isTesting={isTesting}
          />
        </div>
      </div>

      {/* Local Detection History */}
      <DetectionHistory
        history={history}
        onVerifyEvent={verifyEvent}
        onClearHistory={clearHistory}
        onRefresh={fetchHistory}
      />
    </div>
  );
}
