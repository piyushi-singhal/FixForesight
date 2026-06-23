import { API_URL } from './apiConfig';
import { WorkOrderResponse } from '../types';

export const createWorkOrder = async (machineId: string, priority: string, actionRequired: string, recommendationId?: number): Promise<any> => {
  const response = await fetch(`${API_URL}/work-orders`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      machine_id: machineId,
      priority: priority,
      action_required: actionRequired,
      recommendation_id: recommendationId
    })
  });
  if (!response.ok) throw new Error('Failed to generate work order');
  return response.json();
};

export const getWorkOrders = async (): Promise<WorkOrderResponse[]> => {
  const response = await fetch(`${API_URL}/work-orders`);
  if (!response.ok) throw new Error('Failed to load work orders');
  return response.json();
};
