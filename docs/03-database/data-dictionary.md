# Data Dictionary

## Status Enumerations

### Machine Status
| Value | Meaning | Trigger |
|---|---|---|
| `Healthy` | Failure probability ≤ 40% | `prob <= 0.4` in predictions_pipeline.py |
| `Warning` | Failure probability 40–80% | `0.4 < prob <= 0.8` |
| `Critical` | Failure probability > 80% | `prob > 0.8` |

### Work Order Status
| Value | Meaning |
|---|---|
| `open` | Newly created, not yet assigned |
| `in_progress` | Technician has started the work |
| `completed` | Work complete; `completed_at` set |

### Alert Severity
| Value | Meaning |
|---|---|
| `Critical` | `CRITICAL` or `HIGH` in SNS Subject |
| `Warning` | Default for all other SNS messages |

### Recommendation Priority
| Value | Trigger |
|---|---|
| `Critical` | `prob > 0.8` |
| `Medium` | `0.5 < prob <= 0.8` |
| `Low` | `prob <= 0.5` |

## Failure Type Taxonomy

Determined by rule-based logic in `db_service.predict_machine_failure()`:

| Failure Type | Condition |
|---|---|
| `heat_dissipation` | temp_diff < -15.0 OR (proc_temp - air_temp) > 15.0 |
| `tool_wear` | tool_wear > 180.0 |
| `overstrain` | torque > 65.0 |
| `power_loss` | rotational_speed < 1200.0 |
| `random_failure` | None of the above apply but pred_class == 1 |

## Time-to-Failure Buckets

| Value | Probability Range |
|---|---|
| `6 Hours` | prob > 0.9 |
| `24 Hours` | 0.75 < prob ≤ 0.9 |
| `2 Days` | 0.6 < prob ≤ 0.75 |
| `5 Days` | 0.5 < prob ≤ 0.6 |
| `2 Weeks` | 0.3 < prob ≤ 0.5 |
| `1 Month` | prob ≤ 0.3 |

## Sensor Units

| Field | Unit | Range (sensor spec) |
|---|---|---|
| `air_temperature` | Kelvin (K) | 293.15 – 313.15 |
| `process_temperature` | Kelvin (K) | 308.15 – 333.15 |
| `rotational_speed` | RPM | 1000 – 3000 |
| `torque` | Nm | 3 – 100 |
| `tool_wear` | minutes | 0 – 240 |
