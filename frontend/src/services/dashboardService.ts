import { API_URL } from './apiConfig';
import { DashboardResponse } from '../types';

export const getDashboardData = async (): Promise<DashboardResponse> => {
  const response = await fetch(`${API_URL}/dashboard`);
  if (!response.ok) throw new Error('Failed to load dashboard statistics');
  return response.json();
};
