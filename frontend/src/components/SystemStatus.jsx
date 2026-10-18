import React from 'react';

export default function SystemStatus({
  telemetry,
  cameraActive,
  alertsEnabled,
  confidenceThreshold,
  onToggleCamera,
  onToggleAlerts,
  onChangeThreshold,
  isLoading
}) {
  return (
    <div className="glass-panel" style={{ padding: '20px', marginBottom: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        
        {/* Status Indicators */}
        <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
          <div>
            <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.05em' }}>
              System Status
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
              <span style={{
                width: '10px',
                height: '10px',
                borderRadius: '50%',
                backgroundColor: cameraActive ? 'var(--accent-green)' : 'var(--accent-warning)',
                boxShadow: cameraActive ? '0 0 10px var(--accent-green)' : 'none'
              }} />
              <strong style={{ fontSize: '15px' }}>{cameraActive ? 'ACTIVE' : 'STANDBY'}</strong>
            </div>
          </div>

          <div>
            <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.05em' }}>
              Camera Link
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
              <span style={{
                width: '10px',
                height: '10px',
                borderRadius: '50%',
                backgroundColor: cameraActive ? 'var(--accent-cyan)' : 'var(--text-dim)'
              }} />
              <strong style={{ fontSize: '15px' }}>{cameraActive ? 'CONNECTED' : 'DISCONNECTED'}</strong>
            </div>
          </div>

          <div>
            <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.05em' }}>
              AI Vision Engine
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
              <span style={{
                width: '10px',
                height: '10px',
                borderRadius: '50%',
                backgroundColor: 'var(--accent-green)'
              }} />
              <strong style={{ fontSize: '15px' }}>YOLO RUNNING</strong>
            </div>
          </div>

          <div>
            <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.05em' }}>
              Resolution
            </div>
            <div className="mono" style={{ fontSize: '15px', color: 'var(--accent-green)', marginTop: '4px' }}>
              {telemetry.camera_resolution || '2560x1440 (2K)'}
            </div>
          </div>

          <div>
            <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.05em' }}>
              Telemetry Speed
            </div>
            <div className="mono" style={{ fontSize: '15px', color: 'var(--accent-cyan)', marginTop: '4px' }}>
              {telemetry.camera_fps ? `${telemetry.camera_fps} FPS` : '60.0 FPS'}
            </div>
          </div>
        </div>

        {/* Interactive Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
          
          {/* Confidence Slider */}
          <div style={{ display: 'flex', flexDirection: 'column', minWidth: '170px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-muted)' }}>
              <span>Confidence Gate:</span>
              <span className="mono" style={{ color: 'var(--accent-cyan)', fontWeight: 'bold' }}>
                {Math.round(confidenceThreshold * 100)}%
              </span>
            </div>
            <input
              type="range"
              min="0.30"
              max="0.95"
              step="0.05"
              value={confidenceThreshold}
              onChange={(e) => onChangeThreshold(parseFloat(e.target.value))}
              style={{ marginTop: '6px', cursor: 'pointer' }}
            />
          </div>

          {/* Alert Toggle Button */}
          <button
            onClick={onToggleAlerts}
            style={{
              padding: '8px 16px',
              borderRadius: '8px',
              fontWeight: '600',
              fontSize: '13px',
              backgroundColor: alertsEnabled ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
              color: alertsEnabled ? 'var(--accent-green)' : 'var(--accent-danger)',
              border: `1px solid ${alertsEnabled ? 'var(--accent-green)' : 'var(--accent-danger)'}`
            }}
          >
            {alertsEnabled ? '🔊 Audio Alerts: ON' : '🔇 Audio Alerts: OFF'}
          </button>

          {/* Start / Stop Camera Button */}
          <button
            onClick={onToggleCamera}
            disabled={isLoading}
            style={{
              padding: '9px 20px',
              borderRadius: '8px',
              fontWeight: '600',
              fontSize: '14px',
              backgroundColor: cameraActive ? 'var(--accent-danger)' : 'var(--accent-cyan)',
              color: '#ffffff',
              boxShadow: cameraActive ? '0 0 15px var(--accent-danger-glow)' : '0 0 15px rgba(6, 182, 212, 0.35)',
              opacity: isLoading ? 0.7 : 1
            }}
          >
            {isLoading ? 'Processing...' : cameraActive ? '⏹ Stop Camera' : '▶ Start Camera'}
          </button>

        </div>
      </div>
    </div>
  );
}
