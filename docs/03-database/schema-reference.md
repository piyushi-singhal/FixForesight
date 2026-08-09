# Schema Reference

> Source: `backend/database/models.py` (ORM) and `backend/db/schema.sql` (init SQL).

---

## Table: `machines`

Primary registry of monitored industrial machines.

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `machine_id` | VARCHAR(50) | NO | — | Primary key. Format: `M{UDI+100}` e.g. `M101` |
| `machine_name` | VARCHAR(100) | NO | — | Human-readable name |
| `status` | VARCHAR(50) | NO | — | `Healthy`, `Warning`, or `Critical` |
| `air_temperature` | FLOAT/DOUBLE | NO | — | Ambient air temp in Kelvin |
| `process_temperature` | FLOAT/DOUBLE | NO | — | Process temp in Kelvin |
| `rotational_speed` | INTEGER | NO | — | RPM |
| `torque` | FLOAT/DOUBLE | NO | — | Torque in Nm |
| `tool_wear` | FLOAT/DOUBLE | NO | — | Tool wear in minutes |
| `created_at` | TIMESTAMP | YES | `CURRENT_TIMESTAMP` | Row creation time |

**Indexes:** Primary key on `machine_id`

**Relationships:**
- 1 machine → N predictions (CASCADE DELETE)
- 1 machine → N recommendations (CASCADE DELETE)
- 1 machine → N alerts (CASCADE DELETE)
- 1 machine → N work_orders (CASCADE DELETE)

---

## Table: `predictions`

One prediction record per machine per pipeline run.

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `prediction_id` | SERIAL INTEGER | NO | autoincrement | Primary key |
| `machine_id` | VARCHAR(50) | YES | — | FK → machines.machine_id (CASCADE) |
| `failure_probability` | FLOAT/DOUBLE | NO | — | Stored as percentage (0–100) |
| `predicted_failure` | VARCHAR(255) | NO | — | e.g. `Machine Failure` or `No Failure Predicted` |
| `time_to_failure` | VARCHAR(100) | NO | — | e.g. `6 Hours`, `24 Hours`, `2 Days`, `5 Days`, `2 Weeks`, `1 Month` |
| `created_at` | TIMESTAMP | YES | `CURRENT_TIMESTAMP` | Prediction timestamp |

**Indexes:** `idx_predictions_machine` on `machine_id`

> Note: `failure_probability` is stored as a percentage (e.g., `82.0` = 82%). The raw model output is 0–1 range; multiply by 100 before INSERT.

---

## Table: `recommendations`

One recommendation per prediction (linked via `prediction_id`).

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `recommendation_id` | SERIAL INTEGER | NO | autoincrement | Primary key |
| `machine_id` | VARCHAR(50) | YES | — | FK → machines.machine_id (CASCADE) |
| `prediction_id` | INTEGER | YES | NULL | FK → predictions.prediction_id (CASCADE) |
| `recommendation` | TEXT | NO | — | Maintenance action text |
| `priority` | VARCHAR(50) | NO | — | `Critical`, `Medium`, or `Low` |
| `confidence` | FLOAT/DOUBLE | NO | — | Stored as percentage (0–100) |
| `created_at` | TIMESTAMP | YES | `CURRENT_TIMESTAMP` | Creation timestamp |

**Indexes:** `idx_recommendations_machine` on `machine_id`

---

## Table: `alerts`

System and SNS-delivered alerts.

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `alert_id` | SERIAL INTEGER | NO | autoincrement | Primary key |
| `machine_id` | VARCHAR(50) | YES | — | FK → machines.machine_id (CASCADE) |
| `severity` | VARCHAR(50) | NO | — | `Critical` or `Warning` |
| `message` | TEXT | NO | — | Alert message body |
| `created_at` | TIMESTAMP | YES | `CURRENT_TIMESTAMP` | Alert timestamp |

**Indexes:** `idx_alerts_machine` on `machine_id`

---

## Table: `work_orders`

Maintenance task lifecycle.

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | SERIAL INTEGER | NO | autoincrement | Primary key |
| `machine_id` | VARCHAR(50) | YES | — | FK → machines.machine_id (CASCADE) |
| `recommendation_id` | INTEGER | YES | NULL | FK → recommendations.recommendation_id (SET NULL on delete) |
| `status` | VARCHAR(50) | NO | `open` | `open`, `in_progress`, or `completed` |
| `priority` | VARCHAR(50) | NO | — | `Critical`, `High`, `Medium`, `Low` |
| `action_required` | TEXT | NO | — | Maintenance instructions |
| `created_at` | TIMESTAMP | YES | `CURRENT_TIMESTAMP` | Creation timestamp |
| `completed_at` | TIMESTAMP | YES | NULL | Set when status → completed |

**Indexes:** `idx_work_orders_machine` on `machine_id`

---

## Table: `parts_inventory`

Spare parts stock management (reference data).

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `part_id` | SERIAL INTEGER | NO | autoincrement | Primary key |
| `part_name` | VARCHAR(100) | NO | — | UNIQUE. Part name |
| `quantity` | INTEGER | NO | — | Current stock level |
| `min_required` | INTEGER | NO | — | Minimum required stock |
| `unit_cost` | FLOAT/DOUBLE | NO | — | Cost per unit |

---

## Related Documents

- [ER Diagram](diagrams/er-diagram.mmd)
- [Relationships](relationships.md)
- [Data Dictionary](data-dictionary.md)
