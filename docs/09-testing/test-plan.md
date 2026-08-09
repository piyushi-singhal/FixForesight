# Test Plan

## Current Test Coverage

| Area | Coverage | Files |
|---|---|---|
| Sensor Simulator | ✅ Component tested | tests_integration.py TEST 1 |
| Feature Engineering | ✅ Component tested | tests_integration.py TEST 2 |
| ML Training & Prediction | ✅ Component tested | tests_integration.py TEST 3 |
| Recommendation Engine | ✅ Component tested | tests_integration.py TEST 4 |
| Data Processing | ✅ Component tested | tests_integration.py TEST 5 |
| Prediction Pipeline (API) | ✅ API tested | tests_api_e2e.py step 1 |
| Machine & Prediction retrieval | ✅ API tested | tests_api_e2e.py steps 2-3 |
| Work Order lifecycle | ✅ API tested | tests_api_e2e.py steps 4-6 |
| SQS consumer flow | ❌ Not tested | — |
| SNS webhook | ❌ Not tested | — |
| Solr search | ❌ Not tested | — |
| Docker clean build | ❌ Not tested | — |
| Frontend UI | ❌ Not tested | — |
| Database migrations | ❌ Not automated | — |

## Recommended Additional Tests

### Unit Tests (Missing)
- `predict_machine_failure()` with boundary values
- `update_work_order_status()` with invalid status values
- `sync_data_to_solr()` with Solr unreachable

### Integration Tests (Missing)
- SQS message → consumer thread → database insertion
- SNS publish → webhook → alert storage
- Solr sync → search returns results

### Performance Tests (Not Implemented)
- Pipeline throughput for 10,000 records
- API response time under concurrent load

## Running Tests

```bash
# Component tests
python tests_integration.py

# API E2E (requires backend running)
python tests_api_e2e.py

# With pytest (if installed)
pytest tests_integration.py -v
```
