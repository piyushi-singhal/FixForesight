import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Activity,
  AlertTriangle,
  Cpu,
  Database,
  FileText,
  LayoutDashboard,
  RefreshCw,
  Search as SearchIcon,
  TrendingUp,
  Wifi,
  Wrench,
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

// Import refactored page components
import Dashboard from './pages/Dashboard';
import Machines from './pages/Machines';
import MachineDetails from './pages/MachineDetails';
import Predictions from './pages/Predictions';
import Recommendations from './pages/Recommendations';
import Alerts from './pages/Alerts';
import WorkOrders from './pages/WorkOrders';
import Analytics from './pages/Analytics';
import Search from './pages/Search';

export default function App() {
  const dispatch = useDispatch();

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
  const alertsLoading = useSelector((state) => state.alerts.loading);
  const workOrders = useSelector((state) => state.workOrders.list);
  const workOrdersLoading = useSelector((state) => state.workOrders.loading);
  
  const searchQuery = useSelector((state) => state.search.query);
  const searchResults = useSelector((state) => state.search.results);
  const searchLoading = useSelector((state) => state.search.loading);

  const predictions = useSelector((state) => state.predictions.list);
  const predictionsLoading = useSelector((state) => state.predictions.loading);
  
  const recommendations = useSelector((state) => state.recommendations.list);
  const recsLoading = useSelector((state) => state.recommendations.loading);
  
  // Local State
  const [activePage, setActivePage] = useState('dashboard'); // dashboard, machines, machine-details, predictions, recommendations, alerts, work-orders, analytics, search
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
    } else if (activePage === 'alerts') {
      dispatch(fetchAlerts());
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
      const response = await fetch(`${apiBase}/health`);
      if (response.ok) {
        const data = await response.json();
        setSysHealth(data);
      }
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

  const renderActivePage = () => {
    switch (activePage) {
      case 'dashboard':
        return <Dashboard machines={machines} onMachineSelect={handleMachineSelect} />;
      case 'machines':
        return (
          <Machines
            machines={machines}
            machinesLoading={machinesLoading}
            activeId={activeId}
            onMachineSelect={handleMachineSelect}
          />
        );
      case 'machine-details':
        return (
          <MachineDetails
            activeId={activeId}
            machines={machines}
            detail={detail}
            detailLoading={detailLoading}
            rec={rec}
            recLoading={recLoading}
            workOrders={workOrders}
            submittingWorkOrder={submittingWorkOrder}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            onBack={() => setActivePage('machines')}
            onCreateWorkOrder={handleCreateWorkOrder}
          />
        );
      case 'predictions':
        return <Predictions predictions={predictions} predictionsLoading={predictionsLoading} onMachineSelect={handleMachineSelect} />;
      case 'recommendations':
        return <Recommendations recommendations={recommendations} recsLoading={recsLoading} onMachineSelect={handleMachineSelect} />;
      case 'alerts':
        return <Alerts alerts={alerts} alertsLoading={alertsLoading} onMachineSelect={handleMachineSelect} />;
      case 'work-orders':
        return <WorkOrders workOrders={workOrders} workOrdersLoading={workOrdersLoading} onMachineSelect={handleMachineSelect} />;
      case 'analytics':
        return <Analytics machines={machines} recommendations={recommendations} />;
      case 'search':
        return (
          <Search
            searchQuery={searchQuery}
            searchResults={searchResults}
            searchLoading={searchLoading}
            onMachineSelect={handleMachineSelect}
            onSearchSubmit={handleSearchSubmit}
            onClearSearch={handleClearSearch}
          />
        );
      default:
        return <Dashboard machines={machines} onMachineSelect={handleMachineSelect} />;
    }
  };

  return (
    <div className="app-container">
      {/* Header Bar */}
      <header className="app-header">
        <div className="logo-section" style={{ cursor: 'pointer' }} onClick={() => setActivePage('dashboard')}>
          <Cpu className="logo-icon" size={24} />
          <h1 className="logo-text">FixForesight</h1>
        </div>

        {/* Header Search Form redirects/syncs with Search page tab */}
        <form onSubmit={handleSearchSubmit} className="search-container">
          <SearchIcon size={16} className="text-secondary" />
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
            <Database size={13} className={sysHealth.postgres && sysHealth.postgres.includes('healthy') ? 'text-success' : 'text-danger'} />
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
              <div className={`nav-item ${activePage === 'machines' || activePage === 'machine-details' ? 'active' : ''}`} onClick={() => setActivePage('machines')}>
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
              <div className={`nav-item ${activePage === 'alerts' ? 'active' : ''}`} onClick={() => setActivePage('alerts')}>
                <AlertTriangle size={18} />
                <span>Alerts</span>
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
                <SearchIcon size={18} />
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
