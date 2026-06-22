-- FixForesight Seed Data Script

-- 1. Populate Parts Inventory
INSERT INTO parts_inventory (part_name, quantity, min_required, unit_cost) VALUES
('Rotary Bearing B-10', 14, 5, 120.00),
('High-Temp Gasket G-5', 28, 10, 15.50),
('Pressure Valve V-12', 4, 3, 245.00),
('Hydraulic Pump Seal', 3, 5, 45.00), -- Low Stock
('Cooling Fan F-8', 19, 8, 35.00),
('Control Board PCB-9', 2, 2, 550.00);

-- 2. Populate Predictions
-- Machine 1: High Risk Bearing Failure
INSERT INTO predictions (machine_id, failure_probability, predicted_failure_type, time_to_failure_hours) VALUES
(1, 0.88, 'Bearing Failure', 18);

-- Machine 2: Healthy Machine
INSERT INTO predictions (machine_id, failure_probability, predicted_failure_type, time_to_failure_hours) VALUES
(2, 0.05, 'Normal Operation', NULL);

-- Machine 3: Critical Overheating Risk
INSERT INTO predictions (machine_id, failure_probability, predicted_failure_type, time_to_failure_hours) VALUES
(3, 0.94, 'Overheating', 6);

-- Machine 4: Medium Risk Pressure Valve Leak
INSERT INTO predictions (machine_id, failure_probability, predicted_failure_type, time_to_failure_hours) VALUES
(4, 0.52, 'Pressure Valve Leak', 48);

-- Machine 5: Low Risk / Normal
INSERT INTO predictions (machine_id, failure_probability, predicted_failure_type, time_to_failure_hours) VALUES
(5, 0.12, 'Slight Mechanical Wear', 144);

-- 3. Populate Recommendations based on the latest predictions
-- For Machine 1 (Bearing Failure, prediction_id = 1)
INSERT INTO recommendations (prediction_id, machine_id, recommended_action, required_parts, maintenance_priority, estimated_duration_hours) VALUES
(1, 1, 'Schedule bearing replacement immediately. Flush grease system and inspect rotor alignment.', '[{"part_name": "Rotary Bearing B-10", "quantity": 1}, {"part_name": "Hydraulic Pump Seal", "quantity": 2}]'::jsonb, 'high', 3.5);

-- For Machine 3 (Overheating, prediction_id = 3)
INSERT INTO recommendations (prediction_id, machine_id, recommended_action, required_parts, maintenance_priority, estimated_duration_hours) VALUES
(3, 3, 'Perform emergency heat-exchanger cleanout. Replace secondary cooling fan unit and verify coolant pressure.', '[{"part_name": "Cooling Fan F-8", "quantity": 1}, {"part_name": "High-Temp Gasket G-5", "quantity": 1}]'::jsonb, 'critical', 2.0);

-- For Machine 4 (Pressure Valve Leak, prediction_id = 4)
INSERT INTO recommendations (prediction_id, machine_id, recommended_action, required_parts, maintenance_priority, estimated_duration_hours) VALUES
(4, 4, 'Inspect pressure line seal. Replace primary pressure valve V-12 and calibrate limit sensors.', '[{"part_name": "Pressure Valve V-12", "quantity": 1}, {"part_name": "High-Temp Gasket G-5", "quantity": 2}]'::jsonb, 'medium', 4.0);

-- For Machine 5 (Slight Mechanical Wear, prediction_id = 5)
INSERT INTO recommendations (prediction_id, machine_id, recommended_action, required_parts, maintenance_priority, estimated_duration_hours) VALUES
(5, 5, 'Perform general maintenance at next scheduled downtime. Lubricate linkages and adjust belt tension.', '[]'::jsonb, 'low', 1.5);

-- 4. Populate Historical/Current Work Orders
INSERT INTO work_orders (machine_id, status, priority, action_required, created_at, completed_at) VALUES
(1, 'completed', 'medium', 'Calibrate vibration sensor and tighten mounting bracket bolts.', NOW() - INTERVAL '15 days', NOW() - INTERVAL '15 days' + INTERVAL '2 hours'),
(2, 'completed', 'low', 'Routine inspection and oil filter replacement.', NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days' + INTERVAL '1 hour'),
(3, 'completed', 'high', 'Resolved high heat error. Flushed main coolant lines.', NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days' + INTERVAL '3 hours'),
(1, 'in_progress', 'high', 'Emergency inspection of rotor bearings due to sudden spike in vibration.', NOW() - INTERVAL '4 hours', NULL),
(3, 'open', 'critical', 'Perform emergency heat-exchanger cleanout and fan replacement.', NOW() - INTERVAL '1 hour', NULL);

-- 5. Populate Historical Sensor Readings for visualization
INSERT INTO sensor_readings (machine_id, temperature, vibration, pressure, error_code, timestamp) VALUES
(1, 68.2, 4.8, 120.4, NULL, NOW() - INTERVAL '10 minutes'),
(1, 69.5, 5.2, 120.1, 'W-VIB-01', NOW() - INTERVAL '8 minutes'),
(1, 71.0, 6.4, 119.8, 'E-VIB-02', NOW() - INTERVAL '6 minutes'),
(1, 72.1, 7.8, 120.5, 'E-VIB-02', NOW() - INTERVAL '4 minutes'),
(1, 73.4, 8.9, 120.2, 'E-BEAR-CRIT', NOW() - INTERVAL '2 minutes'),

(3, 91.5, 2.1, 98.4, 'W-TEMP-HIGH', NOW() - INTERVAL '10 minutes'),
(3, 93.8, 2.2, 97.9, 'W-TEMP-HIGH', NOW() - INTERVAL '8 minutes'),
(3, 95.2, 2.3, 97.5, 'E-TEMP-CRIT', NOW() - INTERVAL '6 minutes'),
(3, 97.4, 2.4, 96.8, 'E-TEMP-CRIT', NOW() - INTERVAL '4 minutes'),
(3, 99.1, 2.5, 96.2, 'E-OVERHEAT-SHUTDOWN', NOW() - INTERVAL '2 minutes'),

(2, 55.4, 1.2, 115.0, NULL, NOW() - INTERVAL '2 minutes'),
(4, 62.1, 2.4, 138.4, 'W-PRES-HIGH', NOW() - INTERVAL '2 minutes'),
(5, 58.7, 1.8, 112.1, NULL, NOW() - INTERVAL '2 minutes');

-- 6. Populate Initial Alerts
INSERT INTO alerts (message_id, topic_arn, subject, message, received_at) VALUES
('msg-923847', 'arn:aws:sns:us-east-1:000000000000:maintenance-alerts', 'CRITICAL Failure Warning: Machine 3', 'Machine 3 is exhibiting critical temperature levels (99.1°C). Core shutdown initiated. Scheduled emergency action required.', NOW() - INTERVAL '2 hours'),
('msg-923848', 'arn:aws:sns:us-east-1:000000000000:maintenance-alerts', 'HIGH Risk Alert: Machine 1', 'Machine 1 vibration velocity exceeded safe envelope (8.9 mm/s). High probability of bearing failure. Maintenance order created.', NOW() - INTERVAL '4 hours');
