import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Cpu,
  Database,
  FileText,
  LayoutDashboard,
  RefreshCw,
  Search,
  Settings,
  ShieldAlert,
  TrendingUp,
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
  
  // Redux Selectors
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

  // Local State for Tabs / Navigation / Custom Page Data
  const [activePage, setActivePage] = useState('dashboard'); // dashboard, machines, predictions, recommendations, analytics, search
  const [activeTab, setActiveTab] = useState('temperature'); // temperature, vibration, pressure
  const [sysHealth, setSysHealth] = useState({ status: 'healthy', postgres: 'healthy', localstack: 'healthy', solr: 'healthy' });
  const [analytics, setAnalytics] = useState({ healthy: 60, warning: 40, critical: 0 });
  const [predictions, setPredictions] = useState([]);
  const [predictionsLoading, setPredictionsLoading] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [recsLoading, setRecsLoading] = useState(false);

  // Resolve backend API URL dynamically
  const apiBase = window.location.port === '3000'
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : window.location.origin;

  // Initial and poll fetching
  useEffect(() => {
    dispatch(fetchMachines());
    dispatch(fetchAlerts());
    checkHealth();
    loadPredictions();
    loadAllRecommendations();

    const interval = setInterval(() => {
      dispatch(fetchMachines());
      dispatch(fetchAlerts());
      checkHealth();
    }, 3000);

    return () => clearInterval(interval);
  }, [dispatch]);

  // Load active machine recommendations and risk when selected machine changes
  useEffect(() => {
    if (activeId) {
      dispatch(fetchMachineRisk(activeId));
      dispatch(fetchMachineRecommendations(activeId));
    }
  }, [dispatch, activeId]);

  // Switch context fetching when page tab changes
  useEffect(() => {
    if (activePage === 'predictions') {
      loadPredictions();
    } else if (activePage === 'recommendations') {
      loadAllRecommendations();
    } else if (activePage === 'analytics') {
      checkHealth();
    }
  }, [activePage]);

  // Authorization feedback
  useEffect(() => {
    if (workOrderSuccess) {
      alert("Work Order generated successfully!");
      dispatch(resetWorkOrderStatus());
      dispatch(fetchMachines());
      if (activeId) {
        dispatch(fetchMachineRisk(activeId));
        dispatch(fetchMachineRecommendations(activeId));
      }
      loadPredictions();
      loadAllRecommendations();
    }
  }, [workOrderSuccess, dispatch, activeId]);

  const checkHealth = async () => {
    try {
      const response = await fetch(`${apiBase}/health`);
      if (response.ok) {
        const data = await response.json();
        setSysHealth(data);
      }
      
      const analResp = await fetch(`${apiBase}/analytics`);
      if (analResp.ok) {
        const analData = await analResp.json();
        setAnalytics(analData);
      }
    } catch (e) {
      setSysHealth({ status: 'offline', postgres: 'unhealthy', localstack: 'unhealthy', solr: 'unhealthy' });
    }
  };

  const loadPredictions = async () => {
    try {
      setPredictionsLoading(true);
      const resp = await fetch(`${apiBase}/predictions`);
      if (resp.ok) {
        const data = await resp.json();
        setPredictions(data);
      }
    } catch (e) {
      console.error("Failed to load predictions", e);
    } finally {
      setPredictionsLoading(false);
    }
  };

  const loadAllRecommendations = async () => {
    try {
      setRecsLoading(true);
      const resp = await fetch(`${apiBase}/recommendations`);
      if (resp.ok) {
        const list = await resp.json();
        const detailedList = await Promise.all(
          list.map(async (r) => {
            try {
              const dResp = await fetch(`${apiBase}/machines/${r.machine_id}/recommendations`);
              if (dResp.ok) {
                return await dResp.json();
              }
            } catch (err) {
              console.error(err);
            }
            return {
              machine_id: r.machine_id,
              has_recommendation: true,
              recommendation: r.recommendation,
              priority: r.priority,
              confidence: r.confidence,
              parts_status: [],
              parts_missing: false,
              estimated_duration_hours: 4,
              created_at: new Date().toISOString()
            };
          })
        );
        setRecommendations(detailedList);
      }
    } catch (e) {
      console.error("Failed to load global recommendations", e);
    } finally {
      setRecsLoading(false);
    }
  };

  const handleMachineSelect = (id) => {
    dispatch(setActiveMachineId(id));
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      dispatch(searchIncidents(searchQuery));
      setActivePage('search');
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
      actionRequired: rec.recommendation
    }));
  };

  const getRiskClass = (prob) => {
    if (prob >= 70) return 'danger';
    if (prob >= 30) return 'warning';
    return 'healthy';
  };

  // Sparkline Generator helper
  const getSvgPathData = (history, key) => {
    if (!history || history.length === 0) return { path: '', area: '', points: [] };
    
    const width = 500;
    const height = 200;
    const padding = 20;

    const values = history.map(h => h[key]);
    const maxVal = Math.max(...values, 1) * 1.05;
    const minVal = Math.min(...values, 0) * 0.95;
    const valRange = maxVal - minVal || 1;

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
  const selectedMachine = machines.find(m => m.machine_id === activeId) || { machine_name: `Machine-${activeId}`, status: 'Healthy', rpm: 1000 };
  const currentRisk = detail && detail.prediction ? detail.prediction.failure_probability : 5;
  const strokeDash = (currentRisk / 100.0) * 439.6;

  // ================= VIEW RENDERS =================

  // 1. Dashboard View
  const renderDashboardPage = () => {
    const totalCount = machines.length;
    const healthyCount = machines.filter(m => m.status === 'Healthy').length;
    const warningCount = machines.filter(m => m.status === 'Warning').length;
    const criticalCount = machines.filter(m => m.status === 'Critical').length;

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

        {/* Dashboard Grid layout */}
        <div style={{ display: 'grid', gridTemplateColumns: '5fr 4fr', gap: '28px' }}>
          
          {/* Services & Health */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
            <div className="glass-card">
              <h3 className="card-title">Infrastructure Dependencies</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginTop: '10px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(255,255,255,0.01)', border: '1px solid var(--border-glass)', padding: '12px', borderRadius: '10px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <Wifi size={16} style={{ color: sysHealth.status !== 'offline' ? 'var(--success)' : 'var(--danger)' }} />
                    <span style={{ fontSize: '13px', fontWeight: 600 }}>FastAPI Router Server</span>
                  </div>
                  <span className={`machine-prob-badge ${sysHealth.status !== 'offline' ? 'healthy' : 'danger'}`}>
                    {sysHealth.status !== 'offline' ? 'ONLINE' : 'OFFLINE'}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(255,255,255,0.01)', border: '1px solid var(--border-glass)', padding: '12px', borderRadius: '10px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <Database size={16} style={{ color: sysHealth.postgres.includes('healthy') ? 'var(--success)' : 'var(--danger)' }} />
                    <span style={{ fontSize: '13px', fontWeight: 600 }}>PostgreSQL Database</span>
                  </div>
                  <span className={`machine-prob-badge ${sysHealth.postgres.includes('healthy') ? 'healthy' : 'danger'}`}>
                    CONNECTED
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(255,255,255,0.01)', border: '1px solid var(--border-glass)', padding: '12px', borderRadius: '10px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <Search size={16} style={{ color: sysHealth.solr.includes('healthy') ? 'var(--success)' : 'var(--danger)' }} />
                    <span style={{ fontSize: '13px', fontWeight: 600 }}>Apache Solr Incident Logs</span>
                  </div>
                  <span className={`machine-prob-badge ${sysHealth.solr.includes('healthy') ? 'healthy' : 'danger'}`}>
                    INDEXED
                  </span>
                </div>
              </div>
            </div>

            <div className="glass-card">
              <h3 className="card-title">Plant Health Index</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '10px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                  <span>Healthy Index</span>
                  <strong>{analytics.healthy}%</strong>
                </div>
                <div className="prediction-val-bar">
                  <div className="prediction-val-fill healthy" style={{ width: `${analytics.healthy}%` }}></div>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginTop: '6px' }}>
                  <span>Warning / Critical</span>
                  <strong>{analytics.warning + analytics.critical}%</strong>
                </div>
                <div className="prediction-val-bar">
                  <div className="prediction-val-fill warning" style={{ width: `${analytics.warning + analytics.critical}%` }}></div>
                </div>
              </div>
            </div>
          </div>

          {/* Warnings Feed */}
          <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', height: '100%', minHeight: '380px' }}>
            <div style={{ borderBottom: '1px solid var(--border-glass)', paddingBottom: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 className="card-title" style={{ margin: 0 }}>System Event Feed</h3>
              <span className="part-status-badge instock">SNS Topic</span>
            </div>
            
            <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '14px', maxHeight: '350px' }}>
              {alerts.length === 0 ? (
                <p style={{ fontSize: '12px', color: 'var(--text-muted)', textAlign: 'center', marginTop: '40px' }}>
                  All nodes operating normally. No alerts triggered.
                </p>
              ) : (
                alerts.map((a) => {
                  const isCritical = a.severity && a.severity.toLowerCase() === 'critical';
                  const isHigh = a.severity && a.severity.toLowerCase() === 'high';
                  const cardClass = isCritical ? 'critical' : isHigh ? 'warning' : 'info';
                  return (
                    <div key={a.alert_id} className={`alert-card ${cardClass}`}>
                      <div className="alert-content">
                        <span className="alert-subject" style={{ fontWeight: 700 }}>
                          {a.severity} Severity Alert (Machine {a.machine_id})
                        </span>
                        <p className="alert-message">{a.message}</p>
                        <span className="alert-time">{new Date(a.created_at).toLocaleTimeString()}</span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>

        </div>
      </div>
    );
  };

  // 2. Machines Directory & Analytics View
  const renderMachinesPage = () => {
    return (
      <div className="machines-layout">
        {/* Machine directory list */}
        <aside className="sidebar-panel">
          <div className="panel-header">
            <h2 className="panel-title">Monitored Units</h2>
            <span className="status-badge" style={{ padding: '2px 8px', fontSize: '10px' }}>
              <span className="status-indicator active"></span>
              IoT Feed
            </span>
          </div>

          <div className="machine-list">
            {machinesLoading && machines.length === 0 ? (
              <div style={{ display: 'flex', justifyContent: 'center', margin: '40px 0' }}><div className="spinner"></div></div>
            ) : (
              machines.map((m) => {
                const riskLevel = m.status === 'Critical' ? 'danger' : m.status === 'Warning' ? 'warning' : 'healthy';
                return (
                  <div
                    key={m.machine_id}
                    className={`machine-item ${activeId === m.machine_id ? 'active' : ''}`}
                    onClick={() => handleMachineSelect(m.machine_id)}
                  >
                    <div className="machine-item-top">
                      <div className="machine-name-group">
                        <Cpu size={14} className={riskLevel === 'danger' ? 'text-danger' : riskLevel === 'warning' ? 'text-warning' : 'text-success'} />
                        <span className="machine-name">{m.machine_name}</span>
                      </div>
                      <span className={`machine-prob-badge ${riskLevel}`}>
                        {m.status}
                      </span>
                    </div>

                    <div className="machine-metrics-row">
                      <span>T: {m.temperature.toFixed(1)}°C</span>
                      <span>P: {m.pressure.toFixed(0)} PSI</span>
                      <span>V: {m.vibration.toFixed(1)}m/s²</span>
                      <span>RPM: {m.rpm}</span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </aside>

        {/* Machine Details panel */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', overflowY: 'auto' }}>
          
          <div className="machine-detail-grid">
            
            {/* Risk Gauge */}
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
                  <span className="gauge-val" style={{ color: currentRisk >= 70 ? 'var(--danger)' : currentRisk >= 30 ? 'var(--warning)' : 'var(--success)' }}>
                    {currentRisk.toFixed(0)}%
                  </span>
                  <span className="gauge-lbl">Risk</span>
                </div>
              </div>

              <div style={{ marginTop: '10px', textAlign: 'center' }}>
                <h4 style={{ fontSize: '16px', fontWeight: 700 }}>
                  {detail && detail.prediction ? detail.prediction.predicted_failure : 'Normal Operation'}
                </h4>
                {detail && detail.prediction && detail.prediction.time_to_failure !== 'N/A' ? (
                  <p style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '4px', justifyContent: 'center', marginTop: '4px' }}>
                    <Clock size={12} className="text-warning" /> Est. failure: <strong>{detail.prediction.time_to_failure}</strong>
                  </p>
                ) : (
                  <p style={{ fontSize: '12px', color: 'var(--success)', marginTop: '4px' }}>Vitals operating in healthy ranges</p>
                )}
              </div>
            </div>

            {/* Sparkline chart */}
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
                ) : detail && detail.sensor_history && detail.sensor_history.length > 0 ? (
                  <svg viewBox="0 0 500 200" className="sparkline-svg">
                    <defs>
                      <linearGradient id="chart-gradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="var(--primary)" stopOpacity="0.25" />
                        <stop offset="100%" stopColor="var(--primary)" stopOpacity="0" />
                      </linearGradient>
                    </defs>

                    {[40, 80, 120, 160].map((y, idx) => (
                      <line key={idx} x1="20" y1={y} x2="480" y2={y} className="sparkline-grid-line" />
                    ))}

                    <path d={trendData.area} className="sparkline-area" />
                    <path d={trendData.path} className="sparkline-path" />

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

          {/* Recommendations sheet */}
          <div className="glass-card rec-card">
            {recLoading ? (
              <div style={{ display: 'flex', justifyContent: 'center', padding: '40px 0' }}><div className="spinner"></div></div>
            ) : rec && rec.has_recommendation ? (
              <>
                <div className="rec-title-row">
                  <div>
                    <h3 style={{ fontSize: '16px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Wrench size={18} className="text-primary" /> Recommended Mitigation Plan
                    </h3>
                    <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                      Generated: {new Date(rec.created_at).toLocaleString()}
                    </p>
                  </div>
                  <span className={`rec-action-badge ${rec.priority.toLowerCase()}`}>
                    <ShieldAlert size={14} />
                    {rec.priority} Priority (Conf: {rec.confidence}%)
                  </span>
                </div>

                <div className="rec-action-box">
                  <h4 style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.05em' }}>Action Items</h4>
                  <p style={{ fontSize: '13px', marginTop: '6px', lineHeight: '1.5' }}>{rec.recommendation}</p>
                </div>

                <div>
                  <h4 style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.05em', marginBottom: '8px' }}>Required Spare Parts Checklist</h4>
                  
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
        </div>
      </div>
    );
  };

  // 3. Predictions View
  const renderPredictionsPage = () => {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div>
          <h2>Predictive Maintenance Analysis (TensorFlow)</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '4px' }}>
            TensorFlow deep learning models continuously analyze IoT telemetry streams to forecast failure events.
          </p>
        </div>

        {predictionsLoading && predictions.length === 0 ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><div className="spinner"></div></div>
        ) : (
          <div className="predictions-grid">
            {predictions.map((p) => {
              const machineName = machines.find(m => m.machine_id === p.machine_id)?.machine_name || `Machine ${p.machine_id}`;
              const prob = p.failure_probability;
              const riskClass = getRiskClass(prob);
              
              return (
                <div key={p.machine_id} className="glass-card prediction-card">
                  <div className="prediction-header">
                    <span className="prediction-name">{machineName}</span>
                    <span className={`machine-prob-badge ${riskClass}`}>{p.machine_id}</span>
                  </div>
                  
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Failure Risk Score:</span>
                    <span style={{ fontWeight: 700, color: `var(--${riskClass})` }}>{prob}%</span>
                  </div>
                  
                  <div className="prediction-val-bar">
                    <div className={`prediction-val-fill ${riskClass}`} style={{ width: `${prob}%` }}></div>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '12px', marginTop: '4px' }}>
                    <div>
                      <span style={{ color: 'var(--text-secondary)' }}>Forecasted Mode: </span>
                      <strong style={{ color: prob >= 30 ? 'var(--warning)' : 'var(--text-primary)' }}>{p.predicted_failure}</strong>
                    </div>
                    <div>
                      <span style={{ color: 'var(--text-secondary)' }}>Estimated Time: </span>
                      <strong>{p.time_to_failure}</strong>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    );
  };

  // 4. Recommendations View
  const renderRecommendationsPage = () => {
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
            <CheckCircle2 size={36} className="text-success" style={{ marginBottom: '12px' }} />
            <h3>All Systems Operating Normally</h3>
            <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>No active prescriptive repair recommendations found.</p>
          </div>
        ) : (
          <div className="recommendations-grid">
            {recommendations.map((r) => {
              const machineName = machines.find(m => m.machine_id === r.machine_id)?.machine_name || `Machine ${r.machine_id}`;
              return (
                <div key={r.machine_id} className="glass-card rec-card">
                  <div className="rec-title-row">
                    <div>
                      <h3 style={{ fontSize: '16px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Wrench size={16} className="text-primary" /> {machineName} Mitigation Plan
                      </h3>
                      <p style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '2px' }}>
                        Generated: {new Date(r.created_at).toLocaleString()}
                      </p>
                    </div>
                    <span className={`rec-action-badge ${r.priority.toLowerCase()}`}>
                      <ShieldAlert size={12} />
                      {r.priority} Priority (Conf: {r.confidence}%)
                    </span>
                  </div>

                  <div className="rec-action-box">
                    <span style={{ fontSize: '9px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Action Required</span>
                    <p style={{ fontSize: '12px', marginTop: '4px', lineHeight: '1.5' }}>{r.recommendation}</p>
                  </div>

                  <div>
                    <span style={{ fontSize: '9px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Required Spare Parts Checklist</span>
                    {r.parts_status.length === 0 ? (
                      <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>No spare parts required for this maintenance plan.</p>
                    ) : (
                      <table className="parts-table" style={{ marginTop: '6px' }}>
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
                          {r.parts_status.map((p, idx) => (
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
                    <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                      Estimated Duration: <strong>{r.estimated_duration_hours} hours</strong>
                    </span>

                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '6px' }}>
                      {r.parts_missing && (
                        <span style={{ fontSize: '11px', color: 'var(--danger)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <AlertTriangle size={12} /> Out-of-stock parts detected
                        </span>
                      )}
                      <button
                        className="btn-primary"
                        onClick={() => {
                          dispatch(createWorkOrder({
                            machineId: r.machine_id,
                            priority: r.priority,
                            actionRequired: r.recommendation
                          })).then(() => {
                            loadAllRecommendations();
                            dispatch(fetchMachines());
                          });
                        }}
                        disabled={submittingWorkOrder}
                      >
                        <CheckCircle2 size={14} />
                        {submittingWorkOrder ? 'Scheduling...' : 'Authorize Work Order'}
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    );
  };

  // 5. Analytics View
  const renderAnalyticsPage = () => {
    const totalM = machines.length || 1;
    const avgTemp = (machines.reduce((sum, m) => sum + m.temperature, 0) / totalM).toFixed(1);
    const avgPres = (machines.reduce((sum, m) => sum + m.pressure, 0) / totalM).toFixed(0);
    const avgVibr = (machines.reduce((sum, m) => sum + m.vibration, 0) / totalM).toFixed(2);
    const avgRpm = (machines.reduce((sum, m) => sum + m.rpm, 0) / totalM).toFixed(0);

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        <div>
          <h2>System Performance Analytics</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '4px' }}>
            Comprehensive analytics showing plant health status and telemetry averages.
          </p>
        </div>

        <div className="analytics-grid">
          {/* Health Distribution */}
          <div className="glass-card">
            <h3 className="card-title">Health Distribution</h3>
            <div className="analytics-bars-container">
              <div className="analytics-bar-row">
                <div className="analytics-bar-lbl">
                  <span>Healthy</span>
                  <strong>{analytics.healthy}%</strong>
                </div>
                <div className="analytics-bar">
                  <div className="analytics-bar-fill healthy" style={{ width: `${analytics.healthy}%` }}></div>
                </div>
              </div>
              <div className="analytics-bar-row">
                <div className="analytics-bar-lbl">
                  <span>Warning Status</span>
                  <strong>{analytics.warning}%</strong>
                </div>
                <div className="analytics-bar">
                  <div className="analytics-bar-fill warning" style={{ width: `${analytics.warning}%` }}></div>
                </div>
              </div>
              <div className="analytics-bar-row">
                <div className="analytics-bar-lbl">
                  <span>Critical Risk</span>
                  <strong>{analytics.critical}%</strong>
                </div>
                <div className="analytics-bar">
                  <div className="analytics-bar-fill critical" style={{ width: `${analytics.critical}%` }}></div>
                </div>
              </div>
            </div>
          </div>

          {/* Plant Telemetry Averages */}
          <div className="glass-card">
            <h3 className="card-title">Plant Telemetry Averages</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginTop: '10px' }}>
              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '10px', border: '1px solid var(--border-glass)' }}>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>AVG TEMPERATURE</span>
                <div style={{ fontSize: '20px', fontWeight: 800, marginTop: '4px' }}>{avgTemp}°C</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '10px', border: '1px solid var(--border-glass)' }}>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>AVG PRESSURE</span>
                <div style={{ fontSize: '20px', fontWeight: 800, marginTop: '4px' }}>{avgPres} PSI</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '10px', border: '1px solid var(--border-glass)' }}>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>AVG VIBRATION</span>
                <div style={{ fontSize: '20px', fontWeight: 800, marginTop: '4px' }}>{avgVibr} m/s²</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '10px', border: '1px solid var(--border-glass)' }}>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>AVG ROTATIONAL SPEED</span>
                <div style={{ fontSize: '20px', fontWeight: 800, marginTop: '4px' }}>{avgRpm} RPM</div>
              </div>
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
                  <th>Vitals Status</th>
                  <th>Temperature</th>
                  <th>Pressure</th>
                  <th>Vibration</th>
                  <th>Speed</th>
                </tr>
              </thead>
              <tbody>
                {machines.map((m) => (
                  <tr key={m.machine_id}>
                    <td><strong>{m.machine_id}</strong></td>
                    <td>{m.machine_name}</td>
                    <td>
                      <span className={`machine-prob-badge ${m.status === 'Critical' ? 'danger' : m.status === 'Warning' ? 'warning' : 'healthy'}`}>
                        {m.status}
                      </span>
                    </td>
                    <td>{m.temperature.toFixed(1)}°C</td>
                    <td>{m.pressure.toFixed(0)} PSI</td>
                    <td>{m.vibration.toFixed(2)} m/s²</td>
                    <td>{m.rpm} RPM</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  };

  // 6. Solr Incidents Search View
  const renderSearchPage = () => {
    const quickTags = ["Bearing", "Coolant", "Vibration", "Overheat", "Shaft", "M101", "M102"];
    
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div>
          <h2>Historical Incident Database Search</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '4px' }}>
            Query historical incident logs indexed in Apache Solr to find similar signatures and verified actions.
          </p>
        </div>

        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <form onSubmit={handleSearchSubmit} className="search-container" style={{ maxWidth: '100%' }}>
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

          {/* Quick tags */}
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Quick Filters:</span>
            {quickTags.map((tag) => (
              <button
                key={tag}
                onClick={() => {
                  dispatch(setQuery(tag));
                  dispatch(searchIncidents(tag));
                }}
                style={{
                  background: 'rgba(255,255,255,0.03)',
                  border: '1px solid var(--border-glass)',
                  borderRadius: '6px',
                  padding: '4px 10px',
                  color: 'var(--text-secondary)',
                  fontSize: '11px',
                  cursor: 'pointer',
                  transition: 'var(--transition-smooth)'
                }}
                onMouseOver={(e) => e.target.style.background = 'rgba(255,255,255,0.08)'}
                onMouseOut={(e) => e.target.style.background = 'rgba(255,255,255,0.03)'}
              >
                {tag}
              </button>
            ))}
          </div>
        </div>

        {/* Results Container */}
        <div className="glass-card">
          <h3 className="card-title">
            Search Results {searchResults ? `(${searchResults.numFound} logs found)` : ''}
          </h3>

          {searchLoading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><div className="spinner"></div></div>
          ) : searchResults ? (
            <div className="search-results-list">
              {searchResults.docs.length === 0 ? (
                <p style={{ fontSize: '12px', color: 'var(--text-muted)', padding: '20px 0' }}>No historical logs match this search query.</p>
              ) : (
                searchResults.docs.map((doc, idx) => (
                  <div key={doc.id || idx} className="search-result-item">
                    <div style={{ display: 'flex', justifycontent: 'space-between', fontSize: '12px' }}>
                      <strong style={{ color: 'var(--primary)' }}>Machine-{doc.machine_id}</strong>
                      <span style={{ color: 'var(--text-muted)' }}>{new Date(doc.date).toLocaleDateString()}</span>
                    </div>
                    <p style={{ fontSize: '12px', marginTop: '6px' }}>
                      <span style={{ color: 'var(--danger)', fontWeight: 500 }}>Signature:</span> {doc.failure_signature}
                    </p>
                    <p style={{ fontSize: '12px', marginTop: '2px' }}>
                      <span style={{ color: 'var(--success)', fontWeight: 500 }}>Corrective Action:</span> {doc.action_taken}
                    </p>
                    <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                      Outcome: <span style={{ color: doc.outcome === 'Resolved' ? 'var(--success)' : 'var(--warning)' }}>{doc.outcome}</span>
                    </p>
                  </div>
                ))
              )}
            </div>
          ) : (
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', padding: '20px 0' }}>
              Submit a search query or click on a quick filter to query incident archives.
            </p>
          )}
        </div>
      </div>
    );
  };

  const renderActivePage = () => {
    switch (activePage) {
      case 'dashboard':
        return renderDashboardPage();
      case 'machines':
        return renderMachinesPage();
      case 'predictions':
        return renderPredictionsPage();
      case 'recommendations':
        return renderRecommendationsPage();
      case 'analytics':
        return renderAnalyticsPage();
      case 'search':
        return renderSearchPage();
      default:
        return renderDashboardPage();
    }
  };

  return (
    <div className="app-container">
      {/* Header Bar */}
      <header className="app-header">
        <div className="logo-section">
          <Cpu className="logo-icon" size={24} />
          <h1 className="logo-text">FixForesight</h1>
        </div>

        {/* Header Search Form redirects/syncs with Search page tab */}
        <form onSubmit={handleSearchSubmit} className="search-container">
          <Search size={16} className="text-secondary" />
          <input
            type="text"
            className="search-input"
            placeholder="Search incident logs (e.g. bearing, coolant)..."
            value={searchQuery}
            onChange={(e) => dispatch(setQuery(e.target.value))}
          />
          {searchQuery && (
            <button type="button" onClick={handleClearSearch} style={{ background: 'transparent', border: 'none', color: '#64748b', cursor: 'pointer', fontSize: '11px' }}>
              Clear
            </button>
          )}
        </form>

        {/* Infrastructure Status */}
        <div className="system-status">
          <div className="status-badge" style={{ borderColor: 'rgba(255,255,255,0.12)', fontSize: '11px' }}>
            Analytics: <span style={{color:'var(--success)', marginLeft:'4px'}}>{analytics.healthy}% H</span> | <span style={{color:'var(--warning)'}}>{analytics.warning}% W</span> | <span style={{color:'var(--danger)'}}>{analytics.critical}% C</span>
          </div>
          <div className="status-badge" title="FastAPI API Status">
            <Wifi size={13} className={sysHealth.status !== 'offline' ? 'text-success' : 'text-danger'} />
            API: <span style={{ color: sysHealth.status !== 'offline' ? '#10b981' : '#f43f5e' }}>{sysHealth.status}</span>
          </div>
          <div className="status-badge" title="PostgreSQL DB Status">
            <Database size={13} className={sysHealth.postgres.includes('healthy') ? 'text-success' : 'text-danger'} />
            DB
          </div>
          <button className="status-badge" onClick={checkHealth} style={{ cursor: 'pointer', border: '1px solid var(--border-glass)', outline: 'none' }}>
            <RefreshCw size={12} />
          </button>
        </div>
      </header>

      {/* Main Grid: Sidebar + Sub-page Content */}
      <main className="dashboard-grid">
        
        {/* Left Side-Navigation Bar */}
        <aside className="nav-sidebar">
          <div style={{ display: 'flex', flexDirection: 'column', height: '100%', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div className={`nav-item ${activePage === 'dashboard' ? 'active' : ''}`} onClick={() => setActivePage('dashboard')}>
                <LayoutDashboard size={18} />
                <span>Dashboard</span>
              </div>
              <div className={`nav-item ${activePage === 'machines' ? 'active' : ''}`} onClick={() => setActivePage('machines')}>
                <Cpu size={18} />
                <span>Machines</span>
              </div>
              <div className={`nav-item ${activePage === 'predictions' ? 'active' : ''}`} onClick={() => setActivePage('predictions')}>
                <FileText size={18} />
                <span>Predictions</span>
              </div>
              <div className={`nav-item ${activePage === 'recommendations' ? 'active' : ''}`} onClick={() => setActivePage('recommendations')}>
                <Wrench size={18} />
                <span>Recommendations</span>
              </div>
              <div className={`nav-item ${activePage === 'analytics' ? 'active' : ''}`} onClick={() => setActivePage('analytics')}>
                <TrendingUp size={18} />
                <span>Analytics</span>
              </div>
              <div className={`nav-item ${activePage === 'search' ? 'active' : ''}`} onClick={() => setActivePage('search')}>
                <Search size={18} />
                <span>Search Logs</span>
              </div>
            </div>
            <div style={{ padding: '10px', fontSize: '11px', color: 'var(--text-muted)', borderTop: '1px solid var(--border-glass)' }}>
              <span>v1.2.0 • Production</span>
            </div>
          </div>
        </aside>

        {/* Active Page Viewport wrapper */}
        <section className="page-content">
          {renderActivePage()}
        </section>

      </main>
    </div>
  );
}
