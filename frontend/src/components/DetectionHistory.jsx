import React from 'react';

export default function DetectionHistory({ history, onVerifyEvent, onClearHistory, onRefresh }) {
  return (
    <div className="glass-panel" style={{ padding: '20px', marginTop: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <h3 style={{ fontSize: '15px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Local Detection Event Audit History (SQLite)
          </h3>
          <p style={{ fontSize: '12px', color: 'var(--text-dim)', marginTop: '2px' }}>
            Logged on-device records for forensic review and officer verification.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={onRefresh}
            style={{
              padding: '6px 12px',
              borderRadius: '6px',
              fontSize: '12px',
              backgroundColor: 'rgba(255,255,255,0.06)',
              color: 'var(--text-main)',
              border: '1px solid var(--border-color)'
            }}
          >
            ↻ Refresh
          </button>
          <button
            onClick={onClearHistory}
            style={{
              padding: '6px 12px',
              borderRadius: '6px',
              fontSize: '12px',
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              color: 'var(--accent-danger)',
              border: '1px solid rgba(239, 68, 68, 0.3)'
            }}
          >
            🗑 Clear History
          </button>
        </div>
      </div>

      {history.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)', fontSize: '13px' }}>
          No detection events logged yet. Detections will appear here in real-time.
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', fontSize: '11px', textTransform: 'uppercase' }}>
                <th style={{ padding: '10px 12px' }}>ID</th>
                <th style={{ padding: '10px 12px' }}>Timestamp</th>
                <th style={{ padding: '10px 12px' }}>Object Type</th>
                <th style={{ padding: '10px 12px' }}>Confidence</th>
                <th style={{ padding: '10px 12px' }}>Alert Status</th>
                <th style={{ padding: '10px 12px' }}>Human Verification</th>
                <th style={{ padding: '10px 12px', textAlign: 'right' }}>Officer Action</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item) => (
                <tr key={item.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                  <td className="mono" style={{ padding: '12px', color: 'var(--text-dim)' }}>
                    #{item.id}
                  </td>
                  <td className="mono" style={{ padding: '12px' }}>
                    {item.timestamp ? new Date(item.timestamp).toLocaleTimeString() : 'N/A'}
                  </td>
                  <td style={{ padding: '12px', fontWeight: '600' }}>
                    <span style={{
                      color: item.object_type === 'firearm' ? 'var(--accent-danger)' : 'var(--accent-warning)'
                    }}>
                      {item.object_type === 'firearm' ? '🔫 Firearm' : '🔪 Knife'}
                    </span>
                  </td>
                  <td className="mono" style={{ padding: '12px', color: 'var(--accent-cyan)' }}>
                    {Math.round(item.confidence * 100)}%
                  </td>
                  <td style={{ padding: '12px' }}>
                    <span style={{
                      fontSize: '11px',
                      padding: '3px 8px',
                      borderRadius: '4px',
                      backgroundColor: item.alert_status === 'TRIGGERED' ? 'rgba(239,68,68,0.15)' : 'rgba(107,114,128,0.2)',
                      color: item.alert_status === 'TRIGGERED' ? 'var(--accent-danger)' : 'var(--text-muted)'
                    }}>
                      {item.alert_status}
                    </span>
                  </td>
                  <td style={{ padding: '12px' }}>
                    <span style={{
                      fontSize: '11px',
                      fontWeight: 'bold',
                      color: item.human_verification === 'CONFIRMED' ? 'var(--accent-danger)' :
                             item.human_verification === 'FALSE_ALARM' ? 'var(--accent-green)' : 'var(--accent-warning)'
                    }}>
                      {item.human_verification}
                    </span>
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right' }}>
                    {item.human_verification === 'PENDING' ? (
                      <div style={{ display: 'inline-flex', gap: '6px' }}>
                        <button
                          onClick={() => onVerifyEvent(item.id, 'CONFIRMED')}
                          style={{
                            padding: '4px 10px',
                            borderRadius: '4px',
                            fontSize: '11px',
                            fontWeight: '600',
                            backgroundColor: 'rgba(239,68,68,0.2)',
                            color: 'var(--accent-danger)',
                            border: '1px solid var(--accent-danger)'
                          }}
                        >
                          Confirm Threat
                        </button>
                        <button
                          onClick={() => onVerifyEvent(item.id, 'FALSE_ALARM')}
                          style={{
                            padding: '4px 10px',
                            borderRadius: '4px',
                            fontSize: '11px',
                            fontWeight: '600',
                            backgroundColor: 'rgba(16,185,129,0.2)',
                            color: 'var(--accent-green)',
                            border: '1px solid var(--accent-green)'
                          }}
                        >
                          False Alarm
                        </button>
                      </div>
                    ) : (
                      <span style={{ fontSize: '11px', color: 'var(--text-dim)' }}>
                        Resolved
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
