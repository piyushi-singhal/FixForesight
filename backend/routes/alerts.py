from fastapi import APIRouter, Request, Response
from typing import List
import json
from backend.schemas.models import AlertResponse
from backend.services import db_service

router = APIRouter()

@router.get("/alerts", response_model=List[AlertResponse])
def get_alerts():
    return db_service.get_all_alerts()

@router.post("/alerts/webhook")
async def alerts_webhook(req: Request):
    body = await req.body()
    try:
        payload = json.loads(body.decode('utf-8'))
    except Exception:
        payload = {}
        
    msg_type = req.headers.get("x-amz-sns-message-type") or payload.get("Type")
    if msg_type == "SubscriptionConfirmation":
        print(f"SNS Subscription Confirmed: {payload.get('SubscribeURL')}")
        return {"status": "subscription_confirmed"}
        
    subj = payload.get("Subject", "")
    message_val = payload.get("Message", str(body))
    
    # Try to parse target machine
    machine_id = "M101"
    if "M" in subj:
        # e.g., "CRITICAL: Machine M103 is overheating" -> extract M103
        try:
            part = subj.split("M")
            if len(part) > 1:
                machine_id = "M" + part[1][:3]
        except Exception:
            pass

    severity = "Critical" if "CRITICAL" in subj.upper() or "HIGH" in subj.upper() else "Warning"
    db_service.create_raw_alert(machine_id, severity, message_val)
    return {"status": "alert_saved"}
