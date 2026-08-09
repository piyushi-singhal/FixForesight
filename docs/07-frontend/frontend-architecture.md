# Frontend Architecture

## Overview

FixForesight's frontend is a **React** single-page application (SPA) with **Redux Toolkit** for state management.

---

## Technology Stack

| Technology | Version | Purpose |
|---|---|---|
| React | (see package.json) | UI framework |
| Redux Toolkit | (see package.json) | State management |
| TypeScript | Used in slices/services | Type safety |
| Webpack | webpack.config.js | Build bundler |
| nginx | Dockerfile | Static file server in Docker |

---

## Entry Points

| File | Purpose |
|---|---|
| `frontend/src/index.jsx` | React root — renders `<App />` with Redux `<Provider>` |
| `frontend/src/App.jsx` | Main component (~73 KB) — all pages and views |
| `frontend/public/index.html` | Legacy HTML dashboard — also served directly by FastAPI at `GET /` |

> **Note:** There are TWO frontends:
> 1. **React SPA** (`frontend/src/`) — compiled by Webpack, served by nginx in Docker
> 2. **HTML dashboard** (`frontend/public/index.html`) — a standalone HTML/JS file served by FastAPI at `/`. This is the primary UI used in local development without Docker.

---

## Redux Store Structure

Store configured in `frontend/src/store/index.ts`.

| Slice | File | API Endpoint |
|---|---|---|
| `machines` | `machinesSlice.ts` | `GET /machines`, `GET /machines/{id}/risk` |
| `predictions` | `predictionsSlice.ts` | `GET /predictions` |
| `recommendations` | `recommendationsSlice.ts` | `GET /recommendations`, `GET /machines/{id}/recommendations` |
| `alerts` | `alertsSlice.ts` | `GET /alerts` |
| `workOrders` | `workOrdersSlice.ts` | `GET/POST /work-orders`, `PATCH /work-orders/{id}/status` |
| `dashboard` | `dashboardSlice.ts` | `GET /dashboard` |
| `search` | `searchSlice.ts` | `GET /search?q=` |

---

## Service Layer

`frontend/src/services/` — thin HTTP client wrappers using `fetch`:

| Service File | API Calls |
|---|---|
| `apiConfig.js` | Base URL configuration |
| `machineService.ts` | GET /machines, GET /machines/{id}/risk |
| `predictionService.ts` | GET /predictions |
| `recommendationService.ts` | GET /recommendations, GET /machines/{id}/recommendations |
| `alertService.ts` | GET /alerts |
| `workOrderService.ts` | GET /work-orders, POST /work-orders, PATCH /work-orders/{id}/status |
| `analyticsService.ts` | GET /analytics, GET /analytics/feature-importance, GET /analytics/model-monitoring |
| `dashboardService.ts` | GET /dashboard |
| `searchService.ts` | GET /search?q= |

---

## API Base URL

Configured in `frontend/src/services/apiConfig.js`:
```javascript
const BASE_URL = "http://localhost:8000";  // or configured per environment
```

---

## Build Configuration

`frontend/webpack.config.js` bundles the React SPA.

`frontend/Dockerfile` builds the SPA and serves it with nginx on port 80 (mapped to host port 3000).

---

## Related Documents

- [Pages and Features](pages-and-features.md)
- [Redux State Management](redux-state-management.md)
- [API Integration](api-integration.md)
