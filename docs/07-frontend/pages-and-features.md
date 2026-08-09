# Pages and Features

## HTML Dashboard (Primary Local UI)

`frontend/public/index.html` — served by FastAPI at `GET /`.

### Views / Tabs

| View | Content |
|---|---|
| **Dashboard** | Fleet KPI cards: total machines, healthy/warning/critical counts, critical alerts |
| **Machine Fleet** | Card grid of all machines with status badges, telemetry readings, failure probability |
| **Machine Detail** | On machine selection: current telemetry, risk score, failure trend, prediction history, recommendations, alerts, work orders |
| **Explainability** | Feature importance bar chart from `GET /analytics/feature-importance` |
| **Model Quality Metrics** | Accuracy, Precision, Recall, F1, ROC-AUC from `GET /analytics/model-monitoring` |
| **Predictions** | Tabular list of all predictions with failure probability |
| **Recommendations** | Tabular list of all maintenance recommendations with priority |
| **Alerts** | Tabular list of all alerts with severity |
| **Work Orders** | Work order list with create form + status update buttons (in_progress / completed) |
| **Analytics** | Pie/bar charts of fleet status distribution |
| **Search** | Full-text search input → `/search?q=` → results display |

---

## React SPA (frontend/src/App.jsx)

The React application (`App.jsx` — ~73 KB) mirrors the HTML dashboard features but with Redux-managed state and React component structure.

---

## Work Order Workflow

1. User opens **Work Orders** tab
2. Fills in machine ID, priority, description
3. Clicks **Create Work Order** → `POST /work-orders`
4. New work order appears with status `open`
5. Technician clicks **Start Work** → `PATCH /work-orders/{id}/status {status: in_progress}`
6. Technician clicks **Mark Complete** → `PATCH /work-orders/{id}/status {status: completed}`
7. `completed_at` is auto-set by the backend

---

## Polling Behavior

The React frontend uses Redux `createAsyncThunk` and periodic calls. Polling intervals are defined in the slice files.

The HTML dashboard similarly polls endpoints via `setInterval` calls in JavaScript.
