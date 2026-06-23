import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import * as searchService from '../services/searchService';
import { SearchResponse } from '../services/searchService';

interface SearchState {
  query: string;
  results: SearchResponse | null;
  loading: boolean;
  error: string | null;
}

const initialState: SearchState = {
  query: '',
  results: null,
  loading: false,
  error: null
};

export const searchIncidents = createAsyncThunk(
  'search/searchIncidents',
  async (query: string, { rejectWithValue }) => {
    try {
      return await searchService.searchIncidents(query);
    } catch (err: any) {
      return rejectWithValue(err.message);
    }
  }
);

const searchSlice = createSlice({
  name: 'search',
  initialState,
  reducers: {
    setQuery: (state, action: PayloadAction<string>) => {
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
      .addCase(searchIncidents.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(searchIncidents.fulfilled, (state, action: PayloadAction<SearchResponse>) => {
        state.loading = false;
        state.results = action.payload;
      })
      .addCase(searchIncidents.rejected, (state, action: any) => {
        state.loading = false;
        state.error = action.payload || 'Search failed';
      });
  }
});

export const { setQuery, clearSearch } = searchSlice.actions;
export default searchSlice.reducer;
