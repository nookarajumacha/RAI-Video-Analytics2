import React from 'react';

export default function AlertPanel({ alertsEnabled, onTriggerTestAlert, isTesting }) {
  return (
    <div className="glass-panel" style={{ padding: '20px', height: '100%' }}>
      <h3 style={{ fontSize: '15px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '16px' }}>
        Alert Dispatch & Protocol
      </h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '12px 14px',
          backgroundColor: 'rgba(0,0,0,0.25)',
          borderRadius: '8px'
        }}>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 'bold' }}>Acoustic Alert Channel</div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Text-to-Speech Earpiece Dispatch</div>
          </div>
          <span style={{
            fontSize: '12px',
            fontWeight: 'bold',
            color: alertsEnabled ? 'var(--accent-green)' : 'var(--text-dim)'
          }}>
            {alertsEnabled ? 'ACTIVE (3s Cooldown)' : 'MUTED'}
          </span>
        </div>

        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '12px 14px',
          backgroundColor: 'rgba(0,0,0,0.25)',
          borderRadius: '8px'
        }}>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 'bold' }}>Visual Heads-Up Overlay</div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Red HUD Perimeter & Bounding Box</div>
          </div>
          <span style={{ fontSize: '12px', fontWeight: 'bold', color: 'var(--accent-green)' }}>
            ENABLED
          </span>
        </div>

        <button
          onClick={onTriggerTestAlert}
          disabled={isTesting}
          style={{
            padding: '10px 16px',
            borderRadius: '8px',
            backgroundColor: 'rgba(245, 158, 11, 0.15)',
            border: '1px solid var(--accent-warning)',
            color: 'var(--accent-warning)',
            fontWeight: '600',
            fontSize: '13px',
            marginTop: '6px'
          }}
        >
          {isTesting ? 'Dispatching...' : '⚡ Test Alert & Alarm Siren'}
        </button>

        {/* Privacy & Safety Note */}
        <div style={{
          marginTop: '10px',
          padding: '12px',
          borderRadius: '8px',
          backgroundColor: 'rgba(6, 182, 212, 0.05)',
          border: '1px solid rgba(6, 182, 212, 0.2)',
          fontSize: '11px',
          color: 'var(--text-muted)',
          lineHeight: '1.5'
        }}>
          <strong style={{ color: 'var(--accent-cyan)' }}>🔒 PRIVACY & ETHICAL COMPLIANCE:</strong>
          <br />
          Facial recognition is permanently disabled. No biometric records are stored. All detections represent situational guidance and require human confirmation.
        </div>
      </div>
    </div>
  );
}
