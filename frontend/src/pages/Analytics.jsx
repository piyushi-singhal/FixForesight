import React from 'react';
import { getMachineStatus, getMachineName } from '../utils/helpers';

export default function Analytics({ machines, recommendations }) {
  const totalM = machines.length || 1;
  const avgAirTemp = (machines.reduce((sum, m) => sum + (m.air_temperature || 0), 0) / totalM).toFixed(1);
  const avgProcTemp = (machines.reduce((sum, m) => sum + (m.process_temperature || 0), 0) / totalM).toFixed(1);
  const avgSpeed = (machines.reduce((sum, m) => sum + (m.rotational_speed || 0), 0) / totalM).toFixed(0);
  const avgTorque = (machines.reduce((sum, m) => sum + (m.torque || 0), 0) / totalM).toFixed(1);
  const avgToolWear = (machines.reduce((sum, m) => sum + (m.tool_wear || 0), 0) / totalM).toFixed(1);

  // Calculations for charts
  const probDistribution = {
    '0-20%': 0,
    '20-40%': 0,
    '40-60%': 0,
    '60-80%': 0,
    '80-100%': 0
  };
  const statusCounts = {
    'Healthy': 0,
    'Warning': 0,
    'Critical': 0
  };
  const priorityCounts = {
    'Low': 0,
    'Medium': 0,
    'High': 0,
    'Critical': 0
  };

  machines.forEach(m => {
    const prob = m.failure_probability * 100;
    if (prob < 20) probDistribution['0-20%']++;
    else if (prob < 40) probDistribution['20-40%']++;
    else if (prob < 60) probDistribution['40-60%']++;
    else if (prob < 80) probDistribution['60-80%']++;
    else probDistribution['80-100%']++;

    const status = getMachineStatus(m.failure_probability);
    if (statusCounts[status] !== undefined) statusCounts[status]++;
  });

  recommendations.forEach(r => {
    const prio = r.priority || 'Low';
    if (priorityCounts[prio] !== undefined) priorityCounts[prio]++;
  });

  // Helper for rendering a progress bar row
  const renderBarRow = (label, count, total, colorClass, barColor) => {
    const pct = total > 0 ? Math.round((count / total) * 100) : 0;
    return (
      <div key={label} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-secondary)' }}>
          <span>{label}</span>
          <strong>{count} unit(s) ({pct}%)</strong>
        </div>
        <div className="prediction-val-bar" style={{ height: '6px' }}>
          <div 
            className="prediction-val-fill" 
            style={{ 
              width: `${pct}%`, 
              background: barColor || `var(--${colorClass})`,
              height: '100%',
              borderRadius: '3px'
            }}
          ></div>
        </div>
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div>
        <h2>System Performance Analytics</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '4px' }}>
          Fleet-wide diagnostic analytics, operational distributions, and hardware failure statistics.
        </p>
      </div>

      {/* Telemetry Averages Row */}
      <div className="glass-card">
        <h3 className="card-title">Plant Telemetry Averages</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '16px', marginTop: '10px' }}>
          <div style={{ background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '10px', border: '1px solid var(--border-glass)' }}>
            <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontWeight: 600 }}>AIR TEMPERATURE (AVG)</span>
            <div style={{ fontSize: '18px', fontWeight: 800, marginTop: '4px' }}>{avgAirTemp} K</div>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '10px', border: '1px solid var(--border-glass)' }}>
            <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontWeight: 600 }}>PROCESS TEMPERATURE (AVG)</span>
            <div style={{ fontSize: '18px', fontWeight: 800, marginTop: '4px' }}>{avgProcTemp} K</div>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '10px', border: '1px solid var(--border-glass)' }}>
            <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontWeight: 600 }}>ROTATIONAL SPEED (AVG)</span>
            <div style={{ fontSize: '18px', fontWeight: 800, marginTop: '4px' }}>{avgSpeed} RPM</div>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '10px', border: '1px solid var(--border-glass)' }}>
            <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontWeight: 600 }}>TORQUE (AVG)</span>
            <div style={{ fontSize: '18px', fontWeight: 800, marginTop: '4px' }}>{avgTorque} Nm</div>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '10px', border: '1px solid var(--border-glass)' }}>
            <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontWeight: 600 }}>TOOL WEAR (AVG)</span>
            <div style={{ fontSize: '18px', fontWeight: 800, marginTop: '4px' }}>{avgToolWear} min</div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
        
        {/* Failure Probability Distribution */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div>
            <h3 className="card-title">Failure Probability Distribution</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '11px', marginTop: '2px' }}>
              Machines segmented by active risk percentage.
            </p>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {Object.entries(probDistribution).map(([bucket, count]) => 
              renderBarRow(
                bucket, 
                count, 
                machines.length, 
                bucket === '80-100%' ? 'danger' : bucket === '60-80%' ? 'warning' : 'primary',
                bucket === '80-100%' ? 'var(--danger)' : bucket === '60-80%' ? 'var(--warning)' : 'var(--primary)'
              )
            )}
          </div>
        </div>

        {/* Machine Status */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div>
            <h3 className="card-title">Machine Status Splits</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '11px', marginTop: '2px' }}>
              Operational categorization count.
            </p>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {Object.entries(statusCounts).map(([status, count]) => {
              const color = status === 'Critical' ? 'var(--danger)' : status === 'Warning' ? 'var(--warning)' : 'var(--success)';
              return renderBarRow(status, count, machines.length, '', color);
            })}
          </div>
        </div>

        {/* Recommendation Priority */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div>
            <h3 className="card-title">Recommendation Priorities</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '11px', marginTop: '2px' }}>
              Urgency breakdown of active recommendations.
            </p>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {Object.entries(priorityCounts).map(([priority, count]) => {
              const color = priority === 'Critical' ? 'var(--danger)' : priority === 'High' ? 'var(--warning)' : priority === 'Medium' ? 'var(--primary)' : 'var(--text-muted)';
              return renderBarRow(priority, count, recommendations.length, '', color);
            })}
          </div>
        </div>

      </div>

      {/* Fleet Status Summary */}
      <div className="glass-card">
        <h3 className="card-title">Fleet Vitals Health Index</h3>
        <div style={{ overflowX: 'auto' }}>
          <table className="parts-table">
            <thead>
              <tr>
                <th>Machine ID</th>
                <th>Name</th>
                <th>Status</th>
                <th>Air Temp</th>
                <th>Proc Temp</th>
                <th>Speed</th>
                <th>Torque</th>
                <th>Tool Wear</th>
              </tr>
            </thead>
            <tbody>
              {machines.map((m) => (
                <tr key={m.machine_id}>
                  <td><strong>{m.machine_id}</strong></td>
                  <td>{getMachineName(m.machine_id)}</td>
                  <td>
                    <span className={`machine-prob-badge ${getMachineStatus(m.failure_probability) === 'Critical' ? 'danger' : getMachineStatus(m.failure_probability) === 'Warning' ? 'warning' : 'healthy'}`}>
                      {getMachineStatus(m.failure_probability)}
                    </span>
                  </td>
                  <td>{m.air_temperature.toFixed(1)} K</td>
                  <td>{m.process_temperature.toFixed(1)} K</td>
                  <td>{m.rotational_speed} RPM</td>
                  <td>{m.torque.toFixed(1)} Nm</td>
                  <td>{m.tool_wear.toFixed(1)} min</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
