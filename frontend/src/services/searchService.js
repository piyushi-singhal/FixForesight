import { API_URL } from './apiConfig';

export const searchIncidents = async (query) => {
  const response = await fetch(`${API_URL}/search?q=${encodeURIComponent(query)}`);
  if (!response.ok) throw new Error('Search request failed');
  return response.json();
};
