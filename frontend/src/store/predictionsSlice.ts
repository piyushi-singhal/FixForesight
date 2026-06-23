import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import * as predictionService from '../services/predictionService';
import { PredictionResponse } from '../types';

interface PredictionsState {
  list: PredictionResponse[];
  loading: boolean;
  error: string | null;
}

const initialState: PredictionsState = {
  list: [],
  loading: false,
  error: null
};

export const fetchPredictions = createAsyncThunk(
  'predictions/fetchPredictions',
  async (_, { rejectWithValue }) => {
    try {
      return await predictionService.getPredictions();
    } catch (err: any) {
      return rejectWithValue(err.message);
    }
  }
);

const predictionsSlice = createSlice({
  name: 'predictions',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchPredictions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPredictions.fulfilled, (state, action: PayloadAction<PredictionResponse[]>) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchPredictions.rejected, (state, action: any) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch predictions';
      });
  }
});

export default predictionsSlice.reducer;
