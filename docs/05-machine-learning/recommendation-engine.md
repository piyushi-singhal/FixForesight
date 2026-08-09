# Recommendation Engine

## Overview

The recommendation engine converts probabilistic failure predictions into specific, prioritised maintenance actions.

**Primary module:** `src/recommendation_engine.py:RecommendationEngine`

**Pipeline integration:** `src/predictions_pipeline.py` and `backend/services/db_service.py`

---

## Recommendation Logic

### In Predictions Pipeline (`predictions_pipeline.py`)

Simple rule-based thresholds:

```python
if prob > 0.8:
    recommendation_text = "Immediate Maintenance Required"
    priority = "Critical"
elif prob > 0.5:
    recommendation_text = "Schedule preventive maintenance"
    priority = "Medium"
else:
    recommendation_text = "No active recommendations. Machine operation normal."
    priority = "Low"
```

### In db_service.py (via `RecommendationEngine`)

If `RecommendationEngine` from `src/recommendation_engine.py` imports successfully, it is used for richer recommendations based on failure type. If import fails, the simple threshold rules above are used.

---

## Output Fields

| Field | Description |
|---|---|
| `recommendation` | Human-readable maintenance instruction text |
| `priority` | `Critical` / `Medium` / `Low` |
| `confidence` | Same as failure probability (0–100) |
| `prediction_id` | Links recommendation to the triggering prediction |

---

## API Access

```
GET /recommendations                          → all recommendations
GET /machines/{machine_id}/recommendations    → per-machine recommendations
```
