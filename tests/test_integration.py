# tests/test_integration.py
"""
Integration tests for FixForesight:
- SQS -> Consumer -> DB Ingestion
- SNS -> Webhook -> Alerts Ingestion
- Apache Solr search
- Docker Compose config syntax check
"""

import os
import sys
import time
import json
import socket
import pytest
import subprocess
from pathlib import Path
import boto3

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from backend.main import app
from backend.database.connection import SessionLocal
from backend.database.models import Prediction, Alert

client = TestClient(app)

def is_port_open(host: str, port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)
            s.connect((host, port))
            return True
    except Exception:
        return False

# Setup skip conditions for local dev environments where docker services might not be active
localstack_missing = not is_port_open("127.0.0.1", 4566)
postgres_missing = not is_port_open("127.0.0.1", 5432)
solr_missing = not is_port_open("127.0.0.1", 8983)

@pytest.mark.skipif(localstack_missing or postgres_missing, reason="Integration services (LocalStack or Postgres) are offline")
def test_sqs_consumer_db():
    """Verify that pushing a telemetry message to SQS is consumed, run through ML inference, and saved in Postgres."""
    # 1. Initialize SQS client
    sqs = boto3.client(
        "sqs",
        endpoint_url="http://127.0.0.1:4566",
        region_name="us-east-1",
        aws_access_key_id="mock",
        aws_secret_access_key="mock"
    )
    
    # 2. Get queue URL
    queue_url = sqs.get_queue_url(QueueName="sensor-events")["QueueUrl"]
    
    # 3. Publish a simulated critical payload for a unique test machine ID
    test_machine_id = "TEST-MACH-SQS"
    payload = {
        "machine_id": test_machine_id,
        "air_temperature": 304.5,
        "process_temperature": 315.8,
        "rotational_speed": 2350,
        "torque": 68.2,
        "tool_wear": 195.0
    }
    
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(payload)
    )
    
    # 4. Poll database to verify the SQS consumer processed it
    db = SessionLocal()
    try:
        found = False
        # Poll up to 10 seconds
        for _ in range(20):
            pred = db.query(Prediction).filter(Prediction.machine_id == test_machine_id).first()
            if pred:
                found = True
                assert pred.failure_probability > 80.0
                assert "Failure" in pred.predicted_failure
                break
            time.sleep(0.5)
            db.close()
            db = SessionLocal()  # Refresh session to fetch latest updates
            
        assert found, f"SQS consumer did not write prediction record in database for {test_machine_id}"
    finally:
        # Cleanup test prediction
        pred = db.query(Prediction).filter(Prediction.machine_id == test_machine_id).first()
        if pred:
            db.delete(pred)
            db.commit()
        db.close()


@pytest.mark.skipif(localstack_missing or postgres_missing, reason="Integration services (LocalStack or Postgres) are offline")
def test_sns_webhook_alerts():
    """Verify that publishing an alert message to SNS is successfully delivered to the webhook and persisted in Postgres."""
    # 1. Initialize SNS client
    sns = boto3.client(
        "sns",
        endpoint_url="http://127.0.0.1:4566",
        region_name="us-east-1",
        aws_access_key_id="mock",
        aws_secret_access_key="mock"
    )
    
    topic_arn = "arn:aws:sns:us-east-1:000000000000:maintenance-alerts"
    test_machine_id = "M101"
    unique_token = f"TEST-TOKEN-M101-SNS-{int(time.time())}"
    
    # 2. Publish to topic (this will invoke the alerts webhook via LocalStack delivery subscription)
    subject = f"CRITICAL: Machine {test_machine_id} requires immediate attention"
    message = f"Machine {test_machine_id} has high failure probability of 95.0% ({unique_token})."
    
    sns.publish(
        TopicArn=topic_arn,
        Subject=subject,
        Message=message
    )
    
    # 3. Poll database to verify webhook received and saved the alert
    db = SessionLocal()
    try:
        found = False
        # Poll up to 10 seconds
        for _ in range(20):
            alert = db.query(Alert).filter(
                Alert.machine_id == test_machine_id,
                Alert.message.like(f"%{unique_token}%")
            ).first()
            if alert:
                found = True
                assert alert.severity == "Critical"
                assert test_machine_id in alert.message
                break
            time.sleep(0.5)
            db.close()
            db = SessionLocal()  # Refresh session
            
        assert found, f"SNS webhook alert was not written to alerts table for {test_machine_id}"
    finally:
        # Cleanup test alert
        alert = db.query(Alert).filter(
            Alert.machine_id == test_machine_id,
            Alert.message.like(f"%{unique_token}%")
        ).first()
        if alert:
            db.delete(alert)
            db.commit()
        db.close()


@pytest.mark.skipif(solr_missing, reason="Apache Solr is offline")
def test_solr_search():
    """Verify backend search route successfully pings Solr and returns results."""
    response = client.get("/search?q=*:*")
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, dict)
    assert "docs" in results
    assert isinstance(results["docs"], list)



def test_docker_compose_config():
    """Verify that the docker-compose configuration files have syntactically valid structure and backend Dockerfile exists."""
    # 1. Verify Dockerfile exists
    dockerfile_path = Path(__file__).resolve().parents[1] / "backend" / "Dockerfile"
    assert dockerfile_path.exists(), "Backend Dockerfile is missing"
    
    # 2. Verify docker compose config syntax
    try:
        res = subprocess.run(
            ["docker", "compose", "config"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(Path(__file__).resolve().parents[1]),
            text=True
        )
        assert res.returncode == 0, f"Docker compose config has syntax errors: {res.stderr}"
    except FileNotFoundError:
        # Docker Compose is not installed in the test runner host environment, skip compose syntax verification
        pytest.skip("Docker/Docker Compose command is not available in current terminal shell path")
