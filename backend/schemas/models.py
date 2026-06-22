from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class MachineResponse(BaseModel):
    machine_id: str
    machine_name: str
    status: str
    temperature: float
    pressure: float
    vibration: float
    rpm: int

class PredictionResponse(BaseModel):
    machine_id: str
    failure_probability: float
    predicted_failure: str
    time_to_failure: str

class RecommendationResponse(BaseModel):
    machine_id: str
    recommendation: str
    priority: str
    confidence: float

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
