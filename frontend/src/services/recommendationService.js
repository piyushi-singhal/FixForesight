import { API_URL } from './apiConfig';

export const getRecommendations = async () => {
  const response = await fetch(`${API_URL}/recommendations`);
  if (!response.ok) throw new Error('Failed to load recommendations');
  return response.json();
};

export const getMachineRecommendations = async (machineId) => {
  const response = await fetch(`${API_URL}/machines/${machineId}/recommendations`);
  if (!response.ok) throw new Error(`Failed to load recommendations for Machine-${machineId}`);
  return response.json();
};

export const createWorkOrder = async (machineId, priority, actionRequired) => {
  const response = await fetch(`${API_URL}/work-orders`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      machine_id: machineId,
      priority: priority,
      action_required: actionRequired
    })
  });
  if (!response.ok) throw new Error('Failed to generate work order');
  return response.json();
};

export const getWorkOrders = async () => {
  const response = await fetch(`${API_URL}/work-orders`);
  if (!response.ok) throw new Error('Failed to load work orders');
  return response.json();
};
