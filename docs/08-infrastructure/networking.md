# Networking

## Docker Network

All containers use a single bridge network: `pdm-network`.

```
pdm-network (bridge)
├── postgres        → hostname: postgres, port: 5432
├── localstack      → hostname: localstack, port: 4566
├── solr            → hostname: solr, port: 8983
├── backend         → hostname: backend, port: 8000
└── frontend        → hostname: frontend, port: 80 (host: 3000)
```

## Host Port Mappings

| Service | Container Port | Host Port | Access URL |
|---|---|---|---|
| PostgreSQL | 5432 | 5432 | `postgresql://localhost:5432/pdm_db` |
| LocalStack | 4566 | 4566 | `http://localhost:4566` |
| Solr | 8983 | 8983 | `http://localhost:8983/solr` |
| Backend | 8000 | 8000 | `http://localhost:8000` |
| Frontend | 80 | 3000 | `http://localhost:3000` |

## CORS Configuration

Backend allows all origins:
```python
CORSMiddleware(allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
```

This is appropriate for development but must be restricted before any public deployment.
