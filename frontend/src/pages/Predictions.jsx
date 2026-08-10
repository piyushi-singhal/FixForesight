import React from 'react';
import { getRiskClass } from '../utils/helpers';

export default function Predictions({ predictions, predictionsLoading, onMachineSelect }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <h2>Predictive Maintenance Analysis (ML model)</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '4px' }}>
          Machine learning models continuously analyze IoT telemetry streams to forecast failure events.
        </p>
      </div>

      {predictionsLoading && predictions.length === 0 ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><div className="spinner"></div></div>
      ) : (
        <div className="glass-card">
          <h3 className="card-title">Failure Prediction Index</h3>
          <div className="table-responsive" style={{ overflowX: 'auto', marginTop: '10px' }}>
            <table className="parts-table" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr>
                  <th>Machine ID</th>
                  <th>Air Temp</th>
                  <th>Process Temp</th>
                  <th>Rotational Speed</th>
                  <th>Torque</th>
                  <th>Tool Wear</th>
                  <th>Failure Probability</th>
                  <th>Predicted Failure</th>
                </tr>
              </thead>
              <tbody>
                {predictions.map((p) => {
                  const probPct = Math.round(p.failure_probability * 100);
                  const riskClass = getRiskClass(probPct);
                  
                  return (
                    <tr 
                      key={p.machine_id}
                      onClick={() => onMachineSelect(p.machine_id)}
                      className="clickable-row"
                      style={{ cursor: 'pointer' }}
                    >
                      <td><strong>{p.machine_id}</strong></td>
                      <td>{p.air_temperature ? `${p.air_temperature.toFixed(1)} K` : 'N/A'}</td>
                      <td>{p.process_temperature ? `${p.process_temperature.toFixed(1)} K` : 'N/A'}</td>
                      <td>{p.rotational_speed ? `${p.rotational_speed} RPM` : 'N/A'}</td>
                      <td>{p.torque ? `${p.torque.toFixed(1)} Nm` : 'N/A'}</td>
                      <td>{p.tool_wear ? `${p.tool_wear.toFixed(1)} min` : 'N/A'}</td>
                      <td style={{ color: `var(--${riskClass})`, fontWeight: 700 }}>
                        {probPct}%
                      </td>
                      <td>
                        <span className={`machine-prob-badge ${riskClass}`}>
                          {p.predicted_failure}
                        </span>
                      </td>
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
