# API Contracts

> Source: `backend/schemas/models.py` (Pydantic models).

---

## Request Models

### WorkOrderRequest
```python
class WorkOrderRequest(BaseModel):
    machine_id: Optional[str] = None
    priority: Optional[str] = None
    action_required: Optional[str] = None
    recommendation_id: Optional[int] = None
```

### WorkOrderStatusUpdate
```python
class WorkOrderStatusUpdate(BaseModel):
    status: str  # "open" | "in_progress" | "completed"
```

### AlertWebhookRequest
```python
class AlertWebhookRequest(BaseModel):
    Type: Optional[str] = None
    MessageId: Optional[str] = None
    Subject: Optional[str] = None
    Message: Optional[str] = None
    SubscribeURL: Optional[str] = None
```

---

## Response Models

### MachineResponse
```python
class MachineResponse(BaseModel):
    machine_id: str
    air_temperature: float
    process_temperature: float
    rotational_speed: int
    torque: float
    tool_wear: float
    failure_probability: float     # 0–100 (percentage)
    predicted_failure: str
    recommendation: str
    created_at: Optional[str] = None
```

### PredictionResponse
```python
class PredictionResponse(BaseModel):
    machine_id: str
    air_temperature: float
    process_temperature: float
    rotational_speed: int
    torque: float
    tool_wear: float
    failure_probability: float     # 0–100 (percentage)
    predicted_failure: str
    time_to_failure: str
```

### RecommendationResponse
```python
class RecommendationResponse(BaseModel):
    recommendation_id: Optional[int] = None
    machine_id: str
    recommendation: str
    priority: str                  # Critical|Medium|Low
    confidence: float              # 0–100 (percentage)
    prediction_id: Optional[int] = None
    created_at: str
```

### WorkOrderResponse
```python
class WorkOrderResponse(BaseModel):
    id: int
    machine_id: str
    recommendation_id: Optional[int] = None
    status: str                    
    priority: str
    action_required: str
    created_at: str
    completed_at: Optional[str] = None
```

### AlertResponse
```python
class AlertResponse(BaseModel):
    alert_id: int
    machine_id: str
    severity: str                  
    message: str
    created_at: str
```

### AnalyticsResponse
```python
class AnalyticsResponse(BaseModel):
    healthy: int
    warning: int
    critical: int
    healthy_machines: int
    warning_machines: int
    critical_machines: int
    open_work_orders: int
    completed_work_orders: int
```

### DashboardResponse
```python
class DashboardResponse(BaseModel):
    total_machines: int
    healthy_machines: int
    warning_machines: int
    critical_machines: int
    critical_alerts_count: int
```
