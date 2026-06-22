import { API_URL } from './apiConfig';

export const getAlerts = async () => {
  const response = await fetch(`${API_URL}/alerts`);
  if (!response.ok) throw new Error('Failed to retrieve alerts');
  return response.json();
};
