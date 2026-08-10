import React from 'react';
import { AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function Alerts({ alerts, alertsLoading, onMachineSelect }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <h2>System Notification Alerts</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '4px' }}>
          Real-time incident alert logs triggered by predictive maintenance thresholds.
        </p>
      </div>

      {alertsLoading && alerts.length === 0 ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><div className="spinner"></div></div>
      ) : alerts.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
          <CheckCircle2 size={36} className="text-success" style={{ marginBottom: '12px', marginInline: 'auto' }} />
          <h3>No Active Alerts</h3>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>There are no active critical machine threshold notifications.</p>
        </div>
      ) : (
        <div className="glass-card">
          <h3 className="card-title">Alert Notifications Index</h3>
          <div className="table-responsive" style={{ overflowX: 'auto', marginTop: '10px' }}>
            <table className="parts-table" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr>
                  <th>Alert ID</th>
                  <th>Machine ID</th>
                  <th>Severity</th>
                  <th>Message Details</th>
                  <th>Trigger Time</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((a) => {
                  const sevLower = a.severity.toLowerCase();
                  const badgeClass = sevLower === 'critical' ? 'danger' : sevLower === 'warning' ? 'warning' : 'healthy';
                  return (
                    <tr 
                      key={a.alert_id}
                      onClick={() => onMachineSelect(a.machine_id)}
                      className="clickable-row"
                      style={{ cursor: 'pointer' }}
                    >
                      <td><strong>ALT-{String(a.alert_id).padStart(3, '0')}</strong></td>
                      <td><strong>{a.machine_id}</strong></td>
                      <td>
                        <span className={`machine-prob-badge ${badgeClass}`}>
                          {a.severity}
                        </span>
                      </td>
                      <td style={{ fontSize: '12px', maxWidth: '400px', whiteSpace: 'normal', wordBreak: 'break-word' }}>
                        {a.message}
                      </td>
                      <td>{new Date(a.created_at).toLocaleString()}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
