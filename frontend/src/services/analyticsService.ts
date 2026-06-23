import { API_URL } from './apiConfig';

export interface AnalyticsResponse {
  healthy: number;
  warning: number;
  critical: number;
  healthy_machines: number;
  warning_machines: number;
  critical_machines: number;
  open_work_orders: number;
  completed_work_orders: number;
}

export const getAnalytics = async (): Promise<AnalyticsResponse> => {
  const response = await fetch(`${API_URL}/analytics`);
  if (!response.ok) throw new Error('Failed to retrieve analytics');
  return response.json();
};
