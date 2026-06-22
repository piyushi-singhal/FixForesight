"""
Industrial AI Platform - Maintenance Recommendation Engine
Generates maintenance recommendations and spare-part suggestions based on predictions
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json


class RiskLevel(Enum):
    """Risk levels for failure predictions."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MaintenanceType(Enum):
    """Types of maintenance actions."""

    PREVENTIVE = "preventive"
    URGENT = "urgent"
    REPLACEMENT = "replacement"
    INSPECTION = "inspection"


@dataclass
class SparePart:
    """Spare part recommendation."""

    part_name: str
    part_id: str
    quantity: int
    estimated_cost: float
    lead_time_days: int

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "part_name": self.part_name,
            "part_id": self.part_id,
            "quantity": self.quantity,
            "estimated_cost": self.estimated_cost,
            "lead_time_days": self.lead_time_days,
        }


@dataclass
class Recommendation:
    """Maintenance recommendation."""

    machine_id: int
    prediction_id: int
    recommendation_type: str
    action: str
    priority: str
    estimated_cost: float
    spare_parts: List[SparePart]
    days_to_failure: int = None
    failure_probability: float = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "machine_id": self.machine_id,
            "prediction_id": self.prediction_id,
            "recommendation_type": self.recommendation_type,
            "action": self.action,
            "priority": self.priority,
            "estimated_cost": self.estimated_cost,
            "spare_parts": [sp.to_dict() for sp in self.spare_parts],
            "days_to_failure": self.days_to_failure,
            "failure_probability": self.failure_probability,
        }


class RecommendationEngine:
    """Generate maintenance recommendations based on failure predictions."""

    # Spare parts catalog
    SPARE_PARTS_CATALOG = {
        "heat_dissipation": [
            SparePart(
                part_name="Cooling Fan Assembly",
                part_id="FAN-001",
                quantity=1,
                estimated_cost=450,
                lead_time_days=3,
            ),
            SparePart(
                part_name="Thermal Grease (500ml)",
                part_id="THG-500",
                quantity=2,
                estimated_cost=80,
                lead_time_days=1,
            ),
        ],
        "power_loss": [
            SparePart(
                part_name="Motor Drive Belt",
                part_id="BLT-250",
                quantity=1,
                estimated_cost=320,
                lead_time_days=5,
            ),
            SparePart(
                part_name="Power Transmission Coupling",
                part_id="CUP-100",
                quantity=1,
                estimated_cost=280,
                lead_time_days=7,
            ),
        ],
        "overstrain": [
            SparePart(
                part_name="Bearing Assembly",
                part_id="BRG-050",
                quantity=2,
                estimated_cost=350,
                lead_time_days=4,
            ),
            SparePart(
                part_name="Structural Support Bracket",
                part_id="BRK-200",
                quantity=1,
                estimated_cost=150,
                lead_time_days=2,
            ),
        ],
        "tool_wear": [
            SparePart(
                part_name="Cutting Tool Insert (Premium)",
                part_id="TOOL-P100",
                quantity=10,
                estimated_cost=600,
                lead_time_days=2,
            ),
            SparePart(
                part_name="Tool Holder Collet",
                part_id="COLL-50",
                quantity=2,
                estimated_cost=200,
                lead_time_days=3,
            ),
        ],
        "random_failure": [
            SparePart(
                part_name="Control Module PCB",
                part_id="PCB-001",
                quantity=1,
                estimated_cost=800,
                lead_time_days=10,
            ),
            SparePart(
                part_name="Sensor Replacement Kit",
                part_id="SENSOR-KIT",
                quantity=1,
                estimated_cost=400,
                lead_time_days=5,
            ),
        ],
    }

    # Maintenance action templates
    MAINTENANCE_ACTIONS = {
        "heat_dissipation": {
            "low": [
                "Schedule routine cooling system inspection within 2 weeks",
                "Clean cooling ducts and check airflow",
            ],
            "medium": [
                "Perform preventive cooling fan maintenance within 1 week",
                "Check and apply thermal compound to critical heat sources",
                "Verify cooling system is functioning at optimal capacity",
            ],
            "high": [
                "URGENT: Replace cooling fan within 24 hours",
                "Inspect heat sinks for damage",
                "Clean internal components to improve heat dissipation",
                "Monitor temperature continuously",
            ],
            "critical": [
                "CRITICAL: Stop machine immediately if temperature exceeds 85°C",
                "Replace cooling system components immediately",
                "Perform full thermal imaging inspection",
                "Do not resume operation until cooling restored",
            ],
        },
        "power_loss": {
            "low": [
                "Monitor power transmission system weekly",
                "Check belt tension during regular maintenance",
            ],
            "medium": [
                "Inspect drive belt for wear or damage within 1 week",
                "Test motor output and power transmission coupling",
                "Lubricate transmission system",
            ],
            "high": [
                "URGENT: Replace drive belt within 24 hours",
                "Check motor brushes and commutator",
                "Inspect power coupling alignment",
                "Run power loss diagnostics",
            ],
            "critical": [
                "CRITICAL: Reduce machine speed by 50% immediately",
                "Prepare for emergency component replacement",
                "Establish 24/7 monitoring of power metrics",
                "Consider machine shutdown if power loss continues",
            ],
        },
        "overstrain": {
            "low": [
                "Verify load parameters are within specifications",
                "Review production schedule for optimization",
            ],
            "medium": [
                "Inspect bearings for wear within 1 week",
                "Reduce applied loads by 10-15% during operation",
                "Check structural integrity of mounting points",
            ],
            "high": [
                "URGENT: Replace worn bearings within 24 hours",
                "Reduce machine loads by 20-30%",
                "Inspect all structural components for stress cracks",
                "Run vibration analysis",
            ],
            "critical": [
                "CRITICAL: Stop machine immediately",
                "Reduce operating loads to 50% or less",
                "Plan for major overhaul or replacement",
                "Continuous monitoring required",
            ],
        },
        "tool_wear": {
            "low": ["Monitor tool wear rates", "Schedule routine tool inspection"],
            "medium": [
                "Replace cutting tool within 1 week",
                "Inspect tool holder for damage",
                "Adjust cutting parameters to reduce wear",
            ],
            "high": [
                "URGENT: Replace tool immediately (within 12 hours)",
                "Check spindle accuracy",
                "Inspect work surface quality",
            ],
            "critical": [
                "CRITICAL: Stop machine and replace tool NOW",
                "Inspect all components for secondary damage",
                "Verify product quality before resuming",
            ],
        },
    }

    def __init__(self):
        """Initialize the recommendation engine."""
        pass

    def assess_risk_level(self, failure_probability: float, days_to_failure: int = None) -> str:
        """
        Assess risk level based on failure probability and time horizon.

        Args:
            failure_probability: Probability of failure (0-1)
            days_to_failure: Estimated days until failure

        Returns:
            Risk level string
        """
        if failure_probability > 0.8 or (days_to_failure and days_to_failure < 1):
            return RiskLevel.CRITICAL.value
        elif failure_probability > 0.6 or (days_to_failure and days_to_failure < 3):
            return RiskLevel.HIGH.value
        elif failure_probability > 0.4 or (days_to_failure and days_to_failure < 7):
            return RiskLevel.MEDIUM.value
        else:
            return RiskLevel.LOW.value

    def get_spare_parts(self, failure_type: str, risk_level: str) -> List[SparePart]:
        """Get recommended spare parts for failure type."""
        parts = self.SPARE_PARTS_CATALOG.get(failure_type, [])

        # Add extra parts for high-risk scenarios
        if risk_level in [RiskLevel.HIGH.value, RiskLevel.CRITICAL.value]:
            # Increase quantities
            parts = [
                SparePart(
                    part_name=p.part_name,
                    part_id=p.part_id,
                    quantity=p.quantity * 2,
                    estimated_cost=p.estimated_cost * 2,
                    lead_time_days=1,
                )
                for p in parts
            ]

        return parts

    def get_maintenance_actions(self, failure_type: str, risk_level: str) -> List[str]:
        """Get maintenance actions for failure type and risk level."""
        actions_template = self.MAINTENANCE_ACTIONS.get(failure_type, {})
        actions = actions_template.get(risk_level, ["Consult maintenance specialist"])
        return actions

    def estimate_cost(self, spare_parts: List[SparePart], labor_hours: float = 4) -> float:
        """Estimate total maintenance cost."""
        parts_cost = sum(p.estimated_cost for p in spare_parts)
        labor_cost = labor_hours * 100  # $100 per hour
        return parts_cost + labor_cost

    def generate_recommendation(
        self,
        machine_id: int,
        prediction_id: int,
        failure_type: str,
        failure_probability: float,
        days_to_failure: int = None,
    ) -> Recommendation:
        """
        Generate comprehensive maintenance recommendation.

        Args:
            machine_id: ID of the machine
            prediction_id: ID of the prediction
            failure_type: Type of predicted failure
            failure_probability: Probability of failure (0-1)
            days_to_failure: Estimated days until failure

        Returns:
            Recommendation object
        """
        # Assess risk
        risk_level = self.assess_risk_level(failure_probability, days_to_failure)

        # Determine maintenance type
        if risk_level == RiskLevel.CRITICAL.value:
            maintenance_type = MaintenanceType.REPLACEMENT.value
        elif risk_level == RiskLevel.HIGH.value:
            maintenance_type = MaintenanceType.URGENT.value
        else:
            maintenance_type = MaintenanceType.PREVENTIVE.value

        # Get spare parts
        spare_parts = self.get_spare_parts(failure_type, risk_level)

        # Get actions
        actions = self.get_maintenance_actions(failure_type, risk_level)
        action_text = "\n".join([f"• {action}" for action in actions])

        # Estimate cost
        estimated_cost = self.estimate_cost(spare_parts)

        # Create recommendation
        recommendation = Recommendation(
            machine_id=machine_id,
            prediction_id=prediction_id,
            recommendation_type=maintenance_type,
            action=action_text,
            priority=risk_level,
            estimated_cost=estimated_cost,
            spare_parts=spare_parts,
            days_to_failure=days_to_failure,
            failure_probability=failure_probability,
        )

        return recommendation

    def generate_batch_recommendations(
        self, predictions_df: pd.DataFrame
    ) -> List[Dict]:
        """
        Generate recommendations for multiple predictions.

        Args:
            predictions_df: DataFrame with columns:
                - machine_id
                - prediction_id
                - failure_type
                - failure_probability
                - days_to_failure (optional)

        Returns:
            List of recommendation dictionaries
        """
        recommendations = []

        for _, row in predictions_df.iterrows():
            rec = self.generate_recommendation(
                machine_id=row["machine_id"],
                prediction_id=row["prediction_id"],
                failure_type=row.get("failure_type", "random_failure"),
                failure_probability=row["failure_probability"],
                days_to_failure=row.get("days_to_failure"),
            )
            recommendations.append(rec.to_dict())

        return recommendations


class MaintenanceScheduler:
    """Schedule maintenance activities based on recommendations."""

    @staticmethod
    def schedule_maintenance(
        recommendations: List[Dict], current_time: datetime = None
    ) -> List[Dict]:
        """
        Schedule recommended maintenance activities.

        Args:
            recommendations: List of recommendation dicts
            current_time: Current datetime (default: now)

        Returns:
            List of scheduled maintenance tasks
        """
        if current_time is None:
            current_time = datetime.now()

        scheduled_tasks = []

        for rec in recommendations:
            # Determine scheduling window based on priority
            priority = rec["priority"]
            if priority == "critical":
                days_until = 0
                urgency = "IMMEDIATE"
            elif priority == "high":
                days_until = 1
                urgency = "ASAP"
            elif priority == "medium":
                days_until = 3
                urgency = "WITHIN 1 WEEK"
            else:
                days_until = 7
                urgency = "ROUTINE"

            scheduled_date = current_time + timedelta(days=days_until)

            task = {
                "task_id": f"TASK-{rec['machine_id']}-{int(current_time.timestamp())}",
                "machine_id": rec["machine_id"],
                "maintenance_type": rec["recommendation_type"],
                "priority": rec["priority"],
                "urgency": urgency,
                "scheduled_date": scheduled_date.isoformat(),
                "actions": rec["action"],
                "spare_parts": rec["spare_parts"],
                "estimated_cost": rec["estimated_cost"],
                "estimated_duration_hours": 4,
                "required_technician_skill": "advanced" if priority in ["critical", "high"] else "standard",
            }

            scheduled_tasks.append(task)

        return scheduled_tasks


def main():
    """Demo: Generate recommendations for sample predictions."""
    print("=" * 80)
    print("Industrial AI Platform - Maintenance Recommendation Engine")
    print("=" * 80)

    # Sample predictions
    predictions = [
        {
            "machine_id": 1,
            "prediction_id": 101,
            "failure_type": "heat_dissipation",
            "failure_probability": 0.85,
            "days_to_failure": 2,
        },
        {
            "machine_id": 2,
            "prediction_id": 102,
            "failure_type": "tool_wear",
            "failure_probability": 0.65,
            "days_to_failure": 5,
        },
        {
            "machine_id": 3,
            "prediction_id": 103,
            "failure_type": "overstrain",
            "failure_probability": 0.45,
            "days_to_failure": 10,
        },
        {
            "machine_id": 4,
            "prediction_id": 104,
            "failure_type": "power_loss",
            "failure_probability": 0.25,
            "days_to_failure": 20,
        },
    ]

    df_predictions = pd.DataFrame(predictions)

    # Generate recommendations
    engine = RecommendationEngine()
    recommendations = engine.generate_batch_recommendations(df_predictions)

    # Schedule maintenance
    scheduler = MaintenanceScheduler()
    scheduled_tasks = scheduler.schedule_maintenance(recommendations)

    # Print results
    print("\n" + "=" * 80)
    print("GENERATED RECOMMENDATIONS")
    print("=" * 80)

    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. Machine {rec['machine_id']} (Prediction ID: {rec['prediction_id']})")
        print(f"   Type: {rec['recommendation_type'].upper()}")
        print(f"   Priority: {rec['priority'].upper()}")
        print(f"   Failure Probability: {rec['failure_probability']:.2%}")
        print(f"   Estimated Cost: ${rec['estimated_cost']:.2f}")
        print(f"   \n   Actions:")
        print(f"   {rec['action']}")
        print(f"   \n   Spare Parts:")
        for part in rec["spare_parts"]:
            print(f"     • {part['part_name']} (x{part['quantity']}) - ${part['estimated_cost']}")

    print("\n" + "=" * 80)
    print("SCHEDULED MAINTENANCE TASKS")
    print("=" * 80)

    for task in scheduled_tasks:
        print(f"\nTask: {task['task_id']}")
        print(f"  Machine: {task['machine_id']}")
        print(f"  Scheduled: {task['scheduled_date']}")
        print(f"  Urgency: {task['urgency']}")
        print(f"  Estimated Cost: ${task['estimated_cost']:.2f}")
        print(f"  Technician Level: {task['required_technician_skill'].upper()}")

    # Save to JSON
    output_data = {
        "recommendations": recommendations,
        "scheduled_tasks": scheduled_tasks,
        "generated_at": datetime.now().isoformat(),
        "total_estimated_cost": sum(t["estimated_cost"] for t in scheduled_tasks),
    }

    with open("data/recommendations_output.json", "w") as f:
        json.dump(output_data, f, indent=2, default=str)

    print("\n" + "=" * 80)
    print(f"Recommendations saved to: data/recommendations_output.json")
    print(f"Total Estimated Cost: ${output_data['total_estimated_cost']:.2f}")
    print("=" * 80)


if __name__ == "__main__":
    main()
