# API Integration

## Base URL

`frontend/src/services/apiConfig.js`:
```javascript
export const API_BASE_URL = "http://localhost:8000";
```

In Docker, the frontend container talks to `backend` via the Docker network. The nginx config proxies or the JavaScript directly calls the host-mapped port.

## Service Functions

All service files follow this pattern:
```typescript
export const getAlerts = async (): Promise<AlertResponse[]> => {
  const res = await fetch(`${API_BASE_URL}/alerts`);
  if (!res.ok) throw new Error("Failed to fetch alerts");
  return res.json();
};
```

## Error Handling

Each Redux slice handles errors via `createAsyncThunk` rejected state:
```typescript
.addCase(fetchMachines.rejected, (state, action) => {
  state.loading = false;
  state.error = action.error.message || "Failed to fetch machines";
})
```

## API Endpoints Used by Frontend

| Page/Feature | Endpoint | Method |
|---|---|---|
| Dashboard | `/dashboard` | GET |
| Machine fleet | `/machines` | GET |
| Machine risk | `/machines/{id}/risk` | GET |
| Machine recs | `/machines/{id}/recommendations` | GET |
| Predictions | `/predictions` | GET |
| Recommendations | `/recommendations` | GET |
| Alerts | `/alerts` | GET |
| Work orders list | `/work-orders` | GET |
| Create work order | `/work-orders` | POST |
| Update work order | `/work-orders/{id}/status` | PATCH |
| Analytics summary | `/analytics` | GET |
| Feature importance | `/analytics/feature-importance` | GET |
| Model monitoring | `/analytics/model-monitoring` | GET |
| Search | `/search?q={query}` | GET |
| Trigger pipeline | `/predictions/pipeline` | POST |
| Simulate sensor | `/machines/{id}/simulate` | POST |
