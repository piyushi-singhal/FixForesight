# Component Architecture

## Component Map

```
FixForesight/
├── src/                        ← ML & Data Engineering Components
│   ├── sensor_simulator.py     ← SensorSimulator class
│   ├── clean_dataset.py        ← Data cleaning utilities
│   ├── data_pipeline.py        ← SensorDataProcessor class
│   ├── feature_engineering_pipeline.py  ← Full feature engineering
│   ├── engineer_features.py    ← Standalone feature utils
│   ├── ml_pipeline.py          ← FeatureEngineer + PredictiveMaintenanceModel
│   ├── predictions_pipeline.py ← Orchestrates dataset → DB pipeline
│   └── recommendation_engine.py ← RecommendationEngine class
│
├── models/                     ← Serialised ML Artifacts
│   ├── best_model.pkl          ← GradientBoostingClassifier (canonical)
│   ├── scaler.pkl              ← RobustScaler (canonical)
│   ├── gradient_boosting_*/    ← Timestamped training run artifacts
│   ├── random_forest_*/        ← Timestamped training run artifacts
│   ├── model_comparison.csv    ← Evaluation results table
│   └── train_models.py         ← Training entry-point (separate script)
│
├── backend/                    ← FastAPI Application
│   ├── main.py                 ← App factory, startup hook, route registration
│   ├── routes/                 ← One file per resource
│   │   ├── machines.py
│   │   ├── predictions.py
│   │   ├── recommendations.py
│   │   ├── alerts.py
│   │   ├── analytics.py
│   │   ├── work_orders.py
│   │   ├── search.py
│   │   └── dashboard.py
│   ├── services/
│   │   └── db_service.py       ← All business logic + ML model loading
│   ├── database/
│   │   ├── connection.py       ← SQLAlchemy engine + SessionLocal
│   │   ├── models.py           ← ORM table definitions (source of truth)
│   │   └── queries.py          ← Raw ORM query helpers
│   ├── schemas/
│   │   └── models.py           ← Pydantic request/response models
│   ├── db/
│   │   ├── schema.sql          ← SQL init script (Docker entrypoint)
│   │   └── seed.sql            ← Initial seed data
│   └── alembic/                ← Migration files
│
├── frontend/                   ← React SPA
│   ├── public/
│   │   └── index.html          ← Legacy HTML dashboard (also served by FastAPI)
│   └── src/
│       ├── index.jsx           ← React entry point
│       ├── App.jsx             ← Main component (73 KB — monolithic)
│       ├── index.css           ← Global styles
│       ├── types.ts            ← TypeScript types
│       ├── services/           ← API client functions
│       │   ├── apiConfig.js
│       │   ├── machineService.ts
│       │   ├── predictionService.ts
│       │   ├── recommendationService.ts
│       │   ├── alertService.ts
│       │   ├── workOrderService.ts
│       │   ├── analyticsService.ts
│       │   ├── dashboardService.ts
│       │   └── searchService.ts
│       └── store/              ← Redux Toolkit slices
│           ├── index.ts        ← Store configuration
│           ├── machinesSlice.ts
│           ├── predictionsSlice.ts
│           ├── recommendationsSlice.ts
│           ├── alertsSlice.ts
│           ├── workOrdersSlice.ts
│           ├── dashboardSlice.ts
│           └── searchSlice.ts
│
├── infra/
│   └── localstack/
│       └── init-resources.sh  ← Creates S3 bucket, SQS queue, SNS topic + subscription
│
├── data/                       ← Dataset files (NOT in Docker image)
├── docker-compose.yml
├── alembic.ini
└── requirements.txt
```

---

## Key Coupling Points

| From | To | Coupling |
|---|---|---|
| `db_service.py` | `models/best_model.pkl` | Loads at module import time; failure → rule-based fallback |
| `db_service.py` | `src/recommendation_engine.py` | Optional import; fallback if import fails |
| `main.py:startup` | `src/predictions_pipeline.py` | Calls `run_predictions_pipeline()` directly |
| `backend routes` | `db_service.py` | All routes delegate to service functions |
| `frontend services` | `apiConfig.js:BASE_URL` | Single API base URL configuration |
| `connection.py` | `DATABASE_URL` env var | Falls back to SQLite if Postgres unavailable |
