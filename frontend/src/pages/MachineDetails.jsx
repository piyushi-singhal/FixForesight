import React from 'react';
import { Clock, CheckCircle2 } from 'lucide-react';
import {
  getMachineName,
  getMachineModel,
  getMachineLocation,
  getMachineStatus,
  getRiskClass,
  isPointAnomaly,
  getSvgPathData
} from '../utils/helpers';

export default function MachineDetails({
  activeId,
  machines,
  detail,
  detailLoading,
  rec,
  recLoading,
  workOrders,
  submittingWorkOrder,
  activeTab,
  setActiveTab,
  onBack,
  onCreateWorkOrder
}) {
  if (!activeId) {
    return (
      <div className="glass-card" style={{ padding: '28px', textAlign: 'center' }}>
        <h3>No Asset Selected</h3>
        <p style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>Please select a machine from the Assets Directory.</p>
        <button onClick={onBack} className="btn-primary" style={{ marginTop: '16px', marginInline: 'auto' }}>
          Go to Assets Directory
        </button>
      </div>
    );
  }

  const machineObj = machines.find((m) => m.machine_id === activeId);
  const mName = getMachineName(activeId);
  const mModel = getMachineModel(activeId);
  const mLocation = getMachineLocation(activeId);
  
  const probPct = machineObj ? Math.round(machineObj.failure_probability * 100) : 5;
  const status = getMachineStatus(machineObj ? machineObj.failure_probability : 0.05);
  const riskLevel = status === 'Critical' ? 'danger' : status === 'Warning' ? 'warning' : 'healthy';

  // Sensor features
  const airTemp = machineObj ? machineObj.air_temperature : 300.0;
  const procTemp = machineObj ? machineObj.process_temperature : 310.0;
  const speed = machineObj ? machineObj.rotational_speed : 1500;
  const torque = machineObj ? machineObj.torque : 40.0;
  const toolWear = machineObj ? machineObj.tool_wear : 10.0;
  const regDate = machineObj && machineObj.created_at ? new Date(machineObj.created_at).toLocaleDateString() : 'N/A';

  // Recommendation state
  const machineRec = rec; 
  
  // Filter work orders for this machine
  const machineWorkOrders = workOrders.filter((wo) => wo.machine_id === activeId);

  // Dynamic warning indicators for progress bars
  const getVitalBarWidth = (key, val) => {
    if (key === 'air_temperature') return Math.min(100, Math.max(10, (val / 310.0) * 100));
    if (key === 'process_temperature') return Math.min(100, Math.max(10, (val / 320.0) * 100));
    if (key === 'rotational_speed') return Math.min(100, Math.max(10, (val / 2600.0) * 100));
    if (key === 'torque') return Math.min(100, Math.max(10, (val / 80.0) * 100));
    if (key === 'tool_wear') return Math.min(100, Math.max(10, (val / 240.0) * 100));
    return 10;
  };

  const trendData = detail ? getSvgPathData(detail.sensor_history, activeTab) : { path: '', area: '', points: [] };
  const currentRisk = detail && detail.prediction ? detail.prediction.failure_probability : 5;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* Header section with back button */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button 
            onClick={onBack} 
            className="status-badge" 
            style={{ cursor: 'pointer', border: '1px solid var(--border-glass)', outline: 'none', background: 'rgba(255,255,255,0.02)', padding: '8px 16px', borderRadius: '8px' }}
          >
            ← Back to Fleet Directory
          </button>
          <div>
            <h2 style={{ fontSize: '24px', fontWeight: 800 }}>{mName} ({activeId})</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '4px' }}>
              Asset Health Profile, IoT Telemetry Streams & Prescriptive Maintenance
            </p>
          </div>
        </div>
        <span className={`machine-prob-badge ${riskLevel}`} style={{ fontSize: '14px', padding: '8px 16px', borderRadius: '8px' }}>
          {status} Status
        </span>
      </div>

      {/* Details Grid Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '28px', alignItems: 'start' }}>
        {/* Left Column (Asset Info, Sensor History, Work Orders) */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
          
          {/* Machine General Info & Telemetry Grid */}
          <div className="glass-card">
            <h3 className="card-title" style={{ marginBottom: '16px' }}>Asset Specifications & Live Vitals</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '16px', marginBottom: '24px', paddingBottom: '16px', borderBottom: '1px solid var(--border-glass)' }}>
              <div>
                <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Hardware ID</span>
                <div style={{ fontSize: '15px', fontWeight: 700, marginTop: '4px' }}>{activeId}</div>
              </div>
              <div>
                <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Model Number</span>
                <div style={{ fontSize: '15px', fontWeight: 700, marginTop: '4px' }}>{mModel}</div>
              </div>
              <div>
                <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Plant Location</span>
                <div style={{ fontSize: '15px', fontWeight: 700, marginTop: '4px' }}>{mLocation}</div>
              </div>
              <div>
                <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Registration Date</span>
                <div style={{ fontSize: '15px', fontWeight: 700, marginTop: '4px' }}>{regDate}</div>
              </div>
            </div>

            {/* Vitals Mini-Dashboard Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '12px' }}>
              {[
                { label: 'AIR TEMP', val: airTemp, unit: 'K', key: 'air_temperature', rawVal: airTemp },
                { label: 'PROCESS TEMP', val: procTemp, unit: 'K', key: 'process_temperature', rawVal: procTemp },
                { label: 'SPEED', val: speed, unit: 'RPM', key: 'rotational_speed', rawVal: speed },
                { label: 'TORQUE', val: torque, unit: 'Nm', key: 'torque', rawVal: torque },
                { label: 'TOOL WEAR', val: toolWear, unit: 'min', key: 'tool_wear', rawVal: toolWear }
              ].map((item) => {
                const anomalous = isPointAnomaly(item.key, item.rawVal);
                const barPct = getVitalBarWidth(item.key, item.rawVal);
                return (
                  <div 
                    key={item.key} 
                    style={{ 
                      background: 'rgba(255,255,255,0.02)', 
                      padding: '12px', 
                      borderRadius: '8px', 
                      border: '1px solid var(--border-glass)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '6px'
                    }}
                  >
                    <span style={{ fontSize: '9px', color: 'var(--text-secondary)', fontWeight: 600 }}>{item.label}</span>
                    <div style={{ fontSize: '16px', fontWeight: 800, color: anomalous ? 'var(--danger)' : 'var(--text-primary)' }}>
                      {item.val ? `${item.val.toFixed(1)} ${item.unit}` : '—'}
                    </div>
                    {/* Vitals Progress Bar Indicator */}
                    <div style={{ height: '4px', background: 'rgba(255,255,255,0.05)', borderRadius: '2px', overflow: 'hidden', marginTop: '2px' }}>
                      <div 
                        style={{ 
                          width: `${barPct}%`, 
                          height: '100%', 
                          background: anomalous ? 'var(--danger)' : 'var(--success)', 
                          borderRadius: '2px' 
                        }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Historical Telemetry & Failure Risk Trend Charts */}
          <div className="glass-card chart-card">
            <div className="chart-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', flexWrap: 'wrap', gap: '8px' }}>
              <h3 style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>Vitals Trend Analysis</h3>
              <div className="chart-tabs" style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                <button className={`chart-tab ${activeTab === 'air_temperature' ? 'active' : ''}`} onClick={() => setActiveTab('air_temperature')}>Air Temp</button>
                <button className={`chart-tab ${activeTab === 'process_temperature' ? 'active' : ''}`} onClick={() => setActiveTab('process_temperature')}>Proc Temp</button>
                <button className={`chart-tab ${activeTab === 'rotational_speed' ? 'active' : ''}`} onClick={() => setActiveTab('rotational_speed')}>Speed</button>
                <button className={`chart-tab ${activeTab === 'torque' ? 'active' : ''}`} onClick={() => setActiveTab('torque')}>Torque</button>
                <button className={`chart-tab ${activeTab === 'tool_wear' ? 'active' : ''}`} onClick={() => setActiveTab('tool_wear')}>Tool Wear</button>
                <button className={`chart-tab ${activeTab === 'failure_probability' ? 'active' : ''}`} onClick={() => setActiveTab('failure_probability')}>Failure Risk</button>
              </div>
            </div>

            <div style={{ height: '220px', position: 'relative' }}>
              {detailLoading ? (
                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}><div className="spinner"></div></div>
              ) : detail && detail.sensor_history && detail.sensor_history.length > 0 ? (
                <svg viewBox="0 0 500 200" style={{ width: '100%', height: '100%', overflow: 'visible' }}>
                  <defs>
                    <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={activeTab === 'failure_probability' ? 'var(--danger)' : 'var(--primary)'} stopOpacity="0.25" />
                      <stop offset="100%" stopColor={activeTab === 'failure_probability' ? 'var(--danger)' : 'var(--primary)'} stopOpacity="0" />
                    </linearGradient>
                  </defs>

                  {/* Area fill */}
                  <path d={trendData.area} fill="url(#chartGrad)" />

                  {/* Trend Line */}
                  <path d={trendData.path} fill="none" stroke={activeTab === 'failure_probability' ? 'var(--danger)' : 'var(--primary)'} strokeWidth="2.5" />

                  {/* Interactive dots */}
                  {trendData.points.map((p, i) => {
                    const pointVal = detail.sensor_history[i][activeTab];
                    const anomalous = isPointAnomaly(activeTab, pointVal);
                    return (
                      <circle
                        key={i}
                        cx={p.x}
                        cy={p.y}
                        r="3.5"
                        fill={anomalous ? 'var(--danger)' : 'var(--primary)'}
                        stroke="#070a13"
                        strokeWidth="1.5"
                        style={{ cursor: 'pointer' }}
                        title={`Val: ${pointVal.toFixed(1)}`}
                      />
                    );
                  })}

                  <text x="20" y="195" fill="var(--text-muted)" fontSize="9">Time (Historical Evaluation Runs) →</text>
                  <text x="480" y="15" fill="var(--text-muted)" fontSize="9" textAnchor="end">
                    Max Value: {trendData.maxVal ? trendData.maxVal.toFixed(1) : ''}
                  </text>
                </svg>
              ) : (
                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: 'var(--text-muted)', fontSize: '13px' }}>
                  No historical logs active.
                </div>
              )}
            </div>
          </div>

          {/* Work Order History */}
          <div className="glass-card">
            <h3 className="card-title" style={{ marginBottom: '14px' }}>Maintenance Work Order History</h3>
            <div className="table-responsive" style={{ overflowX: 'auto' }}>
              <table className="parts-table" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr>
                    <th>Order ID</th>
                    <th>Action Required</th>
                    <th>Priority</th>
                    <th>Status</th>
                    <th>Created At</th>
                    <th>Completed At</th>
                  </tr>
                </thead>
                <tbody>
                  {machineWorkOrders.length === 0 ? (
                    <tr>
                      <td colSpan={6} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '20px' }}>
                        No work orders generated or authorized for this asset.
                      </td>
                    </tr>
                  ) : (
                    machineWorkOrders.map((wo) => {
                      const statusClass = wo.status === 'completed' ? 'healthy' : wo.status === 'in_progress' ? 'warning' : 'danger';
                      return (
                        <tr key={wo.id}>
                          <td><strong>WO-{String(wo.id).padStart(3, '0')}</strong></td>
                          <td style={{ fontSize: '12px' }}>{wo.action_required}</td>
                          <td>
                            <span className={`machine-prob-badge ${wo.priority.toLowerCase() === 'critical' ? 'danger' : wo.priority.toLowerCase() === 'high' ? 'warning' : 'healthy'}`}>
                              {wo.priority}
                            </span>
                          </td>
                          <td>
                            <span className={`machine-prob-badge ${statusClass}`}>
                              {wo.status.replace('_', ' ')}
                            </span>
                          </td>
                          <td>{new Date(wo.created_at).toLocaleString()}</td>
                          <td>{wo.completed_at ? new Date(wo.completed_at).toLocaleString() : '—'}</td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>

        </div>

        {/* Right Column (Failure Risk Gauge, Prescriptive Actions) */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
          
          {/* Risk Gauge Card */}
          <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', padding: '24px' }}>
            <h3 style={{ fontSize: '14px', alignSelf: 'flex-start', color: 'var(--text-secondary)', marginBottom: '20px' }}>Failure Risk Analysis</h3>
            
            <div className="risk-gauge-container" style={{ position: 'relative', width: '160px', height: '160px', marginBottom: '16px' }}>
              <svg className="risk-gauge-svg" viewBox="0 0 160 160" style={{ width: '100%', height: '100%', transform: 'rotate(-90deg)' }}>
                <circle cx="80" cy="80" r="70" className="gauge-bg" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="12" />
                <circle
                  cx="80"
                  cy="80"
                  r="70"
                  className={`gauge-fill ${getRiskClass(probPct)}`}
                  fill="none"
                  stroke={probPct >= 80 ? 'var(--danger)' : probPct >= 30 ? 'var(--warning)' : 'var(--success)'}
                  strokeWidth="12"
                  strokeDasharray={`${(probPct / 100) * 439.6} 439.6`}
                  style={{ strokeLinecap: 'round', transition: 'stroke-dasharray 0.5s ease' }}
                />
              </svg>
              <div className="gauge-text" style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <span className="gauge-val" style={{ fontSize: '28px', fontWeight: 800, color: probPct >= 80 ? 'var(--danger)' : probPct >= 30 ? 'var(--warning)' : 'var(--success)' }}>
                  {probPct}%
                </span>
                <span className="gauge-lbl" style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', marginTop: '2px' }}>Prob.</span>
              </div>
            </div>

            <div style={{ marginTop: '10px' }}>
              <h4 style={{ fontSize: '15px', fontWeight: 700 }}>
                {machineObj ? machineObj.predicted_failure : 'Normal Operation'}
              </h4>
              {detail && detail.prediction && detail.prediction.time_to_failure && detail.prediction.time_to_failure !== 'N/A' ? (
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '4px', justifyContent: 'center', marginTop: '6px' }}>
                  <Clock size={12} className="text-warning" /> Est. failure in: <strong>{detail.prediction.time_to_failure}</strong>
                </p>
              ) : (
                <p style={{ fontSize: '12px', color: 'var(--success)', marginTop: '6px' }}>Vitals operating in healthy ranges</p>
              )}
            </div>
          </div>

          {/* Prescriptive Recommendation Card */}
          <div className="glass-card">
            {recLoading ? (
              <div style={{ display: 'flex', justifyContent: 'center', padding: '40px 0' }}><div className="spinner"></div></div>
            ) : machineRec && machineRec.has_recommendation ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '12px', borderBottom: '1px solid var(--border-glass)' }}>
                  <h3 style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>Recommended Mitigation</h3>
                  <span className={`machine-prob-badge ${machineRec.priority.toLowerCase() === 'critical' ? 'danger' : machineRec.priority.toLowerCase() === 'high' ? 'warning' : 'healthy'}`}>
                    {machineRec.priority}
                  </span>
                </div>

                <div style={{ padding: '12px', background: 'rgba(255,255,255,0.01)', border: '1px solid var(--border-glass)', borderRadius: '8px' }}>
                  <h4 style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.05em' }}>Action Required</h4>
                  <p style={{ fontSize: '12px', marginTop: '6px', lineHeight: '1.5' }}>{machineRec.recommendation}</p>
                </div>

                <div>
                  <h4 style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.05em', marginBottom: '8px' }}>Spare Parts Checklist</h4>
                  {machineRec.parts_status && machineRec.parts_status.length > 0 ? (
                    <table className="parts-table" style={{ width: '100%', fontSize: '11px' }}>
                      <thead>
                        <tr>
                          <th>Part</th>
                          <th>Qty</th>
                          <th>Stock</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {machineRec.parts_status.map((p, idx) => (
                          <tr key={idx}>
                            <td>{p.part_name}</td>
                            <td>{p.quantity_required}</td>
                            <td>{p.stock_available}</td>
                            <td>
                              <span className={`part-status-badge ${p.status}`} style={{ fontSize: '9px', padding: '2px 6px' }}>
                                {p.status}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p style={{ fontSize: '11px', color: 'var(--text-muted)' }}>No spare parts required.</p>
                  )}
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px', paddingTop: '10px', borderTop: '1px solid var(--border-glass)' }}>
                  <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>Est: <strong>{machineRec.estimated_duration_hours}h</strong></span>
                  <button
                    className="btn-primary"
                    onClick={onCreateWorkOrder}
                    disabled={submittingWorkOrder}
                    style={{ padding: '6px 12px', fontSize: '11px' }}
                  >
                    {submittingWorkOrder ? 'Scheduling...' : 'Authorize Repair'}
                  </button>
                </div>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '30px 10px', color: 'var(--text-secondary)' }}>
                <CheckCircle2 size={32} className="text-success" style={{ marginBottom: '10px', marginInline: 'auto' }} />
                <h3 style={{ fontSize: '14px' }}>Asset Operating Normally</h3>
                <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>No active corrective recommendations required.</p>
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
