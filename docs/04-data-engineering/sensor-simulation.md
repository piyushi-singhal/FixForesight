# Sensor Simulation

## Overview

`src/sensor_simulator.py:SensorSimulator` generates realistic industrial machine telemetry with configurable failure scenarios.

---

## Sensor Specifications

| Sensor | Min | Max | Unit |
|---|---|---|---|
| `air_temperature` | 293.15 | 313.15 | K |
| `process_temperature` | 308.15 | 333.15 | K |
| `rotational_speed` | 1000 | 3000 | RPM |
| `torque` | 3 | 100 | Nm |
| `tool_wear` | 0 | 240 | min |
| `vibration` | 0 | 50 | mm/s |

---

## Failure Modes Simulated

| Mode | Description |
|---|---|
| `heat_dissipation` | Temperature differential anomaly |
| `power_loss` | RPM below operational minimum |
| `overstrain` | Torque × RPM exceeds mechanical limit |
| `tool_wear` | Cumulative wear exceeding threshold |
| `random_failure` | Stochastic fault |

---

## Simulation Modes

### Normal Operation
```python
simulator.generate_normal_operation(num_samples=1000)
```
Returns DataFrame with normally-distributed sensor readings.

### Failure Scenario
```python
df, metadata = simulator.generate_failure_scenario(
    failure_type="tool_wear",
    num_samples_normal=50,
    num_samples_degradation=50
)
```

### Multi-Machine Dataset
```python
df = simulator.generate_multiple_machines_dataset(num_machines=3, samples_per_machine=50)
```

### SQS Streaming
```python
simulator.simulate_to_sqs(machine_id="M101", interval_seconds=1.0, num_events=10)
```
Sends events to the `sensor-events` SQS queue (requires LocalStack).

---

## API Trigger

```bash
POST /machines/{machine_id}/simulate?count=10&interval=1.0
```
Runs simulation as a FastAPI background task.
