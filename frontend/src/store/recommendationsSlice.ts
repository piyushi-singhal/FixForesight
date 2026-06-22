import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import * as recommendationService from '../services/recommendationService';
import { RecommendationResponse } from '../types';

interface RecommendationsState {
  list: RecommendationResponse[];
  activeMachineRec: any;
  loading: boolean;
  activeLoading: boolean;
  error: string | null;
  activeError: string | null;
}

const initialState: RecommendationsState = {
  list: [],
  activeMachineRec: null,
  loading: false,
  activeLoading: false,
  error: null,
  activeError: null
};

export const fetchRecommendations = createAsyncThunk(
  'recommendations/fetchRecommendations',
  async (_, { rejectWithValue }) => {
    try {
      const list = await recommendationService.getRecommendations();
      const detailedList = await Promise.all(
        list.map(async (r) => {
          try {
            const detail = await recommendationService.getMachineRecommendations(r.machine_id);
            return detail;
          } catch (err) {
            return {
              machine_id: r.machine_id,
              has_recommendation: true,
              recommendation: r.recommendation,
              priority: r.priority,
              confidence: r.confidence,
              parts_status: [],
              parts_missing: false,
              estimated_duration_hours: 4,
              created_at: r.created_at
            };
          }
        })
      );
      return detailedList;
    } catch (err: any) {
      return rejectWithValue(err.message);
    }
  }
);

export const fetchMachineRecommendations = createAsyncThunk(
  'recommendations/fetchMachineRecommendations',
  async (machineId: string, { rejectWithValue }) => {
    try {
      return await recommendationService.getMachineRecommendations(machineId);
    } catch (err: any) {
      return rejectWithValue(err.message);
    }
  }
);

const recommendationsSlice = createSlice({
  name: 'recommendations',
  initialState,
  reducers: {
    clearActiveMachineRec: (state) => {
      state.activeMachineRec = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // fetchRecommendations
      .addCase(fetchRecommendations.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRecommendations.fulfilled, (state, action: PayloadAction<RecommendationResponse[]>) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchRecommendations.rejected, (state, action: any) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch recommendations';
      })
      // fetchMachineRecommendations
      .addCase(fetchMachineRecommendations.pending, (state) => {
        state.activeLoading = true;
        state.activeError = null;
      })
      .addCase(fetchMachineRecommendations.fulfilled, (state, action: PayloadAction<any>) => {
        state.activeLoading = false;
        state.activeMachineRec = action.payload;
      })
      .addCase(fetchMachineRecommendations.rejected, (state, action: any) => {
        state.activeLoading = false;
        state.activeError = action.payload || 'Failed to fetch machine recommendations';
      });
  }
});

export const { clearActiveMachineRec } = recommendationsSlice.actions;
export default recommendationsSlice.reducer;
