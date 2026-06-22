import http.server
import json
import urllib.parse
import os
from datetime import datetime, timedelta
import random

PORT = 8000

# In-Memory Database Store simulating relational database tables
class MockDB:
    def __init__(self):
        # 1. Parts Inventory
        self.parts_inventory = [
            {"part_name": "Rotary Bearing B-10", "quantity": 14, "min_required": 5, "unit_cost": 120.00},
            {"part_name": "High-Temp Gasket G-5", "quantity": 28, "min_required": 10, "unit_cost": 15.50},
            {"part_name": "Pressure Valve V-12", "quantity": 4, "min_required": 3, "unit_cost": 245.00},
            {"part_name": "Hydraulic Pump Seal", "quantity": 3, "min_required": 5, "unit_cost": 45.00},
            {"part_name": "Cooling Fan F-8", "quantity": 19, "min_required": 8, "unit_cost": 35.00},
            {"part_name": "Control Board PCB-9", "quantity": 2, "min_required": 2, "unit_cost": 550.00}
        ]

        # 2. Predictions
        self.predictions = {
            1: {"machine_id": 1, "failure_probability": 0.88, "predicted_failure_type": "Bearing Failure", "time_to_failure_hours": 18, "timestamp": datetime.now().isoformat()},
            2: {"machine_id": 2, "failure_probability": 0.05, "predicted_failure_type": "Normal Operation", "time_to_failure_hours": None, "timestamp": datetime.now().isoformat()},
            3: {"machine_id": 3, "failure_probability": 0.94, "predicted_failure_type": "Overheating", "time_to_failure_hours": 6, "timestamp": datetime.now().isoformat()},
            4: {"machine_id": 4, "failure_probability": 0.52, "predicted_failure_type": "Pressure Valve Leak", "time_to_failure_hours": 48, "timestamp": datetime.now().isoformat()},
            5: {"machine_id": 5, "failure_probability": 0.12, "predicted_failure_type": "Slight Mechanical Wear", "time_to_failure_hours": 144, "timestamp": datetime.now().isoformat()}
        }

        # 3. Recommendations
        self.recommendations = {
            1: {
                "id": 101,
                "machine_id": 1,
                "recommended_action": "Schedule bearing replacement immediately. Flush grease system and inspect rotor alignment.",
                "required_parts": [{"part_name": "Rotary Bearing B-10", "quantity": 1}, {"part_name": "Hydraulic Pump Seal", "quantity": 2}],
                "maintenance_priority": "high",
                "estimated_duration_hours": 3.5,
                "created_at": (datetime.now() - timedelta(hours=1)).isoformat()
            },
            3: {
                "id": 103,
                "machine_id": 3,
                "recommended_action": "Perform emergency heat-exchanger cleanout. Replace secondary cooling fan unit and verify coolant pressure.",
                "required_parts": [{"part_name": "Cooling Fan F-8", "quantity": 1}, {"part_name": "High-Temp Gasket G-5", "quantity": 1}],
                "maintenance_priority": "critical",
                "estimated_duration_hours": 2.0,
                "created_at": (datetime.now() - timedelta(minutes=45)).isoformat()
            },
            4: {
                "id": 104,
                "machine_id": 4,
                "recommended_action": "Inspect pressure line seal. Replace primary pressure valve V-12 and calibrate limit sensors.",
                "required_parts": [{"part_name": "Pressure Valve V-12", "quantity": 1}, {"part_name": "High-Temp Gasket G-5", "quantity": 2}],
                "maintenance_priority": "medium",
                "estimated_duration_hours": 4.0,
                "created_at": (datetime.now() - timedelta(hours=2)).isoformat()
            },
            5: {
                "id": 105,
                "machine_id": 5,
                "recommended_action": "Perform general maintenance at next scheduled downtime. Lubricate linkages and adjust belt tension.",
                "required_parts": [],
                "maintenance_priority": "low",
                "estimated_duration_hours": 1.5,
                "created_at": (datetime.now() - timedelta(hours=4)).isoformat()
            }
        }

        # 4. Work Orders
        self.work_orders = [
            {"id": 1, "machine_id": 1, "status": "completed", "priority": "medium", "action_required": "Calibrate vibration sensor and tighten mounting bracket bolts.", "created_at": (datetime.now() - timedelta(days=15)).isoformat(), "completed_at": (datetime.now() - timedelta(days=15, hours=2)).isoformat()},
            {"id": 2, "machine_id": 2, "status": "completed", "priority": "low", "action_required": "Routine inspection and oil filter replacement.", "created_at": (datetime.now() - timedelta(days=10)).isoformat(), "completed_at": (datetime.now() - timedelta(days=10, hours=1)).isoformat()},
            {"id": 3, "machine_id": 3, "status": "completed", "priority": "high", "action_required": "Resolved high heat error. Flushed main coolant lines.", "created_at": (datetime.now() - timedelta(days=4)).isoformat(), "completed_at": (datetime.now() - timedelta(days=4, hours=3)).isoformat()},
            {"id": 4, "machine_id": 1, "status": "in_progress", "priority": "high", "action_required": "Emergency inspection of rotor bearings due to sudden spike in vibration.", "created_at": (datetime.now() - timedelta(hours=4)).isoformat(), "completed_at": None},
            {"id": 5, "machine_id": 3, "status": "open", "priority": "critical", "action_required": "Perform emergency heat-exchanger cleanout and fan replacement.", "created_at": (datetime.now() - timedelta(hours=1)).isoformat(), "completed_at": None}
        ]

        # 5. Sensor History
        self.sensor_history = {}
        for m in range(1, 6):
            self.sensor_history[m] = []
            for i in range(20, 0, -1):
                base_time = datetime.now() - timedelta(minutes=i*2)
                if m == 1:
                    temp = 65.0 + (20 - i) * 0.4
                    vib = 3.0 + (20 - i) * 0.3
                    pres = 120.0 + (i % 3) * 0.2
                    err = "W-VIB-01" if i < 5 else None
                elif m == 3:
                    temp = 80.0 + (20 - i) * 0.95
                    vib = 2.0 + (i % 2) * 0.05
                    pres = 100.0 - (20 - i) * 0.2
                    err = "E-TEMP-CRIT" if i < 4 else "W-TEMP-HIGH" if i < 10 else None
                elif m == 4:
                    temp = 60.0 + (i % 2) * 0.2
                    vib = 2.0 + (i % 3) * 0.1
                    pres = 125.0 + (20 - i) * 0.7
                    err = "W-PRES-HIGH" if i < 6 else None
                else:
                    temp = 55.0 + (i % 4) * 0.1
                    vib = 1.2 + (i % 3) * 0.05
                    pres = 115.0 + (i % 5) * 0.15
                    err = None

                self.sensor_history[m].append({
                    "temperature": temp,
                    "vibration": vib,
                    "pressure": pres,
                    "error_code": err,
                    "timestamp": base_time.isoformat()
                })

        # 6. Alerts
        self.alerts = [
            {"id": 1, "message_id": "msg-923847", "subject": "CRITICAL Failure Warning: Machine 3", "message": "Machine 3 is exhibiting critical temperature levels (99.1°C). Core shutdown initiated. Scheduled emergency action required.", "received_at": (datetime.now() - timedelta(hours=2)).isoformat()},
            {"id": 2, "message_id": "msg-923848", "subject": "HIGH Risk Alert: Machine 1", "message": "Machine 1 vibration velocity exceeded safe envelope (8.9 mm/s). High probability of bearing failure. Maintenance order created.", "received_at": (datetime.now() - timedelta(hours=4)).isoformat()}
        ]

        # 7. Solr incidents
        self.solr_incidents = [
            {"id": "inc-001", "machine_id": 1, "failure_signature": "Vibration levels spike (bearing wear), high temperature near main drive spindle", "action_taken": "Replaced rotary bearing B-10 and adjusted rotor alignment", "outcome": "Resolved", "date": "2026-03-15T08:00:00Z"},
            {"id": "inc-002", "machine_id": 3, "failure_signature": "Overheating shutdown triggered, core temperature reached 99.1°C", "action_taken": "Cleaned heat exchanger lines and replaced cooling fan F-8", "outcome": "Resolved", "date": "2026-04-01T14:30:00Z"},
            {"id": "inc-003", "machine_id": 4, "failure_signature": "Pressure valve leak detected, line pressure fluctuated between 80-140 PSI", "action_taken": "Replaced pressure valve V-12 and high-temp gasket", "outcome": "Resolved", "date": "2026-04-18T11:15:00Z"},
            {"id": "inc-004", "machine_id": 1, "failure_signature": "Rotor locking and screeching noise, motor pulling double current", "action_taken": "Complete bearing rebuild, replaced hydraulic pump seal", "outcome": "Resolved", "date": "2026-05-02T19:00:00Z"},
            {"id": "inc-005", "machine_id": 5, "failure_signature": "Minor vibrations, belt slippage detected", "action_taken": "Tightened drive belt, greased secondary drive gear linkages", "outcome": "Resolved", "date": "2026-05-20T10:00:00Z"},
            {"id": "inc-006", "machine_id": 3, "failure_signature": "Thermal overload sensor tripped due to radiator blockage", "action_taken": "Cleared intake vents, ran flush cycle on radiators", "outcome": "Resolved", "date": "2026-06-01T09:45:00Z"}
        ]

db = MockDB()

class RouterHandler(http.server.BaseHTTPRequestHandler):
    def end_headers(self):
        # Universal CORS Header configuration
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        # 1. Serve React Frontend dashboard at "/"
        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            
            # Read index.html from workspace
            index_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "index.html")
            if os.path.exists(index_path):
                with open(index_path, "r", encoding="utf-8") as f:
                    self.wfile.write(f.read().encode("utf-8"))
            else:
                self.wfile.write(b"<h1>FixForesight Front-end File Not Found. Ensure frontend/public/index.html is created.</h1>")
            return

        # 2. Endpoint: GET /health
        elif path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            resp = {
                "status": "healthy (In-Memory Fallback)",
                "postgres": "simulated",
                "localstack": "simulated",
                "solr": "simulated",
                "note": "API is running without container dependencies."
            }
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        # 3. Endpoint: GET /machines
        elif path == "/machines":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            machines_summary = []
            for i in range(1, 6):
                pred = db.predictions.get(i, {"failure_probability": 0.05, "predicted_failure_type": "Normal Operation", "time_to_failure_hours": None})
                history = db.sensor_history.get(i, [])
                
                # Fluctuate readings dynamically to simulate stream
                last_sensor = history[-1] if history else {"temperature": 50.0, "vibration": 1.0, "pressure": 100.0, "error_code": None}
                temp_fluc = last_sensor["temperature"] + random.uniform(-0.4, 0.4)
                vib_fluc = last_sensor["vibration"] + random.uniform(-0.08, 0.08)
                pres_fluc = last_sensor["pressure"] + random.uniform(-0.5, 0.5)

                last_sensor["temperature"] = max(30.0, min(140.0, temp_fluc))
                last_sensor["vibration"] = max(0.1, min(25.0, vib_fluc))
                last_sensor["pressure"] = max(50.0, min(250.0, pres_fluc))

                open_orders = sum(1 for w in db.work_orders if w["machine_id"] == i and w["status"] in ["open", "in_progress"])

                machines_summary.append({
                    "id": i,
                    "name": f"Machine-{i:03d}",
                    "failure_probability": pred["failure_probability"],
                    "predicted_failure_type": pred["predicted_failure_type"],
                    "time_to_failure_hours": pred["time_to_failure_hours"],
                    "temperature": last_sensor["temperature"],
                    "vibration": last_sensor["vibration"],
                    "pressure": last_sensor["pressure"],
                    "active_error": last_sensor["error_code"],
                    "open_work_orders": open_orders
                })
            self.wfile.write(json.dumps(machines_summary).encode("utf-8"))
            return

        # 4. Endpoint: GET /machines/{id}/risk
        elif path.startswith("/machines/") and path.endswith("/risk"):
            try:
                parts = path.split("/")
                m_id = int(parts[2])
            except ValueError:
                self.send_response(400)
                self.end_headers()
                return

            if m_id < 1 or m_id > 5:
                self.send_response(404)
                self.end_headers()
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            pred = db.predictions.get(m_id, {
                "failure_probability": 0.05,
                "predicted_failure_type": "Normal Operation",
                "time_to_failure_hours": None,
                "timestamp": datetime.now().isoformat()
            })
            history = db.sensor_history.get(m_id, [])

            # Keep length capped at 20
            if len(history) > 20:
                history = history[-20:]

            resp = {
                "machine_id": m_id,
                "prediction": pred,
                "sensor_history": history
            }
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        # 5. Endpoint: GET /machines/{id}/recommendations
        elif path.startswith("/machines/") and path.endswith("/recommendations"):
            try:
                parts = path.split("/")
                m_id = int(parts[2])
            except ValueError:
                self.send_response(400)
                self.end_headers()
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            rec = db.recommendations.get(m_id)
            if not rec:
                self.wfile.write(json.dumps({
                    "machine_id": m_id,
                    "has_recommendation": False,
                    "message": "No active recommendations. Machine operation normal."
                }).encode("utf-8"))
                return

            inventory_map = {item["part_name"]: item for item in db.parts_inventory}
            parts_list = []
            out_of_stock = False

            for part in rec["required_parts"]:
                name = part["part_name"]
                req_qty = part["quantity"]
                inv = inventory_map.get(name)

                if not inv:
                    parts_list.append({
                        "part_name": name,
                        "quantity_required": req_qty,
                        "stock_available": 0,
                        "status": "unavailable",
                        "unit_cost": 0.0
                    })
                    out_of_stock = True
                else:
                    avail = inv["quantity"]
                    min_req = inv["min_required"]
                    cost = inv["unit_cost"]
                    
                    if avail >= req_qty:
                        status = "instock" if avail >= min_req else "lowstock"
                    else:
                        status = "outofstock"
                        out_of_stock = True

                    parts_list.append({
                        "part_name": name,
                        "quantity_required": req_qty,
                        "stock_available": avail,
                        "status": status,
                        "unit_cost": cost
                    })

            resp = {
                "machine_id": m_id,
                "has_recommendation": True,
                "recommendation_id": rec["id"],
                "recommended_action": rec["recommended_action"],
                "priority": rec["maintenance_priority"],
                "estimated_duration_hours": rec["estimated_duration_hours"],
                "parts_status": parts_list,
                "parts_missing": out_of_stock,
                "created_at": rec["created_at"]
            }
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        # 6. Endpoint: GET /alerts
        elif path == "/alerts":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            # Sort newest first
            sorted_alerts = sorted(db.alerts, key=lambda x: x["received_at"], reverse=True)
            self.wfile.write(json.dumps(sorted_alerts).encode("utf-8"))
            return

        # 7. Endpoint: GET /incidents/search
        elif path == "/incidents/search":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            q = query.get("q", ["*:*"])[0]
            query_clean = q.lower().strip()
            
            results = []
            if query_clean == "*:*" or not query_clean:
                results = db.solr_incidents
            else:
                for doc in db.solr_incidents:
                    text_pool = f"{doc.get('failure_signature', '')} {doc.get('action_taken', '')} {doc.get('outcome', '')} machine-{doc.get('machine_id', '')}".lower()
                    if query_clean in text_pool:
                        results.append(doc)
            
            resp = {
                "numFound": len(results),
                "docs": results
            }
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        else:
            self.send_response(404)
            self.end_headers()
            return

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        # Read JSON body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        try:
            payload = json.loads(body) if body else {}
        except Exception:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid JSON")
            return

        # 1. Endpoint: POST /alerts/webhook (SNS endpoint)
        if path == "/alerts/webhook":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            # Inspect headers or payload for SNS Type
            msg_type = self.headers.get("x-amz-sns-message-type") or payload.get("Type")
            
            if msg_type == "SubscriptionConfirmation":
                subscribe_url = payload.get("SubscribeURL")
                print(f"SNS Subscription Confirmation URL: {subscribe_url}")
                self.wfile.write(json.dumps({"status": "subscription_confirmed"}).encode("utf-8"))
                return
            
            else:
                # Store message
                subject = payload.get("Subject", "Alert")
                message = payload.get("Message", body)
                new_alert = {
                    "id": len(db.alerts) + 1,
                    "message_id": payload.get("MessageId", "raw-post"),
                    "subject": subject,
                    "message": message,
                    "received_at": datetime.now().isoformat()
                }
                db.alerts.append(new_alert)
                self.wfile.write(json.dumps({"status": "alert_saved_mock"}).encode("utf-8"))
                return

        # 2. Endpoint: POST /work-orders
        elif path == "/work-orders":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            m_id = payload.get("machine_id")
            priority = payload.get("priority")
            action = payload.get("action_required")

            new_id = len(db.work_orders) + 1
            new_wo = {
                "id": new_id,
                "machine_id": m_id,
                "status": "open",
                "priority": priority,
                "action_required": action,
                "created_at": datetime.now().isoformat(),
                "completed_at": None
            }
            db.work_orders.append(new_wo)

            # Deduct inventory items requested by the recommendation
            rec = db.recommendations.get(m_id)
            if rec:
                for part in rec["required_parts"]:
                    name = part["part_name"]
                    qty = part["quantity"]
                    for inv_item in db.parts_inventory:
                        if inv_item["part_name"] == name:
                            inv_item["quantity"] = max(0, inv_item["quantity"] - qty)

                # Reset failure state since mitigation order is active
                db.predictions[m_id]["failure_probability"] = 0.05
                db.predictions[m_id]["predicted_failure_type"] = "Normal Operation"
                db.predictions[m_id]["time_to_failure_hours"] = None
                db.recommendations.pop(m_id, None)

            self.wfile.write(json.dumps({"status": "created", "work_order_id": new_id}).encode("utf-8"))
            return

        else:
            self.send_response(404)
            self.end_headers()
            return

    def do_PUT(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        # Read JSON body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        try:
            payload = json.loads(body) if body else {}
        except Exception:
            self.send_response(400)
            self.end_headers()
            return

        # 1. Endpoint: PUT /work-orders/{id}
        if path.startswith("/work-orders/"):
            try:
                parts = path.split("/")
                wo_id = int(parts[2])
            except ValueError:
                self.send_response(400)
                self.end_headers()
                return

            status = payload.get("status")
            found = False
            for wo in db.work_orders:
                if wo["id"] == wo_id:
                    wo["status"] = status
                    if status == "completed":
                        wo["completed_at"] = datetime.now().isoformat()
                    found = True
                    break

            if found:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "updated"}).encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()
            return
        else:
            self.send_response(404)
            self.end_headers()
            return

def run_server():
    server_address = ('', PORT)
    httpd = http.server.HTTPServer(server_address, RouterHandler)
    print(f"=========================================================")
    print(f" FixForesight Zero-Dependency Server is running on port {PORT}")
    print(f" Dashboard is live at: http://localhost:{PORT}")
    print(f" Press Ctrl+C to terminate.")
    print(f"=========================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
