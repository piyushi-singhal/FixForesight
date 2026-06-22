import { API_URL } from './apiConfig';

export interface AlertResponse {
  alert_id: number;
  machine_id: string;
  severity: string;
  message: string;
  created_at: string;
}

export const getAlerts = async (): Promise<AlertResponse[]> => {
  const response = await fetch(`${API_URL}/alerts`);
  if (!response.ok) throw new Error('Failed to retrieve alerts');
  return response.json();
};
