import { API_URL } from './apiConfig';

export const getAnalytics = async () => {
  const response = await fetch(`${API_URL}/analytics`);
  if (!response.ok) throw new Error('Failed to retrieve analytics');
  return response.json();
};
