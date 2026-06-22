-- ============================================================================
-- Industrial AI Predictive Maintenance Platform - PostgreSQL Schema
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. MACHINES Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS machines (
    machine_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    location VARCHAR(255),
    manufacturer VARCHAR(255),
    model VARCHAR(255),
    commissioning_date DATE,
    status VARCHAR(50) DEFAULT 'operational', -- operational, maintenance, retired
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_machines_status ON machines(status);
CREATE INDEX idx_machines_created_at ON machines(created_at);

-- ============================================================================
-- 2. SENSORS Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS sensors (
    sensor_id SERIAL PRIMARY KEY,
    machine_id INTEGER NOT NULL,
    sensor_name VARCHAR(255) NOT NULL,
    sensor_type VARCHAR(100), -- temperature, vibration, rpm, torque, pressure, tool_wear
    unit VARCHAR(50), -- K, mm/s, rpm, Nm, bar, min
    min_value FLOAT,
    max_value FLOAT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id) ON DELETE CASCADE,
    UNIQUE(machine_id, sensor_name)
);

CREATE INDEX idx_sensors_machine_id ON sensors(machine_id);
CREATE INDEX idx_sensors_type ON sensors(sensor_type);

-- ============================================================================
-- 3. SENSOR_READINGS Table (Time-series data)
-- ============================================================================
CREATE TABLE IF NOT EXISTS sensor_readings (
    reading_id BIGSERIAL PRIMARY KEY,
    sensor_id INTEGER NOT NULL,
    machine_id INTEGER NOT NULL,
    value FLOAT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sensor_id) REFERENCES sensors(sensor_id) ON DELETE CASCADE,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id) ON DELETE CASCADE
);

-- Critical: Partition for better performance on large datasets
CREATE INDEX idx_sensor_readings_machine_id ON sensor_readings(machine_id);
CREATE INDEX idx_sensor_readings_sensor_id ON sensor_readings(sensor_id);
CREATE INDEX idx_sensor_readings_timestamp ON sensor_readings(timestamp);
CREATE INDEX idx_sensor_readings_machine_timestamp ON sensor_readings(machine_id, timestamp);

-- ============================================================================
-- 4. PREDICTIONS Table (ML model outputs)
-- ============================================================================
CREATE TABLE IF NOT EXISTS predictions (
    prediction_id BIGSERIAL PRIMARY KEY,
    machine_id INTEGER NOT NULL,
    prediction_timestamp TIMESTAMP NOT NULL,
    failure_probability FLOAT NOT NULL CHECK (failure_probability >= 0 AND failure_probability <= 1),
    days_to_failure INT, -- Estimated days until failure (NULL if low risk)
    risk_level VARCHAR(50), -- low, medium, high, critical
    failure_type VARCHAR(100), -- heat dissipation, power loss, overstrain, tool wear, random failure
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id) ON DELETE CASCADE
);

CREATE INDEX idx_predictions_machine_id ON predictions(machine_id);
CREATE INDEX idx_predictions_timestamp ON predictions(prediction_timestamp);
CREATE INDEX idx_predictions_risk_level ON predictions(risk_level);

-- ============================================================================
-- 5. RECOMMENDATIONS Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS recommendations (
    recommendation_id BIGSERIAL PRIMARY KEY,
    machine_id INTEGER NOT NULL,
    prediction_id BIGINT,
    recommendation_type VARCHAR(100), -- preventive, urgent, replacement
    action TEXT NOT NULL,
    priority VARCHAR(50), -- low, medium, high, critical
    estimated_cost FLOAT,
    spare_parts JSON, -- Store as JSON: [{"part_name": "", "part_id": "", "quantity": 1}]
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    addressed BOOLEAN DEFAULT FALSE,
    addressed_date TIMESTAMP,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id) ON DELETE CASCADE,
    FOREIGN KEY (prediction_id) REFERENCES predictions(prediction_id) ON DELETE SET NULL
);

CREATE INDEX idx_recommendations_machine_id ON recommendations(machine_id);
CREATE INDEX idx_recommendations_priority ON recommendations(priority);
CREATE INDEX idx_recommendations_addressed ON recommendations(addressed);

-- ============================================================================
-- 6. MAINTENANCE_HISTORY Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS maintenance_history (
    maintenance_id BIGSERIAL PRIMARY KEY,
    machine_id INTEGER NOT NULL,
    maintenance_type VARCHAR(100), -- preventive, corrective, inspection
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    description TEXT,
    cost FLOAT,
    performed_by VARCHAR(255),
    parts_replaced JSON, -- Store as JSON: [{"part_name": "", "quantity": 1}]
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id) ON DELETE CASCADE
);

CREATE INDEX idx_maintenance_machine_id ON maintenance_history(machine_id);
CREATE INDEX idx_maintenance_date ON maintenance_history(start_date);

-- ============================================================================
-- 7. FAILURE_EVENTS Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS failure_events (
    failure_id BIGSERIAL PRIMARY KEY,
    machine_id INTEGER NOT NULL,
    failure_type VARCHAR(100),
    failure_timestamp TIMESTAMP NOT NULL,
    description TEXT,
    severity VARCHAR(50), -- minor, major, critical
    was_predicted BOOLEAN,
    prediction_id BIGINT,
    days_until_predicted INT, -- How many days before actual failure was it predicted?
    root_cause TEXT,
    resolution TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id) ON DELETE CASCADE,
    FOREIGN KEY (prediction_id) REFERENCES predictions(prediction_id) ON DELETE SET NULL
);

CREATE INDEX idx_failure_events_machine_id ON failure_events(machine_id);
CREATE INDEX idx_failure_events_timestamp ON failure_events(failure_timestamp);

-- ============================================================================
-- 8. ALERTS Table (Real-time alerts)
-- ============================================================================
CREATE TABLE IF NOT EXISTS alerts (
    alert_id BIGSERIAL PRIMARY KEY,
    machine_id INTEGER NOT NULL,
    alert_type VARCHAR(100), -- anomaly, threshold_violation, prediction_alert
    severity VARCHAR(50), -- info, warning, critical
    message TEXT NOT NULL,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id) ON DELETE CASCADE
);

CREATE INDEX idx_alerts_machine_id ON alerts(machine_id);
CREATE INDEX idx_alerts_resolved ON alerts(is_resolved);
CREATE INDEX idx_alerts_created_at ON alerts(created_at);

-- ============================================================================
-- 9. ENGINEERED_FEATURES Table (Pre-computed features for model)
-- ============================================================================
CREATE TABLE IF NOT EXISTS engineered_features (
    feature_id BIGSERIAL PRIMARY KEY,
    machine_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    temperature_diff FLOAT, -- Process temp - Air temp
    power FLOAT, -- RPM * Torque
    wear_rate FLOAT, -- Tool wear / RPM
    thermal_stress FLOAT, -- Normalized temperature
    mechanical_stress FLOAT, -- Normalized torque & RPM
    vibration_energy FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id) ON DELETE CASCADE
);

CREATE INDEX idx_engineered_features_machine_id ON engineered_features(machine_id);
CREATE INDEX idx_engineered_features_timestamp ON engineered_features(timestamp);

-- ============================================================================
-- 10. ML_MODELS Table (Track trained models)
-- ============================================================================
CREATE TABLE IF NOT EXISTS ml_models (
    model_id SERIAL PRIMARY KEY,
    model_name VARCHAR(255) NOT NULL,
    model_version VARCHAR(50) NOT NULL UNIQUE,
    model_type VARCHAR(100), -- lstm, random_forest, gradient_boosting, etc.
    training_date TIMESTAMP NOT NULL,
    accuracy FLOAT,
    precision FLOAT,
    recall FLOAT,
    f1_score FLOAT,
    auc_score FLOAT,
    training_samples INT,
    model_path VARCHAR(500),
    description TEXT,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ml_models_active ON ml_models(is_active);

-- ============================================================================
-- 11. DATA_QUALITY_METRICS Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS data_quality_metrics (
    metric_id BIGSERIAL PRIMARY KEY,
    machine_id INTEGER NOT NULL,
    date DATE NOT NULL,
    total_readings INT,
    missing_readings INT,
    anomalous_readings INT,
    completeness_percentage FLOAT,
    data_quality_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id) ON DELETE CASCADE,
    UNIQUE(machine_id, date)
);

CREATE INDEX idx_data_quality_machine_id ON data_quality_metrics(machine_id);

-- ============================================================================
-- Sample Data Insertion
-- ============================================================================

-- Insert sample machines
INSERT INTO machines (name, location, manufacturer, model, status) VALUES
    ('Machine-A-01', 'Production Floor 1', 'SIEMENS', 'S7-1500', 'operational'),
    ('Machine-A-02', 'Production Floor 1', 'SIEMENS', 'S7-1500', 'operational'),
    ('Machine-B-01', 'Production Floor 2', 'ABB', 'IRB 6700', 'operational'),
    ('Machine-C-01', 'Assembly Line', 'FANUC', 'M-20iA', 'maintenance')
ON CONFLICT DO NOTHING;

-- Insert sample sensors for Machine-A-01
INSERT INTO sensors (machine_id, sensor_name, sensor_type, unit, min_value, max_value) VALUES
    (1, 'Temperature Sensor 1', 'temperature', 'K', 293.15, 323.15),
    (1, 'RPM Sensor', 'rpm', 'rpm', 0, 3000),
    (1, 'Torque Sensor', 'torque', 'Nm', 0, 100),
    (1, 'Vibration Sensor', 'vibration', 'mm/s', 0, 50),
    (1, 'Tool Wear Sensor', 'tool_wear', 'min', 0, 200)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- AUDIT TRAIL (Optional - for tracking changes)
-- ============================================================================
CREATE TABLE IF NOT EXISTS audit_log (
    log_id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(100),
    operation VARCHAR(20), -- INSERT, UPDATE, DELETE
    record_id BIGINT,
    old_values JSON,
    new_values JSON,
    changed_by VARCHAR(255),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_log_table ON audit_log(table_name);
CREATE INDEX idx_audit_log_timestamp ON audit_log(changed_at);

-- ============================================================================
-- VIEWS for Common Queries
-- ============================================================================

-- View: Latest predictions for each machine
CREATE OR REPLACE VIEW latest_predictions AS
SELECT DISTINCT ON (machine_id)
    machine_id,
    failure_probability,
    risk_level,
    days_to_failure,
    prediction_timestamp
FROM predictions
ORDER BY machine_id, prediction_timestamp DESC;

-- View: Outstanding recommendations
CREATE OR REPLACE VIEW outstanding_recommendations AS
SELECT 
    r.recommendation_id,
    m.name as machine_name,
    r.action,
    r.priority,
    r.created_at,
    p.failure_probability
FROM recommendations r
JOIN machines m ON r.machine_id = m.machine_id
LEFT JOIN predictions p ON r.prediction_id = p.prediction_id
WHERE r.addressed = FALSE
ORDER BY r.priority, r.created_at;

-- View: Machine health summary
CREATE OR REPLACE VIEW machine_health_summary AS
SELECT 
    m.machine_id,
    m.name,
    m.status,
    COALESCE(lp.failure_probability, 0) as failure_probability,
    COALESCE(lp.risk_level, 'unknown') as risk_level,
    (SELECT COUNT(*) FROM alerts WHERE machine_id = m.machine_id AND is_resolved = FALSE) as unresolved_alerts,
    (SELECT COUNT(*) FROM recommendations WHERE machine_id = m.machine_id AND addressed = FALSE) as pending_recommendations,
    (SELECT MAX(timestamp) FROM sensor_readings WHERE machine_id = m.machine_id) as last_reading_time
FROM machines m
LEFT JOIN latest_predictions lp ON m.machine_id = lp.machine_id;

-- ============================================================================
-- Create tablespaces for partitioning (if needed for large deployments)
-- ============================================================================
-- For production with millions of rows, consider partitioning sensor_readings by date
-- Example: PARTITION BY RANGE (timestamp)
-- This improves query performance on time-series data
