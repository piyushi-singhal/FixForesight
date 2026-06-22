# API Contracts

## Machines
```json
{
  "machine_id": "M101",
  "machine_name": "CNC Machine",
  "status": "Healthy",
  "temperature": 75,
  "pressure": 30,
  "vibration": 0.5,
  "rpm": 2500
}
```

## Predictions
```json
{
  "machine_id": "M101",
  "failure_probability": 82,
  "predicted_failure": "Bearing Failure",
  "time_to_failure": "5 Days"
}
```

## Recommendations
```json
{
  "machine_id": "M101",
  "recommendation": "Replace Bearing",
  "priority": "High",
  "confidence": 91
}
```

## Alerts
```json
{
  "alert_id": 1,
  "machine_id": "M101",
  "severity": "Critical",
  "message": "Bearing failure risk exceeds 80%"
}
```

## Analytics
```json
{
  "healthy": 85,
  "warning": 10,
  "critical": 5
}
```

---

# Database Schema

### machines
* `machine_id` (VARCHAR PRIMARY KEY)
* `machine_name` (VARCHAR)
* `status` (VARCHAR)
* `temperature` (DOUBLE PRECISION)
* `pressure` (DOUBLE PRECISION)
* `vibration` (DOUBLE PRECISION)
* `rpm` (INT)
* `created_at` (TIMESTAMP)

### predictions
* `prediction_id` (SERIAL PRIMARY KEY)
* `machine_id` (VARCHAR REFERENCES machines(machine_id))
* `failure_probability` (DOUBLE PRECISION)
* `predicted_failure` (VARCHAR)
* `time_to_failure` (VARCHAR)
* `created_at` (TIMESTAMP)

### recommendations
* `recommendation_id` (SERIAL PRIMARY KEY)
* `machine_id` (VARCHAR REFERENCES machines(machine_id))
* `recommendation` (TEXT)
* `priority` (VARCHAR)
* `confidence` (DOUBLE PRECISION)
* `created_at` (TIMESTAMP)

### alerts
* `alert_id` (SERIAL PRIMARY KEY)
* `machine_id` (VARCHAR REFERENCES machines(machine_id))
* `severity` (VARCHAR)
* `message` (TEXT)
* `created_at` (TIMESTAMP)
