# Sequence Flows

## 1. Backend Startup Sequence

```
main.py:startup_pipeline()
  1. start_sqs_consumer() → spawns daemon thread polling sensor-events queue
  2. alembic upgrade head  → applies DB migrations
  3. if not pipeline.lock:
       run_predictions_pipeline(limit=100)
         → load engineered_ai4i.csv
         → clear machines/predictions/recommendations tables
         → for each row: predict + store
         → sync_data_to_solr()
       create pipeline.lock
  4. sync_data_to_solr() (always runs on startup)
```

## 2. Prediction → Recommendation → Work Order Flow

See [sequence-diagram.mmd](diagrams/sequence-diagram.mmd) for the full Mermaid sequence.

Steps:
1. Frontend calls `POST /predictions/pipeline?limit=N`
2. API calls `db_service.run_predictions_pipeline(limit)`
3. For each dataset row: `predict_machine_failure()` → `INSERT Machine/Prediction/Recommendation`
4. Frontend polls `GET /predictions` and `GET /recommendations`
5. User creates work order via `POST /work-orders`
6. User transitions: `PATCH /work-orders/{id}/status {status: in_progress}`
7. User completes: `PATCH /work-orders/{id}/status {status: completed}` — `completed_at` auto-populated

## 3. SQS Sensor Event Flow

```
SensorSimulator.simulate_to_sqs(machine_id, count)
  → SQS.send_message({machine_id, air_temperature, process_temperature, rotational_speed, torque, tool_wear})
  → SQS queue: sensor-events

SQS Consumer Thread (daemon):
  while True:
    → sqs.receive_message(MaxNumberOfMessages=5, WaitTimeSeconds=5)
    → for each msg:
        parse JSON body
        process_single_telemetry(machine_id, air_temp, proc_temp, speed, torque, wear)
          → predict_machine_failure()
          → upsert Machine + Prediction + Recommendation
        sqs.delete_message(ReceiptHandle)
```

## 4. SNS Alert Flow

```
LocalStack init:
  sns.create_topic(maintenance-alerts)
  sns.subscribe(topic_arn, protocol=http, endpoint=http://backend:8000/alerts/webhook)

When backend publishes to SNS:
  → LocalStack delivers HTTP POST to /alerts/webhook
  → alerts_webhook() parses Subject for machine_id + severity
  → db_service.create_raw_alert(machine_id, severity, message)
  → stored in alerts table
```

## 5. Solr Search Flow

```
User types in search box → GET /search?q={query}
  → db_service.search_incidents(q)
  → HTTP GET http://solr:8983/solr/incidents/select?q={q}&wt=json
  → returns matching docs
  → displayed in Search tab
```
