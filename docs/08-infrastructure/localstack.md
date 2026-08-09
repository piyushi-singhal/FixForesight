# LocalStack

## Purpose

LocalStack simulates AWS cloud services locally so the application can use SQS, SNS, and S3 without real AWS credentials.

**LocalStack endpoint:** `http://localhost:4566` (host) / `http://localstack:4566` (Docker network)

---

## Resources Created

Defined in `infra/localstack/init-resources.sh` — runs on container startup:

```bash
# S3 Bucket
awslocal s3 mb s3://iot-raw-data

# SQS Queue
awslocal sqs create-queue --queue-name sensor-events

# SNS Topic
awslocal sns create-topic --name maintenance-alerts

# SNS → FastAPI webhook subscription
awslocal sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:000000000000:maintenance-alerts \
  --protocol http \
  --notification-endpoint http://backend:8000/alerts/webhook
```

---

## Resource Details

| Resource | Type | Name/ARN |
|---|---|---|
| S3 Bucket | AWS::S3::Bucket | `iot-raw-data` |
| SQS Queue | AWS::SQS::Queue | `sensor-events` |
| SNS Topic | AWS::SNS::Topic | `maintenance-alerts` |
| SNS Subscription | HTTP endpoint | `http://backend:8000/alerts/webhook` |

---

## AWS Client Configuration

In `backend/services/db_service.py`:
```python
def get_sqs_client():
    return boto3.client(
        "sqs",
        endpoint_url=os.environ.get("AWS_ENDPOINT_URL", "http://localhost:4566"),
        region_name="us-east-1",
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "mock"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "mock")
    )
```

---

## Important Notes

- LocalStack version: `latest` (unpinned — may introduce breaking changes)
- The health check uses `awslocal --version`, which may not be available in all LocalStack versions
- This is **NOT** real AWS — it is a local simulation only
