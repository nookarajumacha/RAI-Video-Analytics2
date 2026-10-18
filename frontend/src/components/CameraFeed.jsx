import React from 'react';

export default function CameraFeed({ cameraActive, telemetry, hasActiveThreat }) {
  return (
    <div
      className={`glass-panel ${hasActiveThreat ? 'threat-active-pulse' : ''}`}
      style={{
        position: 'relative',
        width: '100%',
        aspectRatio: '16/9',
        overflow: 'hidden',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#050811'
      }}
    >
      {cameraActive ? (
        <img
          src="http://127.0.0.1:8000/api/camera/stream"
          alt="Live Security Camera Stream"
          style={{ width: '100%', height: '100%', objectFit: 'contain' }}
          onError={(e) => {
            console.debug('Camera stream frame error, retrying...');
          }}
        />
      ) : (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📷</div>
          <h3 style={{ fontSize: '18px', color: 'var(--text-main)', marginBottom: '8px' }}>
            Camera Stream Standby
          </h3>
          <p style={{ fontSize: '14px', maxWidth: '380px', margin: '0 auto' }}>
            Click <strong>"Start Camera"</strong> in the top control panel to initialize the live optical sensor and AI threat detector.
          </p>
        </div>
      )}

      {/* Live HUD Badges */}
      {cameraActive && (
        <div style={{
          position: 'absolute',
          top: '16px',
          left: '16px',
          display: 'flex',
          gap: '8px',
          zIndex: 10
        }}>
          <span style={{
            padding: '4px 10px',
            borderRadius: '4px',
            backgroundColor: 'rgba(0,0,0,0.7)',
            backdropFilter: 'blur(6px)',
            color: 'var(--accent-danger)',
            fontSize: '11px',
            fontWeight: 'bold',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--accent-danger)' }} />
            LIVE FEED
          </span>
          <span className="mono" style={{
            padding: '4px 10px',
            borderRadius: '4px',
            backgroundColor: 'rgba(0,0,0,0.7)',
            backdropFilter: 'blur(6px)',
            color: 'var(--accent-green)',
            fontSize: '11px',
            fontWeight: '600'
          }}>
            {telemetry.camera_resolution ? `${telemetry.camera_resolution} (2K)` : '2560x1440 (2K)'}
          </span>
          <span className="mono" style={{
            padding: '4px 10px',
            borderRadius: '4px',
            backgroundColor: 'rgba(0,0,0,0.7)',
            backdropFilter: 'blur(6px)',
            color: 'var(--accent-cyan)',
            fontSize: '11px'
          }}>
            {telemetry.camera_fps ? `${telemetry.camera_fps} FPS` : '60 FPS'}
          </span>
        </div>
      )}

      {/* Threat Active Banner inside Stream */}
      {hasActiveThreat && (
        <div style={{
          position: 'absolute',
          top: '16px',
          right: '16px',
          padding: '6px 14px',
          borderRadius: '4px',
          backgroundColor: 'var(--accent-danger)',
          color: '#ffffff',
          fontWeight: 'bold',
          fontSize: '12px',
          letterSpacing: '0.05em',
          boxShadow: '0 0 15px var(--accent-danger-glow)',
          zIndex: 10
        }}>
          ⚠️ POTENTIAL THREAT IN VIEW
        </div>
      )}
    </div>
  );
}
