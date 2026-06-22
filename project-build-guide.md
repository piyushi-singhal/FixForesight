# IoT Predictive Maintenance + Recommendation Engine
### Full Build & Execution Guide (Local, $0 cost, AWS-equivalent via LocalStack)

---

## 1. Final Architecture (What You're Building)

```
                         ┌─────────────────────┐
                         │   Sensor Simulator   │  (Python script generating fake IoT data)
                         └──────────┬───────────┘
                                    │ publishes to
                                    ▼
                         ┌─────────────────────┐
                         │   SQS (LocalStack)   │  ingestion queue
                         └──────────┬───────────┘
                                    │ consumed by
                                    ▼
                         ┌─────────────────────┐
                         │   Spark (PySpark)    │  feature engineering, windowed aggregation
                         │   reads/writes to S3  │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                                ▼
        ┌─────────────────────┐           ┌─────────────────────┐
        │ TensorFlow Model     │           │  Recommendation      │
        │ (failure prediction) │           │  Model (action/parts/│
        │                      │           │  priority ranking)   │
        └──────────┬───────────┘           └──────────┬───────────┘
                    │                                   │
                    └───────────────┬───────────────────┘
                                     ▼
                         ┌─────────────────────┐
                         │   Postgres (RDS sim) │  predictions, work_orders,
                         │                      │  parts_inventory, recommendations
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
          ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
          │ Solr (search) │ │ SNS (alerts) │ │ FastAPI       │
          │ historical    │ │ LocalStack   │ │ (Backend API) │
          │ incidents     │ │              │ │               │
          └──────────────┘ └──────────────┘ └──────┬───────┘
                                                     ▼
                                          ┌─────────────────────┐
                                          │  React + Redux UI    │
                                          │  (dashboard)          │
                                          └─────────────────────┘
```

**Everything above runs as Docker containers on your laptop, orchestrated by Docker Compose.**

---

## 2. Repository Structure

```
iot-pdm-recommender/
├── docker-compose.yml
├── .env
├── infra/
│   ├── cloudformation/
│   │   └── stack.yaml          # IaC template (tested against LocalStack)
│   └── ansible/
│       └── playbook.yml        # config management (for EC2-equivalent setup)
├── data-sim/
│   └── sensor_simulator.py     # generates fake IoT sensor events → SQS
├── spark-jobs/
│   ├── feature_engineering.py  # reads raw events, aggregates, writes to S3
│   └── requirements.txt
├── ml/
│   ├── train_failure_model.py  # TensorFlow training script
│   ├── train_recommender.py    # recommendation model training
│   └── models/                 # saved model artifacts
├── backend/
│   ├── app.py                  # FastAPI app
│   ├── db/
│   │   └── schema.sql          # Postgres schema (work_orders, recommendations, etc.)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── store/              # Redux slices
│   │   └── components/
│   ├── package.json
│   ├── webpack.config.js
│   └── Dockerfile
└── README.md
```

---

## 3. Build Order (Why This Sequence Matters)

Build in this exact order — each stage produces something the next stage needs. Building out of order is the #1 cause of "nothing works" debugging sessions.

| Stage | What you build | Depends on |
|---|---|---|
| 1 | Postgres schema + Docker Compose skeleton | nothing |
| 2 | LocalStack + S3/SQS/SNS setup | Stage 1 |
| 3 | Sensor simulator pushing to SQS | Stage 2 |
| 4 | Spark job consuming → S3 → Postgres | Stage 3 |
| 5 | TensorFlow failure prediction model | Stage 4 (needs feature data) |
| 6 | Recommendation model | Stage 5 (needs failure predictions + work_orders) |
| 7 | FastAPI backend serving everything | Stages 5 & 6 |
| 8 | React/Redux frontend | Stage 7 (needs API) |
| 9 | Solr indexing historical incidents | Stage 1 data available |
| 10 | CloudFormation + Ansible (IaC docs) | All — written last, describing what you built |

---

## 4. Step-by-Step Execution

### Step 0 — Prerequisites
Install on your machine:
- Docker + Docker Compose
- Python 3.10+
- Node.js 18+ (for React/Webpack)
- AWS CLI (used to talk to LocalStack, not real AWS)

Verify:
```bash
docker --version
docker compose version
python3 --version
node --version
aws --version
```

### Step 1 — Core `docker-compose.yml`
This single file is the backbone. Define services for: `localstack`, `postgres`, `solr`, `spark` (or run Spark via spark-submit in a Python container), `backend`, `frontend`.

Key things to get right (common failure points):
- Give every service a fixed `container_name` and put them on the same Docker `network`
- Postgres must expose `5432`, LocalStack `4566`, Solr `8983`, backend `8000`, frontend `3000`
- Use `depends_on` so Postgres/LocalStack start before backend tries to connect
- Add `healthcheck` blocks — without them, your backend will try to connect before Postgres is actually ready and crash on startup (this is the single most common error in multi-container setups)

```bash
docker compose up -d postgres localstack solr
docker compose ps   # confirm all 3 show "healthy"
```

### Step 2 — Initialize LocalStack resources
Once LocalStack is up, create the S3 bucket, SQS queue, and SNS topic it needs — LocalStack doesn't pre-create these for you.

```bash
aws --endpoint-url=http://localhost:4566 s3 mb s3://iot-raw-data
aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name sensor-events
aws --endpoint-url=http://localhost:4566 sns create-topic --name maintenance-alerts
```

Save these outputs (queue URL, topic ARN) into your `.env` — your Python code will need them.

**Checkpoint**: list the bucket to confirm it exists before moving on.
```bash
aws --endpoint-url=http://localhost:4566 s3 ls
```

### Step 3 — Initialize Postgres schema
Run your `schema.sql` against the running Postgres container.

```bash
docker exec -i postgres psql -U postgres -d pdm_db < backend/db/schema.sql
```

**Checkpoint**: connect and list tables.
```bash
docker exec -it postgres psql -U postgres -d pdm_db -c "\dt"
```
You should see `sensor_readings`, `work_orders`, `parts_inventory`, `recommendations`, `predictions`.

### Step 4 — Run the sensor simulator
This Python script generates fake machine sensor readings and pushes them to the SQS queue every few seconds.

```bash
cd data-sim
pip install boto3 faker --break-system-packages
python3 sensor_simulator.py
```

**Checkpoint**: confirm messages are landing in the queue.
```bash
aws --endpoint-url=http://localhost:4566 sqs receive-message --queue-url <your-queue-url>
```
If this returns nothing, the simulator isn't running or the queue URL in `.env` doesn't match — fix this before going further, every downstream stage depends on it.

### Step 5 — Run the Spark feature engineering job
Spark reads from SQS (or from raw files dumped to S3 by the simulator — simpler for v1), aggregates into time windows (rolling mean, std dev, rate of change per sensor), and writes features to S3 + a Postgres table.

```bash
cd spark-jobs
pip install -r requirements.txt --break-system-packages
spark-submit feature_engineering.py
```

**Checkpoint**: check the output landed in S3.
```bash
aws --endpoint-url=http://localhost:4566 s3 ls s3://iot-raw-data/features/
```

### Step 6 — Train the TensorFlow failure prediction model
Use the engineered features as input, train a classifier (failure within N days: yes/no, or regression for time-to-failure).

```bash
cd ml
pip install tensorflow pandas scikit-learn --break-system-packages
python3 train_failure_model.py
```
This saves a model to `ml/models/failure_model/`.

**Checkpoint**: run a quick local inference test on a sample row before wiring it into the API — catches shape/schema mismatches early, which is the most common TensorFlow integration bug.

### Step 7 — Train the recommendation model
Using `work_orders` (action → outcome history) and `parts_inventory`, train your ranking model (start simple: a co-occurrence/popularity-based recommender before anything fancier — gets you a working pipeline fast).

```bash
python3 train_recommender.py
```

### Step 8 — Build and run the FastAPI backend
The backend loads both models, exposes endpoints like:
- `GET /machines/{id}/risk` → failure probability
- `GET /machines/{id}/recommendations` → recommended action + parts
- `GET /alerts` → recent SNS-triggered alerts

```bash
cd backend
docker build -t pdm-backend .
docker compose up -d backend
```

**Checkpoint**:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/machines/1/risk
```
If you get a connection refused error here, it's almost always one of: Postgres not ready when backend started (fix with healthchecks), or wrong DB host in your connection string (should be the Docker service name `postgres`, not `localhost`, when calling from inside another container).

### Step 9 — Build and run the React/Redux frontend
```bash
cd frontend
npm install
npm run build       # Webpack bundles for production
docker compose up -d frontend
```

**Checkpoint**: open `http://localhost:3000` — dashboard should load and successfully fetch from the backend. If the page loads but data doesn't appear, check the browser console for CORS errors — add `CORSMiddleware` to FastAPI allowing `http://localhost:3000`.

### Step 10 — Index historical incidents into Solr
```bash
curl -X POST -H 'Content-type:application/json' \
  http://localhost:8983/solr/incidents/update \
  --data-binary @sample_incidents.json
```

**Checkpoint**: query it back.
```bash
curl "http://localhost:8983/solr/incidents/select?q=*:*"
```

### Step 11 — Write CloudFormation + Ansible (documentation of "how this maps to real AWS")
These don't need to *run* against real AWS. Write them to describe the production deployment, test syntax validity with `aws cloudformation validate-template`, and keep them in the repo as proof of IaC skill.

```bash
aws cloudformation validate-template --template-body file://infra/cloudformation/stack.yaml
```

---

## 5. Common Errors and Fixes (Read Before You Start)

| Error | Cause | Fix |
|---|---|---|
| `Connection refused` on backend startup | Postgres not ready yet | Add `healthcheck` + `depends_on: condition: service_healthy` |
| `NoSuchBucket` from boto3 | Forgot Step 2, or wrong endpoint URL | Always pass `endpoint_url=http://localstack:4566` inside containers (not `localhost`) |
| Spark job hangs or OOMs | Default memory too low for container | Set `spark.driver.memory` / `spark.executor.memory` explicitly, keep dataset small for local dev |
| React shows blank page, no errors | Webpack build not rebuilt after code change | Re-run `npm run build` or use `npm start` (dev server) instead during development |
| CORS error in browser console | Frontend and backend on different ports | Add FastAPI `CORSMiddleware`, allow your frontend origin |
| `docker-compose` services can't reach each other | Using `localhost` between containers | Use the **service name** as the hostname (Docker's internal DNS), not `localhost` |
| TensorFlow model input shape mismatch | Feature engineering output changed after model was trained | Pin a feature schema/version; retrain if upstream features change |
| LocalStack data disappears on restart | No persistence volume mounted | Add a volume for `/var/lib/localstack` in compose if you want state across restarts |

---

## 6. Definition of "Successfully Running"

You'll know the whole system works end-to-end when:
1. Simulator is producing sensor events → visible in SQS
2. Spark job runs and produces feature files in S3
3. Postgres has populated `predictions` and `recommendations` tables
4. `curl localhost:8000/machines/1/risk` returns a real probability
5. Dashboard at `localhost:3000` shows live machine risk + recommended action
6. Solr returns results for a historical incident search
7. `docker compose ps` shows every service as `Up (healthy)`

Run them **in this order** the first time — don't try to start everything via `docker compose up -d` all at once until you've validated each stage individually. That's the difference between debugging one broken thing vs. debugging six interacting broken things at once.
