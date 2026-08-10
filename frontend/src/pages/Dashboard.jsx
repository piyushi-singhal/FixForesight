import React from 'react';
import { Cpu, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';
import { getMachineStatus } from '../utils/helpers';

export default function Dashboard({ machines, onMachineSelect }) {
  const totalCount = machines.length;
  const healthyCount = machines.filter(m => getMachineStatus(m.failure_probability) === 'Healthy').length;
  const warningCount = machines.filter(m => getMachineStatus(m.failure_probability) === 'Warning').length;
  const criticalCount = machines.filter(m => getMachineStatus(m.failure_probability) === 'Critical').length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      <div>
        <h2 style={{ fontSize: '24px', fontWeight: 700 }}>Factory Telemetry Overview</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '4px' }}>
          Real-time status monitor of predictive and prescriptive IoT workflows.
        </p>
      </div>

      {/* KPIs row */}
      <div className="dashboard-metrics-grid">
        <div className="glass-card metric-card">
          <div className="metric-icon-box" style={{ background: 'var(--primary-glow)', color: 'var(--primary)' }}>
            <Cpu size={20} />
          </div>
          <div>
            <div className="metric-value">{totalCount}</div>
            <div className="metric-label">Monitored Units</div>
          </div>
        </div>
        <div className="glass-card metric-card">
          <div className="metric-icon-box healthy">
            <CheckCircle2 size={20} />
          </div>
          <div>
            <div className="metric-value">{healthyCount}</div>
            <div className="metric-label">Healthy Units</div>
          </div>
        </div>
        <div className="glass-card metric-card">
          <div className="metric-icon-box warning">
            <AlertTriangle size={20} />
          </div>
          <div>
            <div className="metric-value">{warningCount}</div>
            <div className="metric-label">Warnings Active</div>
          </div>
        </div>
        <div className="glass-card metric-card">
          <div className="metric-icon-box danger">
            <XCircle size={20} />
          </div>
          <div>
            <div className="metric-value">{criticalCount}</div>
            <div className="metric-label">Critical Status</div>
          </div>
        </div>
      </div>

      {/* Second Row: Risk and Failure Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '28px' }}>
        <div className="glass-card">
          <h3 className="card-title">Risk Distribution Chart</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '11px', marginTop: '2px' }}>
            Breakdown of machines by active operational risk category.
          </p>
          <div style={{ display: 'flex', height: '18px', borderRadius: '9px', overflow: 'hidden', background: 'rgba(255,255,255,0.05)', marginTop: '24px' }}>
            {totalCount > 0 ? (
              <>
                {healthyCount > 0 && <div style={{ width: `${(healthyCount / totalCount) * 100}%`, background: 'var(--success)', transition: 'width 0.3s' }}></div>}
                {warningCount > 0 && <div style={{ width: `${(warningCount / totalCount) * 100}%`, background: 'var(--warning)', transition: 'width 0.3s' }}></div>}
                {criticalCount > 0 && <div style={{ width: `${(criticalCount / totalCount) * 100}%`, background: 'var(--danger)', transition: 'width 0.3s' }}></div>}
              </>
            ) : (
              <div style={{ width: '100%', background: 'rgba(255,255,255,0.05)' }}></div>
            )}
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-around', marginTop: '20px', flexWrap: 'wrap', gap: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}>
              <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: 'var(--success)' }}></span>
              <span>Healthy: <strong>{healthyCount}</strong> ({totalCount ? Math.round((healthyCount/totalCount)*100) : 0}%)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}>
              <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: 'var(--warning)' }}></span>
              <span>Warning: <strong>{warningCount}</strong> ({totalCount ? Math.round((warningCount/totalCount)*100) : 0}%)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}>
              <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: 'var(--danger)' }}></span>
              <span>Critical: <strong>{criticalCount}</strong> ({totalCount ? Math.round((criticalCount/totalCount)*100) : 0}%)</span>
            </div>
          </div>
        </div>

        <div className="glass-card">
          <h3 className="card-title">Failure Distribution Chart</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '11px', marginTop: '2px' }}>
            Distribution of active failure modes predicted by ML models.
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '16px' }}>
            {(() => {
              const failureCounts = {};
              machines.forEach(m => {
                const mode = m.predicted_failure || 'Normal Operation';
                failureCounts[mode] = (failureCounts[mode] || 0) + 1;
              });
              const failureData = Object.entries(failureCounts).map(([mode, count]) => ({
                mode,
                count,
                pct: totalCount ? Math.round((count / totalCount) * 100) : 0
              })).sort((a, b) => b.count - a.count);

              if (failureData.length === 0) {
                return <p style={{ fontSize: '12px', color: 'var(--text-muted)', textAlign: 'center' }}>No predictions available</p>;
              }

              return failureData.map(f => (
                <div key={f.mode} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>{f.mode}</span>
                    <strong>{f.count} unit(s) ({f.pct}%)</strong>
                  </div>
                  <div className="prediction-val-bar" style={{ height: '6px' }}>
                    <div 
                      className="prediction-val-fill" 
                      style={{ 
                        width: `${f.pct}%`, 
                        background: f.mode === 'Normal Operation' ? 'var(--success)' : 'var(--primary)',
                        height: '100%',
                        borderRadius: '3px'
                      }}
                    ></div>
                  </div>
                </div>
              ));
            })()}
          </div>
        </div>
      </div>

      {/* Third Row: Critical Machines Table */}
      <div className="glass-card">
        <h3 className="card-title">Critical Machines Table</h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '11px', marginTop: '2px', marginBottom: '14px' }}>
          List of machines currently flagged as Critical based on predictive failure risk.
        </p>
        <div className="table-responsive" style={{ overflowX: 'auto' }}>
          <table className="parts-table" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr>
                <th>Machine ID</th>
                <th>Failure Probability</th>
                <th>Risk Level</th>
                <th>Recommendation</th>
              </tr>
            </thead>
            <tbody>
              {(() => {
                const criticalMachines = machines.filter(m => getMachineStatus(m.failure_probability) === 'Critical');
                if (criticalMachines.length === 0) {
                  return (
                    <tr>
                      <td colSpan={4} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '28px' }}>
                        <CheckCircle2 size={24} className="text-success" style={{ margin: '0 auto 8px', display: 'block' }} />
                        All units operating within safe parameters. No critical machines detected.
                      </td>
                    </tr>
                  );
                }
                return criticalMachines.map(m => (
                  <tr 
                    key={m.machine_id}
                    onClick={() => onMachineSelect(m.machine_id)}
                    className="clickable-row"
                    style={{ cursor: 'pointer' }}
                  >
                    <td><strong>{m.machine_id}</strong></td>
                    <td style={{ color: 'var(--danger)', fontWeight: 700 }}>
                      {Math.round(m.failure_probability * 100)}%
                    </td>
                    <td>
                      <span className="machine-prob-badge danger">
                        Critical
                      </span>
                    </td>
                    <td style={{ fontSize: '12px' }}>{m.recommendation}</td>
                  </tr>
                ));
              })()}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
