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
  XCircle,
  ClipboardList
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
  resetWorkOrderStatus,
  fetchWorkOrders,
  fetchPredictions,
  fetchRecommendations,
  fetchDashboardData
} from './store';

import { getAnalytics } from './services/analyticsService';

export default function App() {
  const dispatch = useDispatch();

  const getMachineName = (id) => {
    const names = {
      'M101': 'CNC Spindle Unit',
      'M102': 'Hydraulic Press',
      'M103': 'Injection Molder',
      'M104': 'Robotic Arm Axis 3',
      'M105': 'Cooling Compressor'
    };
    return names[id] || `Machine ${id}`;
  };

  const getMachineStatus = (failureProbability) => {
    if (failureProbability >= 0.8) return 'Critical';
    if (failureProbability >= 0.3) return 'Warning';
    return 'Healthy';
  };

  const getMachineModel = (id) => {
    const models = {
      'M101': 'M-450 Spindle',
      'M102': 'H-200 Press',
      'M103': 'IM-600 Molder',
      'M104': 'RA-3 Axis Controller',
      'M105': 'CC-800 Compressor'
    };
    return models[id] || 'N/A';
  };

  const getMachineLocation = (id) => {
    const locations = {
      'M101': 'Aisle 3, Bay A',
      'M102': 'Aisle 1, Bay C',
      'M103': 'Aisle 2, Bay B',
      'M104': 'Assembly Line 4',
      'M105': 'Utility Plant Room'
    };
    return locations[id] || 'N/A';
  };
  
  // Redux Selectors
  const machines = useSelector((state) => state.machines.list);
  const activeId = useSelector((state) => state.machines.activeMachineId);
  const machinesLoading = useSelector((state) => state.machines.loading);
  
  const detail = useSelector((state) => state.machines.detail);
  const detailLoading = useSelector((state) => state.machines.detailLoading);
  
  const rec = useSelector((state) => state.recommendations.activeMachineRec);
  const recLoading = useSelector((state) => state.recommendations.activeLoading);
  const workOrderSuccess = useSelector((state) => state.workOrders.success);
  const submittingWorkOrder = useSelector((state) => state.workOrders.submitting);

  const alerts = useSelector((state) => state.alerts.list);
  const workOrders = useSelector((state) => state.workOrders.list);
  const workOrdersLoading = useSelector((state) => state.workOrders.loading);
  
  const searchQuery = useSelector((state) => state.search.query);
  const searchResults = useSelector((state) => state.search.results);
  const searchLoading = useSelector((state) => state.search.loading);

  const predictions = useSelector((state) => state.predictions.list);
  const predictionsLoading = useSelector((state) => state.predictions.loading);
  
  const recommendations = useSelector((state) => state.recommendations.list);
  const recsLoading = useSelector((state) => state.recommendations.loading);
  
  const dashboardData = useSelector((state) => state.dashboard.data);
  const dashboardLoading = useSelector((state) => state.dashboard.loading);

  // Local State for Tabs / Navigation / Custom Page Data
  const [activePage, setActivePage] = useState('dashboard'); // dashboard, machines, predictions, recommendations, work-orders, analytics, search
  const [activeTab, setActiveTab] = useState('air_temperature'); // air_temperature, process_temperature, rotational_speed, torque, tool_wear
  const [sysHealth, setSysHealth] = useState({ status: 'healthy', postgres: 'healthy', localstack: 'healthy', solr: 'healthy' });
  const [analytics, setAnalytics] = useState({ healthy: 60, warning: 40, critical: 0 });

  // Resolve backend API URL dynamically
  const apiBase = window.location.port === '3000'
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : window.location.origin;

  // Initial and poll fetching
  useEffect(() => {
    dispatch(fetchMachines());
    dispatch(fetchAlerts());
    dispatch(fetchWorkOrders());
    dispatch(fetchDashboardData());
    dispatch(fetchPredictions());
    dispatch(fetchRecommendations());
    checkHealth();

    const interval = setInterval(() => {
      dispatch(fetchMachines());
      dispatch(fetchAlerts());
      dispatch(fetchWorkOrders());
      dispatch(fetchDashboardData());
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
      dispatch(fetchPredictions());
    } else if (activePage === 'recommendations') {
      dispatch(fetchRecommendations());
    } else if (activePage === 'work-orders') {
      dispatch(fetchWorkOrders());
    } else if (activePage === 'analytics') {
      checkHealth();
    } else if (activePage === 'dashboard') {
      dispatch(fetchDashboardData());
    }
  }, [activePage, dispatch]);

  // Authorization feedback
  useEffect(() => {
    if (workOrderSuccess) {
      alert("Work Order generated successfully!");
      dispatch(resetWorkOrderStatus());
      dispatch(fetchMachines());
      dispatch(fetchWorkOrders());
      if (activeId) {
        dispatch(fetchMachineRisk(activeId));
        dispatch(fetchMachineRecommendations(activeId));
      }
      dispatch(fetchPredictions());
      dispatch(fetchRecommendations());
    }
  }, [workOrderSuccess, dispatch, activeId]);

  const checkHealth = async () => {
    try {
      // Route health check via FastAPI
      const response = await fetch(`${apiBase}/health`);
      if (response.ok) {
        const data = await response.json();
        setSysHealth(data);
      }
      
      // Route global analytics via Service Layer
      const analData = await getAnalytics();
      setAnalytics(analData);
    } catch (e) {
      setSysHealth({ status: 'offline', postgres: 'unhealthy', localstack: 'unhealthy', solr: 'unhealthy' });
    }
  };



  const handleMachineSelect = (id) => {
    dispatch(setActiveMachineId(id));
    setActivePage('machine-details');
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
      actionRequired: rec.recommendation,
      recommendationId: rec.recommendation_id
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

    const values = history.map(h => h[key] || 0);
    const maxVal = Math.max(...values, 1) * 1.05;
    const minVal = Math.min(...values, 0) * 0.95;
    const valRange = maxVal - minVal || 1;

    const points = history.map((h, i) => {
      const x = padding + (i * (width - padding * 2)) / (history.length - 1);
      const val = h[key] || 0;
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

  const isPointAnomaly = (tab, val) => {
    if (tab === 'air_temperature' && val > 303.0) return true;
    if (tab === 'process_temperature' && val > 313.0) return true;
    if (tab === 'rotational_speed' && (val > 2200 || val < 1100)) return true;
    if (tab === 'torque' && val > 65.0) return true;
    if (tab === 'tool_wear' && val > 180.0) return true;
    if (tab === 'failure_probability' && val > 50.0) return true;
    return false;
  };

  const trendData = detail ? getSvgPathData(detail.sensor_history, activeTab) : { path: '', area: '', points: [] };
  const currentRisk = detail && detail.prediction ? detail.prediction.failure_probability : 5;
  const strokeDash = (currentRisk / 100.0) * 439.6;

  // ================= VIEW RENDERS =================

  // 1. Dashboard View
  const renderDashboardPage = () => {
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
            <div className="metric-icon-box style={{ background: 'var(--primary-glow)', color: 'var(--primary)' }}">
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
                      onClick={() => handleMachineSelect(m.machine_id)}
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
  };

  // 2. Machines Directory & Analytics View
  const renderMachinesPage = () => {
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
                        onClick={() => handleMachineSelect(m.machine_id)}
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
  };

  // Machine Details Page View
  const renderMachineDetailsPage = () => {
    if (!activeId) {
      return (
        <div className="glass-card" style={{ padding: '28px', textAlign: 'center' }}>
          <h3>No Asset Selected</h3>
          <p style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>Please select a machine from the Assets Directory.</p>
          <button onClick={() => setActivePage('machines')} className="btn-primary" style={{ marginTop: '16px', marginInline: 'auto' }}>
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

    const isVitalAnomalous = (key, val) => {
      return isPointAnomaly(key, val);
    };

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
        {/* Header section with back button */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <button 
              onClick={() => setActivePage('machines')} 
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
                  const anomalous = isVitalAnomalous(item.key, item.rawVal);
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
                      onClick={handleCreateWorkOrder}
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
                        onClick={() => handleMachineSelect(p.machine_id)}
                        className="clickable-row"
                        style={{ cursor: 'pointer' }}
                      >
                        <td><strong>{p.machine_id}</strong></td>
                        <td>{p.air_temperature ? `${p.air_temperature.toFixed(1)}°C` : 'N/A'}</td>
                        <td>{p.process_temperature ? `${p.process_temperature.toFixed(1)}°C` : 'N/A'}</td>
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
                      onClick={() => handleMachineSelect(r.machine_id)}
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
  };

  // 5. Work Orders View
  const renderWorkOrdersPage = () => {
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
            <CheckCircle2 size={36} className="text-success" style={{ marginBottom: '12px' }} />
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
                            onClick={() => handleMachineSelect(wo.machine_id)}
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
  };

  // 6. Analytics View
  const renderAnalyticsPage = () => {
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
          <div style={{ display: 'flex', justifycontent: 'space-between', fontSize: '11px', color: 'var(--text-secondary)' }}>
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
              <div style={{ fontSize: '18px', fontWeight: 800, marginTop: '4px' }}>{avgAirTemp}°C</div>
            </div>
            <div style={{ background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '10px', border: '1px solid var(--border-glass)' }}>
              <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontWeight: 600 }}>PROCESS TEMPERATURE (AVG)</span>
              <div style={{ fontSize: '18px', fontWeight: 800, marginTop: '4px' }}>{avgProcTemp}°C</div>
            </div>
            <div style={{ background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '10px', border: '1px solid var(--border-glass)' }}>
              <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontWeight: 600 }}>ROTATIONAL SPEED (AVG)</span>
              <div style={{ fontSize: '18px', fontWeight: 800, marginTop: '4px' }}>{avgSpeed} RPM</div>
            </div>
            <div style={{ background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '10px', border: '1px solid var(--border-glass)' }}>
              <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontWeight: 600 }}>TORQUE (AVG)</span>
              <div style={{ fontSize: '18px', fontWeight: 800, marginTop: '4px' }}>{avgTorque} Nm</div>
            </div>
            <div style={{ background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '10px', border: '1px solid var(--border-glass)', gridColumn: 'span 2' }}>
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
                    <td>{m.air_temperature.toFixed(1)}°C</td>
                    <td>{m.process_temperature.toFixed(1)}°C</td>
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
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                      <strong 
                        onClick={() => handleMachineSelect(doc.machine_id)}
                        style={{ color: 'var(--primary)', cursor: 'pointer', textDecoration: 'underline' }}
                      >
                        Machine-{doc.machine_id}
                      </strong>
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
      case 'machine-details':
        return renderMachineDetailsPage();
      case 'predictions':
        return renderPredictionsPage();
      case 'recommendations':
        return renderRecommendationsPage();
      case 'work-orders':
        return renderWorkOrdersPage();
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
              <div className={`nav-item ${activePage === 'work-orders' ? 'active' : ''}`} onClick={() => setActivePage('work-orders')}>
                <ClipboardList size={18} />
                <span>Work Orders</span>
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
