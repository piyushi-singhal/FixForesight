# Relationships

## Entity Relationships

```
machines (1) ─────────────────── (N) predictions
  ↓ CASCADE DELETE                     ↓
machines (1) ─────────────────── (N) recommendations
  ↓ CASCADE DELETE
machines (1) ─────────────────── (N) alerts
  ↓ CASCADE DELETE
machines (1) ─────────────────── (N) work_orders
  ↓ CASCADE DELETE

predictions (1) ────────────── (0 or 1) recommendations
  ↓ CASCADE DELETE

recommendations (1) ─────────── (N) work_orders
  ↓ SET NULL on delete
```

## Cascade Behaviours

| Delete Event | Cascade Action |
|---|---|
| DELETE machines | → DELETE predictions, recommendations, alerts, work_orders |
| DELETE predictions | → DELETE linked recommendations |
| DELETE recommendations | → SET recommendation_id = NULL in work_orders |

## Business Rules Enforced by Schema

- A machine may have multiple predictions (one per pipeline run).
- Each prediction has at most one recommendation (`uselist=False` on SQLAlchemy relationship).
- A work order may exist without a recommendation (`recommendation_id` nullable).
- A work order `completed_at` is NULL until status is set to `completed`.
- `parts_inventory.part_name` is UNIQUE — no duplicate part names.
