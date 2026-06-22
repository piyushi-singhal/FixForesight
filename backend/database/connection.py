from datetime import datetime, timedelta
import random

class MockDB:
    def __init__(self):
        # 1. Machines Directory (Internal representation, status/name will be mapped dynamically on frontend)
        self.machines = {
            "M101": {"machine_id": "M101", "machine_name": "CNC Spindle Unit", "status": "Warning", "air_temperature": 302.5, "process_temperature": 309.1, "rotational_speed": 1450, "torque": 40.2, "tool_wear": 120.0},
            "M102": {"machine_id": "M102", "machine_name": "Hydraulic Press", "status": "Healthy", "air_temperature": 295.1, "process_temperature": 301.2, "rotational_speed": 1000, "torque": 15.2, "tool_wear": 5.0},
            "M103": {"machine_id": "M103", "machine_name": "Injection Molder", "status": "Critical", "air_temperature": 312.4, "process_temperature": 321.8, "rotational_speed": 1800, "torque": 48.5, "tool_wear": 150.0},
            "M104": {"machine_id": "M104", "machine_name": "Robotic Arm Axis 3", "status": "Healthy", "air_temperature": 298.0, "process_temperature": 304.5, "rotational_speed": 900, "torque": 10.1, "tool_wear": 2.0},
            "M105": {"machine_id": "M105", "machine_name": "Cooling Compressor", "status": "Warning", "air_temperature": 305.6, "process_temperature": 314.2, "rotational_speed": 2200, "torque": 35.0, "tool_wear": 95.0}
        }

        # 2. Predictions (TensorFlow model output schema)
        self.predictions = {
            "M101": {"machine_id": "M101", "failure_probability": 82.0, "predicted_failure": "Machine Failure", "time_to_failure": "5 Days"},
            "M102": {"machine_id": "M102", "failure_probability": 5.0, "predicted_failure": "Normal Operation", "time_to_failure": "N/A"},
            "M103": {"machine_id": "M103", "failure_probability": 94.0, "predicted_failure": "Machine Failure", "time_to_failure": "6 Hours"},
            "M104": {"machine_id": "M104", "failure_probability": 12.0, "predicted_failure": "Normal Operation", "time_to_failure": "N/A"},
            "M105": {"machine_id": "M105", "failure_probability": 52.0, "predicted_failure": "Machine Failure", "time_to_failure": "48 Hours"}
        }

        # 3. Recommendations (Recommendation engine output schema)
        self.recommendations = {
            "M101": {
                "machine_id": "M101",
                "recommendation": "Schedule preventive maintenance",
                "priority": "High",
                "confidence": 91.0,
                "required_parts": [{"part_name": "Rotary Bearing B-10", "quantity": 1}, {"part_name": "Hydraulic Pump Seal", "quantity": 2}],
                "estimated_duration_hours": 3.5,
                "created_at": (datetime.now() - timedelta(hours=1)).isoformat()
            },
            "M103": {
                "machine_id": "M103",
                "recommendation": "Schedule emergency maintenance",
                "priority": "Critical",
                "confidence": 96.0,
                "required_parts": [{"part_name": "Cooling Fan F-8", "quantity": 1}, {"part_name": "High-Temp Gasket G-5", "quantity": 1}],
                "estimated_duration_hours": 2.0,
                "created_at": (datetime.now() - timedelta(minutes=45)).isoformat()
            },
            "M105": {
                "machine_id": "M105",
                "recommendation": "Schedule preventive maintenance",
                "priority": "Medium",
                "confidence": 78.0,
                "required_parts": [{"part_name": "Pressure Valve V-12", "quantity": 1}, {"part_name": "High-Temp Gasket G-5", "quantity": 2}],
                "estimated_duration_hours": 4.0,
                "created_at": (datetime.now() - timedelta(hours=2)).isoformat()
            }
        }

        # 4. Event Alerts (SNS mock alert feed)
        self.alerts = [
            {"alert_id": 1, "machine_id": "M101", "severity": "Critical", "message": "Machine M101 torque exceeded safe envelope (40.2 Nm). Bearing failure risk exceeds 80%.", "created_at": (datetime.now() - timedelta(hours=4)).isoformat()},
            {"alert_id": 2, "machine_id": "M103", "severity": "Critical", "message": "Machine M103 process temperature reached critical levels (321.8°C). Core shutdown initiated. Scheduled emergency action required.", "created_at": (datetime.now() - timedelta(hours=2)).isoformat()},
            {"alert_id": 3, "machine_id": "M105", "severity": "Warning", "message": "Machine M105 rotational speed fluctuated. Recalibration of sensor recommended.", "created_at": (datetime.now() - timedelta(minutes=30)).isoformat()}
        ]

        # 5. Historical Sensor Readings (Sparkline telemetry charts)
        self.sensor_history = {}
        for m_id in ["M101", "M102", "M103", "M104", "M105"]:
            self.sensor_history[m_id] = []
            for i in range(20, 0, -1):
                base_time = datetime.now() - timedelta(minutes=i*2)
                if m_id == "M101":
                    air_temp = 295.0 + (20 - i) * 0.4
                    proc_temp = 300.5 + (20 - i) * 0.45
                    speed = 1400 + (i % 5) * 10
                    torque = 35.0 + (20 - i) * 0.3
                    wear = 100.0 + (20 - i) * 1.0
                elif m_id == "M103":
                    air_temp = 300.0 + (20 - i) * 0.65
                    proc_temp = 308.2 + (20 - i) * 0.7
                    speed = 1750 + (i % 3) * 15
                    torque = 40.0 + (20 - i) * 0.45
                    wear = 120.0 + (20 - i) * 1.5
                elif m_id == "M105":
                    air_temp = 298.0 + (20 - i) * 0.38
                    proc_temp = 305.4 + (20 - i) * 0.45
                    speed = 2100 + (20 - i) * 5
                    torque = 28.0 + (i % 3) * 2.0
                    wear = 70.0 + (20 - i) * 1.25
                else:
                    air_temp = 290.0 + (i % 4) * 0.2
                    proc_temp = 296.0 + (i % 4) * 0.25
                    speed = 950 + (i % 5) * 10
                    torque = 12.0 + (i % 3) * 0.5
                    wear = 1.0 + (20 - i) * 0.1

                self.sensor_history[m_id].append({
                    "air_temperature": air_temp,
                    "process_temperature": proc_temp,
                    "rotational_speed": speed,
                    "torque": torque,
                    "tool_wear": wear,
                    "timestamp": base_time.isoformat()
                })

        # 6. Parts Inventory (Used for prescriptive spare check)
        self.parts_inventory = [
            {"part_name": "Rotary Bearing B-10", "quantity": 14, "min_required": 5, "unit_cost": 120.00},
            {"part_name": "High-Temp Gasket G-5", "quantity": 28, "min_required": 10, "unit_cost": 15.50},
            {"part_name": "Pressure Valve V-12", "quantity": 4, "min_required": 3, "unit_cost": 245.00},
            {"part_name": "Hydraulic Pump Seal", "quantity": 3, "min_required": 5, "unit_cost": 45.00},
            {"part_name": "Cooling Fan F-8", "quantity": 19, "min_required": 8, "unit_cost": 35.00},
            {"part_name": "Control Board PCB-9", "quantity": 2, "min_required": 2, "unit_cost": 550.00}
        ]

        # 7. Work Orders
        self.work_orders = [
            {"id": 1, "machine_id": "M101", "status": "completed", "priority": "Medium", "action_required": "Calibrate sensor and tighten mounting bracket bolts.", "created_at": (datetime.now() - timedelta(days=15)).isoformat(), "completed_at": (datetime.now() - timedelta(days=15, hours=2)).isoformat()},
            {"id": 2, "machine_id": "M102", "status": "completed", "priority": "Low", "action_required": "Routine inspection and oil filter replacement.", "created_at": (datetime.now() - timedelta(days=10)).isoformat(), "completed_at": (datetime.now() - timedelta(days=10, hours=1)).isoformat()},
            {"id": 3, "machine_id": "M103", "status": "completed", "priority": "High", "action_required": "Resolved high heat error. Flushed main coolant lines.", "created_at": (datetime.now() - timedelta(days=4)).isoformat(), "completed_at": (datetime.now() - timedelta(days=4, hours=3)).isoformat()},
            {"id": 4, "machine_id": "M101", "status": "in_progress", "priority": "High", "action_required": "Emergency inspection of rotor bearings due to sudden spike in vibration.", "created_at": (datetime.now() - timedelta(hours=4)).isoformat(), "completed_at": None}
        ]

        # 8. Solr Incidents Index
        self.solr_incidents = [
            {"id": "inc-001", "machine_id": "M101", "failure_signature": "Vibration levels spike (bearing wear), high temperature near main drive spindle", "action_taken": "Replaced rotary bearing B-10 and adjusted rotor alignment", "outcome": "Resolved", "date": "2026-03-15T08:00:00Z"},
            {"id": "inc-002", "machine_id": "M103", "failure_signature": "Overheating shutdown triggered, core temperature reached 99.1°C", "action_taken": "Cleaned heat exchanger lines and replaced cooling fan F-8", "outcome": "Resolved", "date": "2026-04-01T14:30:00Z"},
            {"id": "inc-003", "machine_id": "M105", "failure_signature": "Pressure valve leak detected, line pressure fluctuated between 80-140 PSI", "action_taken": "Replaced pressure valve V-12 and high-temp gasket", "outcome": "Resolved", "date": "2026-04-18T11:15:00Z"}
        ]

db = MockDB()
