import { API_URL } from './apiConfig';
import { RecommendationResponse } from '../types';

export const getRecommendations = async (): Promise<RecommendationResponse[]> => {
  const response = await fetch(`${API_URL}/recommendations`);
  if (!response.ok) throw new Error('Failed to load recommendations');
  return response.json();
};

export const getMachineRecommendations = async (machineId: string): Promise<any> => {
  const response = await fetch(`${API_URL}/machines/${machineId}/recommendations`);
  if (!response.ok) throw new Error(`Failed to load recommendations for Machine-${machineId}`);
  return response.json();
};
