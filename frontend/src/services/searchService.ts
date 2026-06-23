import { API_URL } from './apiConfig';

export interface SearchResponse {
  numFound: number;
  docs: Array<{
    id: string;
    machine_id: string;
    failure_signature: string;
    action_taken: string;
    outcome: string;
    date: string;
  }>;
}

export const searchIncidents = async (query: string): Promise<SearchResponse> => {
  const response = await fetch(`${API_URL}/search?q=${encodeURIComponent(query)}`);
  if (!response.ok) throw new Error('Search request failed');
  return response.json();
};
