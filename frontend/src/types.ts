export interface MachinePrediction {
  machine_id: string;
  air_temperature: number;
  process_temperature: number;
  rotational_speed: number;
  torque: number;
  tool_wear: number;
  failure_probability: number;
  predicted_failure: string;
  recommendation: string;
}

export interface PredictionResponse {
  machine_id: string;
  air_temperature: number;
  process_temperature: number;
  rotational_speed: number;
  torque: number;
  tool_wear: number;
  failure_probability: number;
  predicted_failure: string;
  time_to_failure: string;
}

export interface RecommendationResponse {
  machine_id: string;
  recommendation: string;
  priority: string;
  confidence: number;
  created_at: string;
}

export interface WorkOrderResponse {
  id: number;
  machine_id: string;
  status: string;
  priority: string;
  action_required: string;
  created_at: string;
  completed_at: string | null;
}

export interface DashboardResponse {
  total_machines: number;
  healthy_machines: number;
  warning_machines: number;
  critical_machines: number;
  critical_alerts_count: number;
}
