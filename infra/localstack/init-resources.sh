#!/bin/bash
echo "Initializing LocalStack resources..."

# Create S3 Bucket
awslocal s3 mb s3://iot-raw-data

# Create SQS Queue
awslocal sqs create-queue --queue-name sensor-events

# Create SNS Topic
awslocal sns create-topic --name maintenance-alerts

# Subscribe the FastAPI backend container to the SNS topic
awslocal sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:000000000000:maintenance-alerts \
  --protocol http \
  --notification-endpoint http://backend:8000/alerts/webhook

echo "LocalStack resources initialized successfully!"
