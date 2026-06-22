from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class MachineResponse(BaseModel):
    machine_id: str
    air_temperature: float
    process_temperature: float
    rotational_speed: int
    torque: float
    tool_wear: float
    failure_probability: float
    predicted_failure: str
    recommendation: str

class PredictionResponse(BaseModel):
    machine_id: str
    air_temperature: float
    process_temperature: float
    rotational_speed: int
    torque: float
    tool_wear: float
    failure_probability: float
    predicted_failure: str
    time_to_failure: str

class RecommendationResponse(BaseModel):
    machine_id: str
    recommendation: str
    priority: str
    confidence: float
    created_at: str

class WorkOrderResponse(BaseModel):
    id: int
    machine_id: str
    status: str
    priority: str
    action_required: str
    created_at: str
    completed_at: Optional[str] = None

class AlertResponse(BaseModel):
    alert_id: int
    machine_id: str
    severity: str
    message: str
    created_at: str

class AnalyticsResponse(BaseModel):
    healthy: int
    warning: int
    critical: int

class DashboardResponse(BaseModel):
    total_machines: int
    healthy_machines: int
    warning_machines: int
    critical_machines: int
    critical_alerts_count: int

class WorkOrderRequest(BaseModel):
    machine_id: str
    priority: str
    action_required: str


class AlertWebhookRequest(BaseModel):
    Type: Optional[str] = None
    MessageId: Optional[str] = None
    Subject: Optional[str] = None
    Message: Optional[str] = None
    SubscribeURL: Optional[str] = None
