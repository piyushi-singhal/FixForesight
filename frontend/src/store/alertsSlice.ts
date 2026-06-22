import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import * as alertService from '../services/alertService';
import { AlertResponse } from '../services/alertService';

interface AlertsState {
  list: AlertResponse[];
  loading: boolean;
  error: string | null;
}

const initialState: AlertsState = {
  list: [],
  loading: false,
  error: null
};

export const fetchAlerts = createAsyncThunk(
  'alerts/fetchAlerts',
  async (_, { rejectWithValue }) => {
    try {
      return await alertService.getAlerts();
    } catch (err: any) {
      return rejectWithValue(err.message);
    }
  }
);

const alertsSlice = createSlice({
  name: 'alerts',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchAlerts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAlerts.fulfilled, (state, action: PayloadAction<AlertResponse[]>) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchAlerts.rejected, (state, action: any) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch alerts';
      });
  }
});

export default alertsSlice.reducer;
