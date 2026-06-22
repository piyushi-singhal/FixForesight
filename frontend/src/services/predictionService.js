import { API_URL } from './apiConfig';

export const getPredictions = async () => {
  const response = await fetch(`${API_URL}/predictions`);
  if (!response.ok) throw new Error('Failed to load predictions');
  return response.json();
};
