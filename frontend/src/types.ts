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
