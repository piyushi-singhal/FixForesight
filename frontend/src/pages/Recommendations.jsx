import React from 'react';
import { CheckCircle2 } from 'lucide-react';

export default function Recommendations({ recommendations, recsLoading, onMachineSelect }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <h2>Prescriptive Action Plans & Parts Logistics</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '4px' }}>
          Recommended maintenance mitigations matched against real-time warehouse inventory levels.
        </p>
      </div>

      {recsLoading && recommendations.length === 0 ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><div className="spinner"></div></div>
      ) : recommendations.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
          <CheckCircle2 size={36} className="text-success" style={{ marginBottom: '12px', marginInline: 'auto' }} />
          <h3>All Systems Operating Normally</h3>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>No active prescriptive repair recommendations found.</p>
        </div>
      ) : (
        <div className="glass-card">
          <h3 className="card-title">Mitigation Recommendations Directory</h3>
          <div className="table-responsive" style={{ overflowX: 'auto', marginTop: '10px' }}>
            <table className="parts-table" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr>
                  <th>Machine ID</th>
                  <th>Recommendation</th>
                  <th>Priority</th>
                  <th>Generated Time</th>
                </tr>
              </thead>
              <tbody>
                {recommendations.map((r) => (
                  <tr 
                    key={r.machine_id}
                    onClick={() => onMachineSelect(r.machine_id)}
                    className="clickable-row"
                    style={{ cursor: 'pointer' }}
                  >
                    <td><strong>{r.machine_id}</strong></td>
                    <td>{r.recommendation}</td>
                    <td>
                      <span className={`machine-prob-badge ${r.priority.toLowerCase() === 'critical' ? 'danger' : r.priority.toLowerCase() === 'high' ? 'warning' : 'healthy'}`}>
                        {r.priority}
                      </span>
                    </td>
                    <td>{new Date(r.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
