import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import * as workOrderService from '../services/workOrderService';
import { WorkOrderResponse } from '../types';

interface WorkOrdersState {
  list: WorkOrderResponse[];
  loading: boolean;
  submitting: boolean;
  success: boolean;
  error: string | null;
}

const initialState: WorkOrdersState = {
  list: [],
  loading: false,
  submitting: false,
  success: false,
  error: null
};

export const fetchWorkOrders = createAsyncThunk(
  'workOrders/fetchWorkOrders',
  async (_, { rejectWithValue }) => {
    try {
      return await workOrderService.getWorkOrders();
    } catch (err: any) {
      return rejectWithValue(err.message);
    }
  }
);

export const createWorkOrder = createAsyncThunk(
  'workOrders/createWorkOrder',
  async ({ machineId, priority, actionRequired }: { machineId: string; priority: string; actionRequired: string }, { rejectWithValue }) => {
    try {
      return await workOrderService.createWorkOrder(machineId, priority, actionRequired);
    } catch (err: any) {
      return rejectWithValue(err.message);
    }
  }
);

const workOrdersSlice = createSlice({
  name: 'workOrders',
  initialState,
  reducers: {
    resetWorkOrderStatus: (state) => {
      state.success = false;
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // fetchWorkOrders
      .addCase(fetchWorkOrders.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchWorkOrders.fulfilled, (state, action: PayloadAction<WorkOrderResponse[]>) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchWorkOrders.rejected, (state, action: any) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch work orders';
      })
      // createWorkOrder
      .addCase(createWorkOrder.pending, (state) => {
        state.submitting = true;
        state.success = false;
        state.error = null;
      })
      .addCase(createWorkOrder.fulfilled, (state) => {
        state.submitting = false;
        state.success = true;
      })
      .addCase(createWorkOrder.rejected, (state, action: any) => {
        state.submitting = false;
        state.success = false;
        state.error = action.payload || 'Failed to create work order';
      });
  }
});

export const { resetWorkOrderStatus } = workOrdersSlice.actions;
export default workOrdersSlice.reducer;
