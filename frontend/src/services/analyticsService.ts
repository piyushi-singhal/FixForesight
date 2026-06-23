import { API_URL } from './apiConfig';

export interface AnalyticsResponse {
  healthy: number;
  warning: number;
  critical: number;
}

export const getAnalytics = async (): Promise<AnalyticsResponse> => {
  const response = await fetch(`${API_URL}/analytics`);
  if (!response.ok) throw new Error('Failed to retrieve analytics');
  return response.json();
};
