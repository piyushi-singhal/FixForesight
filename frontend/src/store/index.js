import { configureStore, createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import * as machineService from '../services/machineService';
import * as recommendationService from '../services/recommendationService';
import * as alertService from '../services/alertService';
import * as searchService from '../services/searchService';

// Async Thunks
export const fetchMachines = createAsyncThunk(
  'machines/fetchMachines',
  async (_, { rejectWithValue }) => {
    try {
      return await machineService.getMachines();
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

export const fetchMachineRisk = createAsyncThunk(
  'detail/fetchMachineRisk',
  async (machineId, { rejectWithValue }) => {
    try {
      return await machineService.getMachineRisk(machineId);
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

export const fetchMachineRecommendations = createAsyncThunk(
  'recommendation/fetchMachineRecommendations',
  async (machineId, { rejectWithValue }) => {
    try {
      return await recommendationService.getMachineRecommendations(machineId);
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

export const createWorkOrder = createAsyncThunk(
  'recommendation/createWorkOrder',
  async ({ machineId, priority, actionRequired }, { rejectWithValue }) => {
    try {
      return await recommendationService.createWorkOrder(machineId, priority, actionRequired);
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

export const fetchAlerts = createAsyncThunk(
  'alerts/fetchAlerts',
  async (_, { rejectWithValue }) => {
    try {
      return await alertService.getAlerts();
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

export const searchIncidents = createAsyncThunk(
  'search/searchIncidents',
  async (query, { rejectWithValue }) => {
    try {
      return await searchService.searchIncidents(query);
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

export const fetchWorkOrders = createAsyncThunk(
  'workOrders/fetchWorkOrders',
  async (_, { rejectWithValue }) => {
    try {
      return await recommendationService.getWorkOrders();
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

// Slices
const machinesSlice = createSlice({
  name: 'machines',
  initialState: {
    list: [],
    activeMachineId: 'M101',
    loading: false,
    error: null
  },
  reducers: {
    setActiveMachineId: (state, action) => {
      state.activeMachineId = action.payload;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchMachines.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(fetchMachines.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchMachines.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  }
});

const detailSlice = createSlice({
  name: 'detail',
  initialState: {
    data: null,
    loading: false,
    error: null
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchMachineRisk.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(fetchMachineRisk.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchMachineRisk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  }
});

const recommendationSlice = createSlice({
  name: 'recommendation',
  initialState: {
    data: null,
    loading: false,
    submittingWorkOrder: false,
    workOrderSuccess: false,
    error: null
  },
  reducers: {
    resetWorkOrderStatus: (state) => {
      state.workOrderSuccess = false;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchMachineRecommendations.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(fetchMachineRecommendations.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchMachineRecommendations.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(createWorkOrder.pending, (state) => { state.submittingWorkOrder = true; })
      .addCase(createWorkOrder.fulfilled, (state) => {
        state.submittingWorkOrder = false;
        state.workOrderSuccess = true;
      })
      .addCase(createWorkOrder.rejected, (state, action) => {
        state.submittingWorkOrder = false;
        state.error = action.payload;
      });
  }
});

const alertsSlice = createSlice({
  name: 'alerts',
  initialState: {
    list: [],
    loading: false,
    error: null
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchAlerts.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(fetchAlerts.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchAlerts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  }
});

const searchSlice = createSlice({
  name: 'search',
  initialState: {
    query: '',
    results: null,
    loading: false,
    error: null
  },
  reducers: {
    setQuery: (state, action) => {
      state.query = action.payload;
    },
    clearSearch: (state) => {
      state.query = '';
      state.results = null;
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(searchIncidents.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(searchIncidents.fulfilled, (state, action) => {
        state.loading = false;
        state.results = action.payload;
      })
      .addCase(searchIncidents.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  }
});

const workOrdersSlice = createSlice({
  name: 'workOrders',
  initialState: {
    list: [],
    loading: false,
    error: null
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchWorkOrders.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(fetchWorkOrders.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchWorkOrders.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  }
});

// Configure and Export Store
export const store = configureStore({
  reducer: {
    machines: machinesSlice.reducer,
    detail: detailSlice.reducer,
    recommendation: recommendationSlice.reducer,
    alerts: alertsSlice.reducer,
    search: searchSlice.reducer,
    workOrders: workOrdersSlice.reducer
  }
});

export const { setActiveMachineId } = machinesSlice.actions;
export const { resetWorkOrderStatus } = recommendationSlice.actions;
export const { setQuery, clearSearch } = searchSlice.actions;
