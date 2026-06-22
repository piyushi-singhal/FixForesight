import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Cpu,
  Database,
  RefreshCw,
  Search,
  Settings,
  ShieldAlert,
  Wifi,
  Wrench,
  XCircle
} from 'lucide-react';
import {
  fetchMachines,
  fetchMachineRisk,
  fetchMachineRecommendations,
  createWorkOrder,
  fetchAlerts,
  searchIncidents,
  setActiveMachineId,
  clearSearch,
  setQuery,
  resetWorkOrderStatus
} from './store';

export default function App() {
  const dispatch = useDispatch();
  
  // Selectors
  const machines = useSelector((state) => state.machines.list);
  const activeId = useSelector((state) => state.machines.activeMachineId);
  const machinesLoading = useSelector((state) => state.machines.loading);
  
  const detail = useSelector((state) => state.detail.data);
  const detailLoading = useSelector((state) => state.detail.loading);
  
  const rec = useSelector((state) => state.recommendation.data);
  const recLoading = useSelector((state) => state.recommendation.loading);
  const workOrderSuccess = useSelector((state) => state.recommendation.workOrderSuccess);
  const submittingWorkOrder = useSelector((state) => state.recommendation.submittingWorkOrder);

  const alerts = useSelector((state) => state.alerts.list);
  
  const searchQuery = useSelector((state) => state.search.query);
  const searchResults = useSelector((state) => state.search.results);
  const searchLoading = useSelector((state) => state.search.loading);

  // Local State
  const [activeTab, setActiveTab] = useState('temperature'); // temperature, vibration, pressure
  const [sysHealth, setSysHealth] = useState({ status: 'healthy', postgres: 'healthy', localstack: 'healthy', solr: 'healthy' });

  // Fetch initial data
  useEffect(() => {
    dispatch(fetchMachines());
    dispatch(fetchAlerts());
    checkHealth();

    // Auto-polling interval for live IoT/alert feed updates (every 3 seconds)
    const interval = setInterval(() => {
      dispatch(fetchMachines());
      dispatch(fetchAlerts());
    }, 3000);

    return () => clearInterval(interval);
  }, [dispatch]);

  // Fetch detail data when active machine changes
  useEffect(() => {
    if (activeId) {
      dispatch(fetchMachineRisk(activeId));
      dispatch(fetchMachineRecommendations(activeId));
    }
  }, [dispatch, activeId]);

  // Handle work order creation success notification
  useEffect(() => {
    if (workOrderSuccess) {
      alert("Work Order generated successfully!");
      dispatch(resetWorkOrderStatus());
      dispatch(fetchMachines());
    }
  }, [workOrderSuccess, dispatch]);

  const checkHealth = async () => {
    try {
      const response = await fetch(`${window.location.origin}/health`);
      if (response.ok) {
        const data = await response.json();
        setSysHealth(data);
      }
    } catch (e) {
      setSysHealth({ status: 'offline', postgres: 'unhealthy', localstack: 'unhealthy', solr: 'unhealthy' });
    }
  };

  const handleMachineSelect = (id) => {
    dispatch(setActiveMachineId(id));
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      dispatch(searchIncidents(searchQuery));
    }
  };

  const handleClearSearch = () => {
    dispatch(clearSearch());
  };

  const handleCreateWorkOrder = () => {
    if (!rec || !rec.has_recommendation) return;
    dispatch(createWorkOrder({
      machineId: activeId,
      priority: rec.priority,
      actionRequired: rec.recommended_action
    }));
  };

  // Helper: color code for risk levels
  const getRiskClass = (prob) => {
    if (prob >= 0.7) return 'danger';
    if (prob >= 0.3) return 'warning';
    return 'healthy';
  };

  // Helper: dynamic gauge properties
  const selectedMachine = machines.find(m => m.id === activeId) || { name: `Machine-${String(activeId).padStart(3, '0')}`, failure_probability: 0.05 };
  const currentRisk = selectedMachine.failure_probability;
  const strokeDash = currentRisk * 439.6; // Gauge circumference = 2 * pi * 70

  // Helper: SVG Path generator for sensor trend history
  const getSvgPathData = (history, key) => {
    if (!history || history.length === 0) return { path: '', area: '' };
    
    const width = 500;
    const height = 200;
    const padding = 20;

    const values = history.map(h => h[key]);
    const maxVal = Math.max(...values, 1) * 1.05;
    const minVal = Math.min(...values, 0) * 0.95;
    const valRange = maxVal - minVal;

    const points = history.map((h, i) => {
      const x = padding + (i * (width - padding * 2)) / (history.length - 1);
      const val = h[key];
      const y = height - padding - ((val - minVal) * (height - padding * 2)) / valRange;
      return { x, y };
    });

    let path = `M ${points[0].x} ${points[0].y}`;
    for (let i = 1; i < points.length; i++) {
      path += ` L ${points[i].x} ${points[i].y}`;
    }

    const area = `${path} L ${points[points.length - 1].x} ${height - padding} L ${points[0].x} ${height - padding} Z`;
    return { path, area, points, minVal, maxVal };
  };

  const trendData = detail ? getSvgPathData(detail.sensor_history, activeTab) : { path: '', area: '', points: [] };

  return (
    <div className="app-container">
      {/* Header Bar */}
      <header className="app-header">
        <div className="logo-section">
          <Cpu className="logo-icon" size={24} />
          <h1 className="logo-text">FixForesight</h1>
        </div>

        {/* Global Search Bar */}
        <form onSubmit={handleSearchSubmit} className="search-container">
          <Search size={16} className="text-secondary" />
          <input
            type="text"
            className="search-input"
            placeholder="Search historical incidents (e.g. bearing, coolant, overheat)..."
            value={searchQuery}
            onChange={(e) => dispatch(setQuery(e.target.value))}
          />
          {searchQuery && (
            <button type="button" onClick={handleClearSearch} style={{ background: 'transparent', border: 'none', color: '#64748b', cursor: 'pointer', fontSize: '11px' }}>
              Clear
            </button>
          )}
        </form>

        {/* Infrastructure Status indicators */}
        <div className="system-status">
          <div className="status-badge" title="FastAPI API Status">
            <Wifi size={13} className={sysHealth.status !== 'offline' ? 'text-success' : 'text-danger'} />
            API: <span style={{ color: sysHealth.status !== 'offline' ? '#10b981' : '#f43f5e' }}>{sysHealth.status}</span>
          </div>
          <div className="status-badge" title="PostgreSQL DB Status">
            <Database size={13} className={sysHealth.postgres === 'healthy' ? 'text-success' : 'text-danger'} />
            DB
          </div>
          <div className="status-badge" title="AWS simulated SQS/SNS Status">
            <Activity size={13} className={sysHealth.localstack === 'healthy' ? 'text-success' : 'text-danger'} />
            AWS-Queue
          </div>
          <div className="status-badge" title="Solr incidents index Status">
            <Search size={13} className={sysHealth.solr === 'healthy' ? 'text-success' : 'text-danger'} />
            Solr
          </div>
          <button className="status-badge" onClick={checkHealth} style={{ cursor: 'pointer', border: '1px solid var(--border-glass)', outline: 'none' }}>
            <RefreshCw size={12} />
          </button>
        </div>
      </header>

      {/* Main Grid */}
      <main className="dashboard-grid">
        
        {/* Left Column: Machine Directory */}
        <aside className="sidebar-panel">
          <div className="panel-header">
            <h2 className="panel-title">Monitored Machines</h2>
            <span className="status-badge" style={{ padding: '2px 8px', fontSize: '10px' }}>
              <span className="status-indicator active"></span>
              Live Feed
            </span>
          </div>
          
          <div className="machine-list">
            {machinesLoading && machines.length === 0 ? (
              <div style={{ display: 'flex', justifyContent: 'center', margin: '40px 0' }}><div className="spinner"></div></div>
            ) : (
              machines.map((m) => {
                const riskLevel = getRiskClass(m.failure_probability);
                return (
                  <div
                    key={m.id}
                    className={`machine-item ${activeId === m.id ? 'active' : ''}`}
                    onClick={() => handleMachineSelect(m.id)}
                  >
                    <div className="machine-item-top">
                      <div className="machine-name-group">
                        <Cpu size={14} className={riskLevel === 'danger' ? 'text-danger' : riskLevel === 'warning' ? 'text-warning' : 'text-success'} />
                        <span className="machine-name">{m.name}</span>
                      </div>
                      <span className={`machine-prob-badge ${riskLevel}`}>
                        {(m.failure_probability * 100).toFixed(0)}% Risk
                      </span>
                    </div>

                    <div className="machine-metrics-row">
                      <span>T: {m.temperature.toFixed(1)}°C</span>
                      <span>V: {m.vibration.toFixed(1)}m/s²</span>
                      <span>P: {m.pressure.toFixed(0)} PSI</span>
                    </div>

                    <div className="machine-item-bottom">
                      <span>{m.predicted_failure_type || 'Healthy'}</span>
                      {m.open_work_orders > 0 && (
                        <span style={{ color: '#0ea5e9', display: 'flex', alignItems: 'center', gap: '3px' }}>
                          <Wrench size={10} /> Active order
                        </span>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </aside>

        {/* Center Column: Detailed Analytics & Prescriptive Panel */}
        <section className="center-panel">
          {/* Solr Search Results pop-in */}
          {searchResults && (
            <div className="glass-card search-results-overlay">
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                <h3 style={{ fontSize: '16px', color: 'var(--primary)' }}>Historical Incidents Search Results</h3>
                <button onClick={handleClearSearch} style={{ background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid var(--border-glass)', padding: '4px 10px', borderRadius: '6px', cursor: 'pointer', fontSize: '11px' }}>
                  Close Results
                </button>
              </div>
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Found {searchResults.numFound} logs matching your query.</p>
              
              <div className="search-results-list">
                {searchResults.docs.length === 0 ? (
                  <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>No historical logs match this search term.</p>
                ) : (
                  searchResults.docs.map((doc, idx) => (
                    <div key={doc.id || idx} className="search-result-item">
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                        <strong>Machine-{String(doc.machine_id).padStart(3, '0')}</strong>
                        <span style={{ color: 'var(--text-muted)' }}>{new Date(doc.date).toLocaleDateString()}</span>
                      </div>
                      <p style={{ fontSize: '12px', marginTop: '4px' }}>
                        <span style={{ color: 'var(--danger)', fontWeight: 500 }}>Signature:</span> {doc.failure_signature}
                      </p>
                      <p style={{ fontSize: '12px' }}>
                        <span style={{ color: 'var(--success)', fontWeight: 500 }}>Corrective Action:</span> {doc.action_taken}
                      </p>
                      <p style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                        Outcome: <span style={{ color: doc.outcome === 'Resolved' ? 'var(--success)' : 'var(--warning)' }}>{doc.outcome}</span>
                      </p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* Machine Details view */}
          <div className="machine-detail-grid">
            
            {/* Fail Prediction Gauge */}
            <div className="glass-card risk-level-card">
              <h3 style={{ fontSize: '14px', alignSelf: 'flex-start', color: 'var(--text-secondary)' }}>Failure Risk Matrix</h3>
              
              <div className="risk-gauge-container">
                <svg className="risk-gauge-svg">
                  <circle cx="80" cy="80" r="70" className="gauge-bg" />
                  <circle
                    cx="80"
                    cy="80"
                    r="70"
                    className={`gauge-fill ${getRiskClass(currentRisk)}`}
                    strokeDasharray={`${strokeDash} 439.6`}
                  />
                </svg>
                <div className="gauge-text">
                  <span className="gauge-val" style={{ color: currentRisk >= 0.7 ? 'var(--danger)' : currentRisk >= 0.3 ? 'var(--warning)' : 'var(--success)' }}>
                    {(currentRisk * 100).toFixed(0)}%
                  </span>
                  <span className="gauge-lbl">Failure</span>
                </div>
              </div>

              <div style={{ marginTop: '10px' }}>
                <h4 style={{ fontSize: '16px', fontWeight: 700 }}>{selectedMachine.predicted_failure_type || 'Healthy'}</h4>
                {selectedMachine.time_to_failure_hours ? (
                  <p style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '4px', justifyContent: 'center', marginTop: '4px' }}>
                    <Clock size={12} className="text-warning" /> Est. failure in: <strong>{selectedMachine.time_to_failure_hours} hours</strong>
                  </p>
                ) : (
                  <p style={{ fontSize: '12px', color: 'var(--success)', marginTop: '4px' }}>Vitals operating in healthy ranges</p>
                )}
              </div>
            </div>

            {/* Live Sensor Telemetry Charts */}
            <div className="glass-card chart-card">
              <div className="chart-header">
                <h3 style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>Sensor History</h3>
                <div className="chart-tabs">
                  <button className={`chart-tab ${activeTab === 'temperature' ? 'active' : ''}`} onClick={() => setActiveTab('temperature')}>Temp</button>
                  <button className={`chart-tab ${activeTab === 'vibration' ? 'active' : ''}`} onClick={() => setActiveTab('vibration')}>Vibr</button>
                  <button className={`chart-tab ${activeTab === 'pressure' ? 'active' : ''}`} onClick={() => setActiveTab('pressure')}>Pres</button>
                </div>
              </div>

              <div className="chart-body">
                {detailLoading ? (
                  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}><div className="spinner"></div></div>
                ) : detail && detail.sensor_history.length > 0 ? (
                  <svg viewBox="0 0 500 200" className="sparkline-svg">
                    <defs>
                      <linearGradient id="chart-gradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="var(--primary)" stopOpacity="0.25" />
                        <stop offset="100%" stopColor="var(--primary)" stopOpacity="0" />
                      </linearGradient>
                    </defs>

                    {/* Grid lines */}
                    {[40, 80, 120, 160].map((y, idx) => (
                      <line key={idx} x1="20" y1={y} x2="480" y2={y} className="sparkline-grid-line" />
                    ))}

                    {/* Line & Area */}
                    <path d={trendData.area} className="sparkline-area" />
                    <path d={trendData.path} className="sparkline-path" />

                    {/* Chart Points */}
                    {trendData.points.map((p, i) => (
                      <circle
                        key={i}
                        cx={p.x}
                        cy={p.y}
                        r={activeTab === 'vibration' && detail.sensor_history[i][activeTab] > 5 ? 5 : 3.5}
                        fill={activeTab === 'vibration' && detail.sensor_history[i][activeTab] > 5 ? 'var(--danger)' : 'var(--primary)'}
                        stroke="#070a13"
                        strokeWidth="1.5"
                        style={{ cursor: 'pointer' }}
                        title={`Val: ${detail.sensor_history[i][activeTab].toFixed(1)}`}
                      />
                    ))}

                    {/* Axis Labels */}
                    <text x="20" y="195" fill="var(--text-muted)" fontSize="9">Time →</text>
                    <text x="440" y="15" fill="var(--text-muted)" fontSize="9" textAnchor="end">
                      Max: {trendData.maxVal ? trendData.maxVal.toFixed(1) : ''}
                    </text>
                  </svg>
                ) : (
                  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: 'var(--text-muted)' }}>No historical data logged.</div>
                )}
              </div>
            </div>

          </div>

          {/* Prescriptive Recommendation Sheet */}
          <div className="glass-card rec-card">
            {recLoading ? (
              <div style={{ display: 'flex', justifyContent: 'center', padding: '40px 0' }}><div className="spinner"></div></div>
            ) : rec && rec.has_recommendation ? (
              <>
                <div className="rec-title-row">
                  <div>
                    <h3 style={{ fontSize: '18px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Wrench size={18} className="text-primary" /> Recommended Mitigation Plan
                    </h3>
                    <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                      Generated: {new Date(rec.created_at).toLocaleString()}
                    </p>
                  </div>
                  <span className={`rec-action-badge ${rec.priority}`}>
                    <ShieldAlert size={14} />
                    {rec.priority} Priority
                  </span>
                </div>

                <div style={{ padding: '16px', background: 'rgba(255,255,255,0.01)', border: '1px solid var(--border-glass)', borderRadius: '10px' }}>
                  <h4 style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.05em' }}>Action Items</h4>
                  <p style={{ fontSize: '13px', marginTop: '6px', lineHeight: '1.5' }}>{rec.recommended_action}</p>
                </div>

                {/* Parts Requirement checklist */}
                <div>
                  <h4 style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.05em', marginBottom: '8px' }}>Required Spare Parts Checklist</h4>
                  
                  {rec.parts_status.length === 0 ? (
                    <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>No spare parts required for this maintenance plan.</p>
                  ) : (
                    <table className="parts-table">
                      <thead>
                        <tr>
                          <th>Part Name</th>
                          <th>Needed</th>
                          <th>Warehouse Stock</th>
                          <th>Status</th>
                          <th>Unit Cost</th>
                        </tr>
                      </thead>
                      <tbody>
                        {rec.parts_status.map((p, idx) => (
                          <tr key={idx}>
                            <td>{p.part_name}</td>
                            <td>{p.quantity_required}</td>
                            <td>{p.stock_available}</td>
                            <td>
                              <span className={`part-status-badge ${p.status}`}>
                                {p.status}
                              </span>
                            </td>
                            <td>${p.unit_cost.toFixed(2)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px', paddingTop: '10px', borderTop: '1px solid var(--border-glass)' }}>
                  <div style={{ display: 'flex', gap: '20px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                    <span>Est. Repair Duration: <strong>{rec.estimated_duration_hours} hours</strong></span>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '6px' }}>
                    {rec.parts_missing && (
                      <span style={{ fontSize: '11px', color: 'var(--danger)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <AlertTriangle size={12} /> Out-of-stock parts detected
                      </span>
                    )}
                    <button
                      className="btn-primary"
                      onClick={handleCreateWorkOrder}
                      disabled={submittingWorkOrder}
                    >
                      <CheckCircle2 size={16} />
                      {submittingWorkOrder ? 'Scheduling...' : 'Authorize Work Order'}
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-secondary)' }}>
                <CheckCircle2 size={32} className="text-success" style={{ marginBottom: '10px' }} />
                <h3>Vitals Stable & Normal</h3>
                <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>No active corrective recommendations are pending for this unit.</p>
              </div>
            )}
          </div>
        </section>

        {/* Right Column: Live Warnings & SNS Alerts feed */}
        <aside className="alerts-panel">
          <div className="panel-header">
            <h2 className="panel-title">System Event Feed</h2>
            <span className="status-badge" style={{ borderColor: 'var(--primary-glow)', color: 'var(--primary)' }}>
              SNS
            </span>
          </div>

          <div className="alerts-list">
            {alerts.length === 0 ? (
              <p style={{ fontSize: '12px', color: 'var(--text-muted)', textAlign: 'center', marginTop: '20px' }}>No warnings logged.</p>
            ) : (
              alerts.map((a) => {
                const isCritical = a.subject && a.subject.includes('CRITICAL');
                const isHigh = a.subject && a.subject.includes('HIGH');
                const cardClass = isCritical ? 'critical' : isHigh ? 'warning' : 'info';
                
                return (
                  <div key={a.id} className={`alert-card ${cardClass}`}>
                    <div className="alert-icon-wrapper">
                      {isCritical ? (
                        <XCircle size={16} className="text-danger" />
                      ) : isHigh ? (
                        <AlertTriangle size={16} className="text-warning" />
                      ) : (
                        <Activity size={16} className="text-info" />
                      )}
                    </div>
                    <div className="alert-content">
                      <span className="alert-subject">{a.subject}</span>
                      <p className="alert-message">{a.message}</p>
                      <span className="alert-time">{new Date(a.received_at).toLocaleTimeString()}</span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </aside>

      </main>
    </div>
  );
}
