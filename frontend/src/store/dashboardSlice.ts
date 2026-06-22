import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import * as dashboardService from '../services/dashboardService';
import { DashboardResponse } from '../types';

interface DashboardState {
  data: DashboardResponse | null;
  loading: boolean;
  error: string | null;
}

const initialState: DashboardState = {
  data: null,
  loading: false,
  error: null
};

export const fetchDashboardData = createAsyncThunk(
  'dashboard/fetchDashboardData',
  async (_, { rejectWithValue }) => {
    try {
      return await dashboardService.getDashboardData();
    } catch (err: any) {
      return rejectWithValue(err.message);
    }
  }
);

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchDashboardData.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDashboardData.fulfilled, (state, action: PayloadAction<DashboardResponse>) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchDashboardData.rejected, (state, action: any) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch dashboard data';
      });
  }
});

export default dashboardSlice.reducer;
