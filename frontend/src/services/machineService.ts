import { API_URL } from './apiConfig';
import { MachinePrediction } from '../types';

export const getMachines = async (): Promise<MachinePrediction[]> => {
  const response = await fetch(`${API_URL}/machines`);
  if (!response.ok) throw new Error('Failed to load machine overview');
  return response.json();
};

export const getMachineRisk = async (machineId: string): Promise<any> => {
  const response = await fetch(`${API_URL}/machines/${machineId}/risk`);
  if (!response.ok) throw new Error(`Failed to load telemetry for Machine-${machineId}`);
  return response.json();
};
