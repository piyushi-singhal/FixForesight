import { configureStore } from '@reduxjs/toolkit';
import { useDispatch, useSelector, TypedUseSelectorHook } from 'react-redux';

// Import reducers
import machinesReducer from './machinesSlice';
import predictionsReducer from './predictionsSlice';
import recommendationsReducer from './recommendationsSlice';
import workOrdersReducer from './workOrdersSlice';
import dashboardReducer from './dashboardSlice';
import alertsReducer from './alertsSlice';
import searchReducer from './searchSlice';

// Configure store
export const store = configureStore({
  reducer: {
    machines: machinesReducer,
    predictions: predictionsReducer,
    recommendations: recommendationsReducer,
    workOrders: workOrdersReducer,
    dashboard: dashboardReducer,
    alerts: alertsReducer,
    search: searchReducer
  }
});

// RootState and AppDispatch types
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Custom hooks for dispatch and selector
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// Re-export slice actions and thunks for App.jsx compatibility
export {
  fetchMachines,
  fetchMachineRisk,
  setActiveMachineId
} from './machinesSlice';

export {
  fetchPredictions
} from './predictionsSlice';

export {
  fetchRecommendations,
  fetchMachineRecommendations,
  clearActiveMachineRec
} from './recommendationsSlice';

export {
  fetchWorkOrders,
  createWorkOrder,
  resetWorkOrderStatus
} from './workOrdersSlice';

export {
  fetchDashboardData
} from './dashboardSlice';

export {
  fetchAlerts
} from './alertsSlice';

export {
  searchIncidents,
  setQuery,
  clearSearch
} from './searchSlice';
