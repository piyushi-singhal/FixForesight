# Redux State Management

## Store Configuration

`frontend/src/store/index.ts` — combines all slices.

## Slice Summary

| Slice | State Shape | Key Actions |
|---|---|---|
| `machines` | `{items: Machine[], selectedMachine: Machine\|null, loading, error}` | `fetchMachines`, `fetchMachineRisk`, `selectMachine` |
| `predictions` | `{items: Prediction[], loading, error}` | `fetchPredictions` |
| `recommendations` | `{items: Recommendation[], machineRecs: Recommendation[], loading, error}` | `fetchRecommendations`, `fetchMachineRecommendations` |
| `alerts` | `{items: Alert[], loading, error}` | `fetchAlerts` |
| `workOrders` | `{items: WorkOrder[], loading, error}` | `fetchWorkOrders`, `createWorkOrder`, `updateWorkOrderStatus` |
| `dashboard` | `{data: DashboardData\|null, loading, error}` | `fetchDashboard` |
| `search` | `{results: any[], query: string, loading, error}` | `searchIncidents` |

## Data Flow

```
Component → dispatch(fetchMachines()) → machineService.getMachines()
         → GET /machines
         → store.machines.items updated
         → Component re-renders via useSelector
```
