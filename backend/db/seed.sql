-- FixForesight Seed Data Script (Contract Aligned)

-- 1. Populate Machines Directory
INSERT INTO machines (machine_id, machine_name, status, air_temperature, process_temperature, rotational_speed, torque, tool_wear) VALUES
('M101', 'CNC Spindle Unit', 'Warning', 75.0, 78.5, 2500, 4.8, 0.5),
('M102', 'Hydraulic Press', 'Healthy', 48.5, 52.1, 1200, 0.8, 0.0),
('M103', 'Injection Molder', 'Critical', 99.1, 101.3, 1800, 2.1, 12.0),
('M104', 'Robotic Arm Axis 3', 'Healthy', 35.2, 38.6, 900, 1.2, 0.0),
('M105', 'Cooling Compressor', 'Warning', 62.4, 66.8, 3000, 3.4, 4.2);

-- 2. Populate Predictions
INSERT INTO predictions (machine_id, failure_probability, predicted_failure, time_to_failure) VALUES
('M101', 82.0, 'Bearing Failure', '5 Days'),
('M102', 5.0, 'Normal Operation', 'N/A'),
('M103', 94.0, 'Thermal Overheating', '6 Hours'),
('M104', 12.0, 'Normal Operation', 'N/A'),
('M105', 52.0, 'Pressure Valve Leak', '48 Hours');

-- 3. Populate Recommendations
INSERT INTO recommendations (machine_id, recommendation, priority, confidence) VALUES
('M101', 'Schedule bearing replacement immediately. Flush grease system and inspect rotor alignment.', 'High', 91.0),
('M103', 'Perform emergency heat-exchanger cleanout. Replace secondary cooling fan unit and verify coolant pressure.', 'Critical', 96.0),
('M105', 'Inspect pressure line seal. Replace primary pressure valve V-12 and calibrate limit sensors.', 'Medium', 78.0);

-- 4. Populate Alerts
INSERT INTO alerts (machine_id, severity, message) VALUES
('M101', 'High', 'Machine M101 torque exceeded safe envelope (4.8 Nm). Bearing failure risk exceeds 80%.'),
('M103', 'Critical', 'Machine M103 process temperature reached critical levels (101.3°C). core shutdown initiated. Scheduled emergency action required.'),
('M105', 'Medium', 'Machine M105 rotational speed fluctuated. Recalibration of sensor recommended.');

-- 5. Populate Parts Inventory
INSERT INTO parts_inventory (part_name, quantity, min_required, unit_cost) VALUES
('Rotary Bearing B-10', 14, 5, 120.00),
('High-Temp Gasket G-5', 28, 10, 15.50),
('Pressure Valve V-12', 4, 3, 245.00),
('Hydraulic Pump Seal', 3, 5, 45.00),
('Cooling Fan F-8', 19, 8, 35.00),
('Control Board PCB-9', 2, 2, 550.00);

-- 6. Populate Work Orders
INSERT INTO work_orders (machine_id, status, priority, action_required, created_at, completed_at) VALUES
('M101', 'completed', 'Medium', 'Calibrate vibration sensor and tighten mounting bracket bolts.', NOW() - INTERVAL '15 days', NOW() - INTERVAL '15 days' + INTERVAL '2 hours'),
('M102', 'completed', 'Low', 'Routine inspection and oil filter replacement.', NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days' + INTERVAL '1 hour'),
('M103', 'completed', 'High', 'Resolved high heat error. Flushed main coolant lines.', NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days' + INTERVAL '3 hours'),
('M101', 'in_progress', 'High', 'Emergency inspection of rotor bearings due to sudden spike in vibration.', NOW() - INTERVAL '4 hours', NULL);
