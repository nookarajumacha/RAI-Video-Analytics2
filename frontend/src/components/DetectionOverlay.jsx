import React from 'react';

export default function DetectionOverlay({ currentThreat, hasActiveThreat }) {
  return (
    <div className="glass-panel" style={{ padding: '20px', marginTop: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
        <h3 style={{ fontSize: '15px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Current Status & Threat Assessment
        </h3>
        <span style={{
          padding: '3px 10px',
          borderRadius: '4px',
          fontSize: '11px',
          fontWeight: 'bold',
          backgroundColor: hasActiveThreat ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.15)',
          color: hasActiveThreat ? 'var(--accent-danger)' : 'var(--accent-green)',
          border: `1px solid ${hasActiveThreat ? 'var(--accent-danger)' : 'var(--accent-green)'}`
        }}>
          {hasActiveThreat ? 'THREAT IDENTIFIED' : 'CLEAR'}
        </span>
      </div>

      {hasActiveThreat && currentThreat ? (
        <div style={{
          backgroundColor: 'rgba(239, 68, 68, 0.08)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '8px',
          padding: '16px'
        }}>
          <div style={{ color: 'var(--accent-danger)', fontWeight: 'bold', fontSize: '18px', marginBottom: '12px' }}>
            ⚠️ POTENTIAL THREAT DETECTED
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px' }}>
            <div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Object Classification:</div>
              <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#ffffff' }}>
                {currentThreat.display_name || currentThreat.object_type?.toUpperCase()}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Confidence Score:</div>
              <div className="mono" style={{ fontSize: '16px', fontWeight: 'bold', color: 'var(--accent-cyan)' }}>
                {Math.round((currentThreat.confidence || 0) * 100)}%
              </div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Detection Time:</div>
              <div className="mono" style={{ fontSize: '15px', color: 'var(--text-main)' }}>
                {new Date(currentThreat.timestamp).toLocaleTimeString()}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Mandatory Action:</div>
              <div style={{ fontSize: '14px', fontWeight: 'bold', color: 'var(--accent-warning)' }}>
                Human verification required
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div style={{
          padding: '18px',
          backgroundColor: 'rgba(16, 185, 129, 0.05)',
          borderRadius: '8px',
          border: '1px solid rgba(16, 185, 129, 0.2)',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <span style={{ fontSize: '20px' }}>🛡️</span>
          <div>
            <div style={{ fontWeight: '600', color: 'var(--accent-green)' }}>
              No potential threat detected
            </div>
            <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Optical sensors active. Monitoring visual horizon for firearms and edged weapons.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
