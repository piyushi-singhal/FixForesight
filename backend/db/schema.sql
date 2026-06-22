-- FixForesight PostgreSQL Database Schema

-- Drop tables if they exist (clean setup)
DROP TABLE IF EXISTS alerts CASCADE;
DROP TABLE IF EXISTS recommendations CASCADE;
DROP TABLE IF EXISTS predictions CASCADE;
DROP TABLE IF EXISTS parts_inventory CASCADE;
DROP TABLE IF EXISTS work_orders CASCADE;
DROP TABLE IF EXISTS sensor_readings CASCADE;

-- 1. Sensor Readings (Raw IoT data stream target)
CREATE TABLE sensor_readings (
    id SERIAL PRIMARY KEY,
    machine_id INT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    temperature DOUBLE PRECISION,
    vibration DOUBLE PRECISION,
    pressure DOUBLE PRECISION,
    error_code VARCHAR(50)
);

-- 2. Predictions (Output from TensorFlow failure prediction model)
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    machine_id INT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    failure_probability DOUBLE PRECISION NOT NULL, -- 0.0 to 1.0
    predicted_failure_type VARCHAR(100), -- 'Bearing Failure', 'Overheating', 'Pressure Valve Leak', etc.
    time_to_failure_hours INT -- Estimated hours remaining before failure
);

-- 3. Work Orders (Current and historical corrective task logs)
CREATE TABLE work_orders (
    id SERIAL PRIMARY KEY,
    machine_id INT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'open', -- 'open', 'in_progress', 'completed', 'cancelled'
    priority VARCHAR(50) NOT NULL, -- 'low', 'medium', 'high', 'critical'
    action_required TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- 4. Parts Inventory (Spare parts stock management)
CREATE TABLE parts_inventory (
    part_id SERIAL PRIMARY KEY,
    part_name VARCHAR(100) NOT NULL UNIQUE,
    quantity INT NOT NULL,
    min_required INT NOT NULL,
    unit_cost DOUBLE PRECISION NOT NULL
);

-- 5. Recommendations (Output from Recommendation model matching failures to parts and actions)
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    prediction_id INT REFERENCES predictions(id) ON DELETE CASCADE,
    machine_id INT NOT NULL,
    recommended_action TEXT NOT NULL,
    required_parts JSONB NOT NULL, -- e.g., [{"part_name": "High-Temp Gasket", "quantity": 2}]
    maintenance_priority VARCHAR(50) NOT NULL, -- 'low', 'medium', 'high', 'critical'
    estimated_duration_hours DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. System Alerts (Sourced from SNS topics / notifications)
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    message_id VARCHAR(100),
    topic_arn VARCHAR(255),
    subject VARCHAR(255),
    message TEXT NOT NULL,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance optimization
CREATE INDEX idx_sensor_readings_machine ON sensor_readings(machine_id, timestamp DESC);
CREATE INDEX idx_predictions_machine ON predictions(machine_id, timestamp DESC);
CREATE INDEX idx_recommendations_machine ON recommendations(machine_id);
CREATE INDEX idx_work_orders_machine ON work_orders(machine_id);
