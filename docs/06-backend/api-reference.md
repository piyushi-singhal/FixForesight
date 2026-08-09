# API Reference

> **Source of truth:** `backend/routes/*.py` and `backend/main.py`.  
> Base URL: `http://localhost:8000`

---

## System Endpoints

### GET /health
Health status of all dependent services.

**Response:**
```json
{
  "status": "healthy",
  "postgres": "healthy",
  "localstack": "healthy",
  "solr": "healthy"
}
```
`status` may be `"degraded"` if localstack or solr are unavailable.

---

### GET /
### GET /index.html
Returns the legacy HTML dashboard (`frontend/public/index.html`) as `text/html`.

---

## Machines

### GET /machines
Returns all machines with their latest telemetry, failure probability, predicted failure, and recommendation.

**Response:** Array of `MachineResponse`
```json
[
  {
    "machine_id": "M101",
    "air_temperature": 298.1,
    "process_temperature": 308.6,
    "rotational_speed": 1551,
    "torque": 42.8,
    "tool_wear": 0.0,
    "failure_probability": 3.2,
    "predicted_failure": "No Failure Predicted",
    "recommendation": "No active recommendations. Machine operation normal.",
    "created_at": "2026-08-09T20:00:00"
  }
]
```

### GET /machines/{machine_id}/risk
Returns risk assessment data for a specific machine.

**Path param:** `machine_id` (string, e.g. `M101`)

**Response:** JSON with machine risk data.
**Errors:** 404 if machine not found.

### POST /machines/{machine_id}/simulate
Triggers sensor simulation for a machine. Sends `count` SQS events at `interval` second spacing (runs as a background task).

**Query params:** `count` (int, default=10), `interval` (float, default=1.0)

**Response:**
```json
{"status": "simulation_started", "machine_id": "M101", "events_count": 10}
```

---

## Predictions

### GET /predictions
Returns all predictions with machine telemetry.

**Response:** Array of `PredictionResponse`
```json
[
  {
    "machine_id": "M101",
    "air_temperature": 298.1,
    "process_temperature": 308.6,
    "rotational_speed": 1551,
    "torque": 42.8,
    "tool_wear": 0.0,
    "failure_probability": 3.2,
    "predicted_failure": "No Failure Predicted",
    "time_to_failure": "1 Month"
  }
]
```

### POST /predictions/pipeline
Triggers the prediction pipeline for up to `limit` records from the dataset.

**Query params:** `limit` (int, default=100)

**Response:**
```json
{"status": "success", "processed_records": 100}
```

---

## Recommendations

### GET /recommendations
Returns all maintenance recommendations.

**Response:** Array of `RecommendationResponse`
```json
[
  {
    "recommendation_id": 1,
    "machine_id": "M101",
    "recommendation": "No active recommendations. Machine operation normal.",
    "priority": "Low",
    "confidence": 3.2,
    "prediction_id": 1,
    "created_at": "2026-08-09T20:00:00"
  }
]
```

### GET /machines/{machine_id}/recommendations
Returns recommendations for a specific machine.

---

## Alerts

### GET /alerts
Returns all alerts.

**Response:** Array of `AlertResponse`
```json
[
  {
    "alert_id": 1,
    "machine_id": "M101",
    "severity": "Critical",
    "message": "High failure probability detected",
    "created_at": "2026-08-09T20:00:00"
  }
]
```

### POST /alerts/webhook
SNS webhook receiver. Accepts SNS `SubscriptionConfirmation` or `Notification` HTTP POST.

**Body:** SNS JSON payload (or raw body)

Extracts machine_id from Subject, determines severity, stores alert in DB.

---

## Work Orders

### GET /work-orders
Returns all work orders.

**Response:** Array of `WorkOrderResponse`
```json
[
  {
    "id": 1,
    "machine_id": "M101",
    "recommendation_id": null,
    "status": "open",
    "priority": "High",
    "action_required": "Replace worn parts",
    "created_at": "2026-08-09T20:00:00",
    "completed_at": null
  }
]
```

### POST /work-orders
Creates a new work order.

**Body:** `WorkOrderRequest`
```json
{
  "machine_id": "M101",
  "priority": "High",
  "action_required": "Replace worn parts during shutdown",
  "recommendation_id": null
}
```

**Response:**
```json
{"status": "created", "work_order_id": 1}
```

### PATCH /work-orders/{id}/status
Updates work order status.

**Path param:** `id` (integer)

**Body:** `WorkOrderStatusUpdate`
```json
{"status": "in_progress"}
```
or
```json
{"status": "completed"}
```

**Response:**
```json
{"status": "success", "work_order_id": 1, "new_status": "in_progress"}
```

**Errors:** 404 if work order not found.

---

## Analytics

### GET /analytics
Fleet-level summary statistics.

**Response:** `AnalyticsResponse`
```json
{
  "healthy": 72,
  "warning": 18,
  "critical": 10,
  "healthy_machines": 72,
  "warning_machines": 18,
  "critical_machines": 10,
  "open_work_orders": 5,
  "completed_work_orders": 12
}
```

### GET /analytics/feature-importance
Model feature importances from the loaded GradientBoosting model.

**Response:**
```json
{
  "Torque": 0.439,
  "Tool Wear": 0.171,
  "Temperature Difference": 0.253,
  "Air Temperature": 0.147,
  "Rotational Speed": 0.135,
  "Process Temperature": 0.108
}
```

### GET /analytics/model-monitoring
Model evaluation metrics.

**Response:**
```json
{
  "accuracy": 0.9845,
  "precision": 0.885,
  "recall": 0.642,
  "f1": 0.7438,
  "roc_auc": 0.9618
}
```
> ⚠️ These values are currently hardcoded, not dynamically computed.

---

## Dashboard

### GET /dashboard
Fleet summary for dashboard header.

**Response:** `DashboardResponse`
```json
{
  "total_machines": 100,
  "healthy_machines": 72,
  "warning_machines": 18,
  "critical_machines": 10,
  "critical_alerts_count": 5
}
```

---

## Search

### GET /search
Full-text search over incident data via Apache Solr.

**Query param:** `q` (string, default=`"*:*"`)

**Response:** Solr JSON response with matching documents.

**Example:** `GET /search?q=bearing+failure`

---

## Interactive API Documentation

FastAPI auto-generates interactive docs:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
