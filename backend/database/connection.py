from datetime import datetime, timedelta
import random

class MockDB:
    def __init__(self):
        # 1. Machines Directory
        self.machines = {
            "M101": {"machine_id": "M101", "machine_name": "CNC Spindle Unit", "status": "Warning", "temperature": 75.0, "pressure": 30.0, "vibration": 4.8, "rpm": 2500},
            "M102": {"machine_id": "M102", "machine_name": "Hydraulic Press", "status": "Healthy", "temperature": 48.5, "pressure": 120.0, "vibration": 0.8, "rpm": 1200},
            "M103": {"machine_id": "M103", "machine_name": "Injection Molder", "status": "Critical", "temperature": 99.1, "pressure": 85.0, "vibration": 2.1, "rpm": 1800},
            "M104": {"machine_id": "M104", "machine_name": "Robotic Arm Axis 3", "status": "Healthy", "temperature": 35.2, "pressure": 10.0, "vibration": 1.2, "rpm": 900},
            "M105": {"machine_id": "M105", "machine_name": "Cooling Compressor", "status": "Warning", "temperature": 62.4, "pressure": 145.0, "vibration": 3.4, "rpm": 3000}
        }

        # 2. Predictions (TensorFlow model output schema)
        self.predictions = {
            "M101": {"machine_id": "M101", "failure_probability": 82.0, "predicted_failure": "Bearing Failure", "time_to_failure": "5 Days"},
            "M102": {"machine_id": "M102", "failure_probability": 5.0, "predicted_failure": "Normal Operation", "time_to_failure": "N/A"},
            "M103": {"machine_id": "M103", "failure_probability": 94.0, "predicted_failure": "Thermal Overheating", "time_to_failure": "6 Hours"},
            "M104": {"machine_id": "M104", "failure_probability": 12.0, "predicted_failure": "Normal Operation", "time_to_failure": "N/A"},
            "M105": {"machine_id": "M105", "failure_probability": 52.0, "predicted_failure": "Pressure Valve Leak", "time_to_failure": "48 Hours"}
        }

        # 3. Recommendations (Recommendation engine output schema)
        self.recommendations = {
            "M101": {
                "machine_id": "M101",
                "recommendation": "Schedule bearing replacement immediately. Flush grease system and inspect rotor alignment.",
                "priority": "High",
                "confidence": 91.0,
                "required_parts": [{"part_name": "Rotary Bearing B-10", "quantity": 1}, {"part_name": "Hydraulic Pump Seal", "quantity": 2}],
                "estimated_duration_hours": 3.5,
                "created_at": (datetime.now() - timedelta(hours=1)).isoformat()
            },
            "M103": {
                "machine_id": "M103",
                "recommendation": "Perform emergency heat-exchanger cleanout. Replace secondary cooling fan unit and verify coolant pressure.",
                "priority": "Critical",
                "confidence": 96.0,
                "required_parts": [{"part_name": "Cooling Fan F-8", "quantity": 1}, {"part_name": "High-Temp Gasket G-5", "quantity": 1}],
                "estimated_duration_hours": 2.0,
                "created_at": (datetime.now() - timedelta(minutes=45)).isoformat()
            },
            "M105": {
                "machine_id": "M105",
                "recommendation": "Inspect pressure line seal. Replace primary pressure valve V-12 and calibrate limit sensors.",
                "priority": "Medium",
                "confidence": 78.0,
                "required_parts": [{"part_name": "Pressure Valve V-12", "quantity": 1}, {"part_name": "High-Temp Gasket G-5", "quantity": 2}],
                "estimated_duration_hours": 4.0,
                "created_at": (datetime.now() - timedelta(hours=2)).isoformat()
            }
        }

        # 4. Event Alerts (SNS mock alert feed)
        self.alerts = [
            {"alert_id": 1, "machine_id": "M101", "severity": "Critical", "message": "Bearing failure risk exceeds 80%", "created_at": (datetime.now() - timedelta(hours=4)).isoformat()},
            {"alert_id": 2, "machine_id": "M103", "severity": "Critical", "message": "Machine M103 temperature reached critical levels (99.1°C). Core shutdown initiated.", "created_at": (datetime.now() - timedelta(hours=2)).isoformat()},
            {"alert_id": 3, "machine_id": "M105", "severity": "Warning", "message": "Machine M105 line pressure fluctuated. Recalibration of sensor recommended.", "created_at": (datetime.now() - timedelta(minutes=30)).isoformat()}
        ]

        # 5. Historical Sensor Readings (Sparkline telemetry charts)
        self.sensor_history = {}
        for m_id in ["M101", "M102", "M103", "M104", "M105"]:
            self.sensor_history[m_id] = []
            for i in range(20, 0, -1):
                base_time = datetime.now() - timedelta(minutes=i*2)
                if m_id == "M101":
                    temp = 65.0 + (20 - i) * 0.4
                    vib = 3.0 + (20 - i) * 0.1
                    pres = 28.0 + (i % 3) * 0.2
                elif m_id == "M103":
                    temp = 80.0 + (20 - i) * 0.95
                    vib = 2.0 + (i % 2) * 0.05
                    pres = 80.0 - (20 - i) * 0.2
                elif m_id == "M105":
                    temp = 55.0 + (20 - i) * 0.35
                    vib = 2.0 + (i % 3) * 0.1
                    pres = 135.0 + (20 - i) * 0.5
                else:
                    temp = 45.0 + (i % 4) * 0.1
                    vib = 0.7 + (i % 3) * 0.05
                    pres = 115.0 + (i % 5) * 0.15

                self.sensor_history[m_id].append({
                    "temperature": temp,
                    "vibration": vib,
                    "pressure": pres,
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
            {"id": 1, "machine_id": "M101", "status": "completed", "priority": "Medium", "action_required": "Calibrate vibration sensor and tighten mounting bracket bolts.", "created_at": (datetime.now() - timedelta(days=15)).isoformat(), "completed_at": (datetime.now() - timedelta(days=15, hours=2)).isoformat()},
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
