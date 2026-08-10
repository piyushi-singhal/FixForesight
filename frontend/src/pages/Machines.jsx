import React from 'react';
import { getMachineStatus, getMachineName, getMachineModel, getMachineLocation } from '../utils/helpers';

export default function Machines({ machines, machinesLoading, activeId, onMachineSelect }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      <div>
        <h2>Monitored Assets Directory</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '4px' }}>
          Fleet-wide hardware inventory, models, deployment locations, and operational statuses.
        </p>
      </div>

      {/* Master Machines Table */}
      <div className="glass-card">
        <h3 className="card-title">Assets Master Directory</h3>
        <div className="table-responsive" style={{ overflowX: 'auto', marginTop: '10px' }}>
          <table className="parts-table" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr>
                <th>Machine ID</th>
                <th>Machine Name</th>
                <th>Model</th>
                <th>Location</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {machinesLoading && machines.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', padding: '20px' }}>
                    <div className="spinner" style={{ margin: '0 auto' }}></div>
                  </td>
                </tr>
              ) : (
                machines.map((m) => {
                  const status = getMachineStatus(m.failure_probability);
                  const riskLevel = status === 'Critical' ? 'danger' : status === 'Warning' ? 'warning' : 'healthy';
                  const isActive = m.machine_id === activeId;
                  
                  return (
                    <tr 
                      key={m.machine_id}
                      onClick={() => onMachineSelect(m.machine_id)}
                      className={`clickable-row ${isActive ? 'active-row' : ''}`}
                      style={{ 
                        cursor: 'pointer',
                        background: isActive ? 'rgba(255,255,255,0.06)' : 'transparent',
                        transition: 'background 0.2s'
                      }}
                    >
                      <td><strong>{m.machine_id}</strong></td>
                      <td>{getMachineName(m.machine_id)}</td>
                      <td>{getMachineModel(m.machine_id)}</td>
                      <td>{getMachineLocation(m.machine_id)}</td>
                      <td>
                        <span className={`machine-prob-badge ${riskLevel}`}>
                          {status}
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
