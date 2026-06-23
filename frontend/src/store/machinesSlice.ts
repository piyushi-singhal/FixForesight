import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import * as machineService from '../services/machineService';
import { MachinePrediction } from '../types';

interface MachinesState {
  list: MachinePrediction[];
  activeMachineId: string;
  detail: any;
  loading: boolean;
  detailLoading: boolean;
  error: string | null;
  detailError: string | null;
}

const initialState: MachinesState = {
  list: [],
  activeMachineId: 'M101',
  detail: null,
  loading: false,
  detailLoading: false,
  error: null,
  detailError: null
};

export const fetchMachines = createAsyncThunk(
  'machines/fetchMachines',
  async (_, { rejectWithValue }) => {
    try {
      return await machineService.getMachines();
    } catch (err: any) {
      return rejectWithValue(err.message);
    }
  }
);

export const fetchMachineRisk = createAsyncThunk(
  'machines/fetchMachineRisk',
  async (machineId: string, { rejectWithValue }) => {
    try {
      return await machineService.getMachineRisk(machineId);
    } catch (err: any) {
      return rejectWithValue(err.message);
    }
  }
);

const machinesSlice = createSlice({
  name: 'machines',
  initialState,
  reducers: {
    setActiveMachineId: (state, action: PayloadAction<string>) => {
      state.activeMachineId = action.payload;
    }
  },
  extraReducers: (builder) => {
    builder
      // fetchMachines
      .addCase(fetchMachines.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMachines.fulfilled, (state, action: PayloadAction<MachinePrediction[]>) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchMachines.rejected, (state, action: any) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch machines';
      })
      // fetchMachineRisk
      .addCase(fetchMachineRisk.pending, (state) => {
        state.detailLoading = true;
        state.detailError = null;
      })
      .addCase(fetchMachineRisk.fulfilled, (state, action: PayloadAction<any>) => {
        state.detailLoading = false;
        state.detail = action.payload;
      })
      .addCase(fetchMachineRisk.rejected, (state, action: any) => {
        state.detailLoading = false;
        state.detailError = action.payload || 'Failed to fetch machine risk';
      });
  }
});

export const { setActiveMachineId } = machinesSlice.actions;
export default machinesSlice.reducer;
