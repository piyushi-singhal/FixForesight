import { API_URL } from './apiConfig';
import { PredictionResponse } from '../types';

export const getPredictions = async (): Promise<PredictionResponse[]> => {
  const response = await fetch(`${API_URL}/predictions`);
  if (!response.ok) throw new Error('Failed to load predictions');
  return response.json();
};
