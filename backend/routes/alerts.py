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
        subscribe_url = payload.get("SubscribeURL")
        print(f"SNS Subscription Confirmation requested: {subscribe_url}")
        if subscribe_url:
            import requests
            try:
                # LocalStack subscription endpoint uses localhost, but we need to resolve it to localstack inside Docker container.
                # If subscribe_url contains 'localhost', replace it with 'localstack' so it is reachable from backend container.
                if "localhost.localstack.cloud" in subscribe_url:
                    subscribe_url = subscribe_url.replace("localhost.localstack.cloud", "localstack")
                elif "localhost" in subscribe_url:
                    subscribe_url = subscribe_url.replace("localhost", "localstack")
                r = requests.get(subscribe_url, timeout=5.0)
                print(f"SNS Subscription Confirmed successfully! Response: {r.status_code}")
            except Exception as confirm_err:
                print(f"Error confirming SNS subscription: {confirm_err}")
        return {"status": "subscription_confirmed"}
        
    subj = payload.get("Subject", "")
    message_val = payload.get("Message", str(body))
    
    # Try to parse target machine using regex (e.g., M101)
    import re
    match = re.search(r"M\d+", subj)
    if match:
        machine_id = match.group(0)
    else:
        machine_id = "M101"

    severity = "Critical" if "CRITICAL" in subj.upper() or "HIGH" in subj.upper() else "Warning"
    db_service.create_raw_alert(machine_id, severity, message_val)
    return {"status": "alert_saved"}
