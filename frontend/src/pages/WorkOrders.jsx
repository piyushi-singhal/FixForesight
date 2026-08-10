import React from 'react';
import { CheckCircle2 } from 'lucide-react';
import { getMachineName } from '../utils/helpers';

export default function WorkOrders({ workOrders, workOrdersLoading, onMachineSelect }) {
  const getAssignedTechnician = (woId) => {
    const techs = [
      "Marcus Vance",
      "Dave Miller",
      "Elena Rostova",
      "Carlos Mendez",
      "Sarah Jenkins"
    ];
    return techs[woId % techs.length];
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <h2>Work Orders Tracking Directory</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '4px' }}>
          Authorized maintenance schedules, technician assignments, and job completion statuses.
        </p>
      </div>

      {workOrdersLoading && workOrders.length === 0 ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><div className="spinner"></div></div>
      ) : workOrders.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
          <CheckCircle2 size={36} className="text-success" style={{ marginBottom: '12px', marginInline: 'auto' }} />
          <h3>No Active Work Orders</h3>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>There are currently no scheduled corrective work orders in queue.</p>
        </div>
      ) : (
        <div className="glass-card">
          <h3 className="card-title">Mitigation Tasks Ledger</h3>
          <div className="table-responsive" style={{ overflowX: 'auto', marginTop: '10px' }}>
            <table className="parts-table" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr>
                  <th>Work Order ID</th>
                  <th>Machine ID</th>
                  <th>Assigned Technician</th>
                  <th>Status</th>
                  <th>Created At</th>
                  <th>Completed At</th>
                </tr>
              </thead>
              <tbody>
                {workOrders.map((wo) => {
                  const statusClass = wo.status === 'completed' ? 'healthy' : wo.status === 'in_progress' ? 'warning' : 'danger';
                  return (
                    <tr key={wo.id}>
                      <td><strong>WO-{String(wo.id).padStart(3, '0')}</strong></td>
                      <td>
                        <span 
                          onClick={() => onMachineSelect(wo.machine_id)}
                          style={{ 
                            cursor: 'pointer', 
                            textDecoration: 'underline', 
                            color: 'var(--primary)',
                            fontWeight: 600
                          }}
                        >
                          {wo.machine_id}
                        </span>
                        {" "}({getMachineName(wo.machine_id)})
                      </td>
                      <td>{getAssignedTechnician(wo.id)}</td>
                      <td>
                        <span className={`machine-prob-badge ${statusClass}`}>
                          {wo.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td>{new Date(wo.created_at).toLocaleString()}</td>
                      <td>{wo.completed_at ? new Date(wo.completed_at).toLocaleString() : '—'}</td>
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
