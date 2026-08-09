# SQS / SNS Event Flow

> **Implementation Status:** 🟡 Partially Implemented  
> The infrastructure (queue, topic, consumer thread, webhook) is in place. The end-to-end flow works when LocalStack is running but relies on manual simulation trigger.

---

## SQS — Sensor Events

### Queue Name: `sensor-events`

**Producer:** `src/sensor_simulator.py:SensorSimulator.simulate_to_sqs()`

```python
# Triggered via POST /machines/{machine_id}/simulate
sqs.send_message(
    QueueUrl=queue_url,
    MessageBody=json.dumps({
        "machine_id": machine_id,
        "air_temperature": ...,
        "process_temperature": ...,
        "rotational_speed": ...,
        "torque": ...,
        "tool_wear": ...
    })
)
```

**Consumer:** Daemon thread in `backend/main.py:start_sqs_consumer()`

```python
# Runs continuously, long-polling every 5 seconds
sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=5, WaitTimeSeconds=5)
# For each message:
process_single_telemetry(machine_id, air_temp, proc_temp, speed, torque, wear)
sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=...)
```

---

## SNS — Maintenance Alerts

### Topic Name: `maintenance-alerts`
### Topic ARN: `arn:aws:sns:us-east-1:000000000000:maintenance-alerts`

**Publisher:** `backend/services/db_service.py` (publishes on critical predictions)

**Subscriber:** `POST /alerts/webhook` — FastAPI endpoint receiving SNS HTTP notifications

```python
# Webhook processes:
# 1. SubscriptionConfirmation (prints URL, returns confirmed)
# 2. Notification (extracts machine_id from Subject, saves alert to DB)
```

---

## S3 — Raw Data Storage

### Bucket Name: `iot-raw-data`

**Current status:** ⚪ Created but not actively used in the current codebase. Intended for raw telemetry archival.

---

## Flow Diagram

See [system-architecture.mmd](../02-architecture/diagrams/system-architecture.mmd) for the complete infrastructure diagram.
