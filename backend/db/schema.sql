-- FixForesight PostgreSQL Database Schema (Contract Aligned)

DROP TABLE IF EXISTS alerts CASCADE;
DROP TABLE IF EXISTS recommendations CASCADE;
DROP TABLE IF EXISTS predictions CASCADE;
DROP TABLE IF EXISTS work_orders CASCADE;
DROP TABLE IF EXISTS parts_inventory CASCADE;
DROP TABLE IF EXISTS machines CASCADE;

-- 1. Machines Directory Table
CREATE TABLE machines (
    machine_id VARCHAR(50) PRIMARY KEY,
    machine_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    temperature DOUBLE PRECISION NOT NULL,
    pressure DOUBLE PRECISION NOT NULL,
    vibration DOUBLE PRECISION NOT NULL,
    rpm INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Predictions Table (TensorFlow output target)
CREATE TABLE predictions (
    prediction_id SERIAL PRIMARY KEY,
    machine_id VARCHAR(50) REFERENCES machines(machine_id) ON DELETE CASCADE,
    failure_probability DOUBLE PRECISION NOT NULL, -- 0.0 to 100.0 (or 0.0 to 1.0, contract specifies 82 as 82%)
    predicted_failure VARCHAR(255) NOT NULL, -- 'Bearing Failure', etc.
    time_to_failure VARCHAR(100) NOT NULL, -- '5 Days', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Recommendations Table (Recommendation model output)
CREATE TABLE recommendations (
    recommendation_id SERIAL PRIMARY KEY,
    machine_id VARCHAR(50) REFERENCES machines(machine_id) ON DELETE CASCADE,
    recommendation TEXT NOT NULL, -- 'Replace Bearing', etc.
    priority VARCHAR(50) NOT NULL, -- 'High', etc.
    confidence DOUBLE PRECISION NOT NULL, -- 0.0 to 100.0
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Alerts Table (SNS/SQS alerts receiver)
CREATE TABLE alerts (
    alert_id SERIAL PRIMARY KEY,
    machine_id VARCHAR(50) REFERENCES machines(machine_id) ON DELETE CASCADE,
    severity VARCHAR(50) NOT NULL, -- 'Critical', etc.
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Parts Inventory (Spare parts stock management)
CREATE TABLE parts_inventory (
    part_id SERIAL PRIMARY KEY,
    part_name VARCHAR(100) NOT NULL UNIQUE,
    quantity INT NOT NULL,
    min_required INT NOT NULL,
    unit_cost DOUBLE PRECISION NOT NULL
);

-- 6. Work Orders (Mitigation task logging)
CREATE TABLE work_orders (
    id SERIAL PRIMARY KEY,
    machine_id VARCHAR(50) REFERENCES machines(machine_id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'open', -- 'open', 'in_progress', 'completed'
    priority VARCHAR(50) NOT NULL,
    action_required TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_predictions_machine ON predictions(machine_id);
CREATE INDEX idx_recommendations_machine ON recommendations(machine_id);
CREATE INDEX idx_alerts_machine ON alerts(machine_id);
CREATE INDEX idx_work_orders_machine ON work_orders(machine_id);
