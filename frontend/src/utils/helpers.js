export const getMachineName = (id) => {
  const names = {
    'M101': 'CNC Spindle Unit',
    'M102': 'Hydraulic Press',
    'M103': 'Injection Molder',
    'M104': 'Robotic Arm Axis 3',
    'M105': 'Cooling Compressor'
  };
  return names[id] || `Machine ${id}`;
};

export const getMachineStatus = (failureProbability) => {
  if (failureProbability >= 0.8) return 'Critical';
  if (failureProbability >= 0.3) return 'Warning';
  return 'Healthy';
};

export const getMachineModel = (id) => {
  const models = {
    'M101': 'M-450 Spindle',
    'M102': 'H-200 Press',
    'M103': 'IM-600 Molder',
    'M104': 'RA-3 Axis Controller',
    'M105': 'CC-800 Compressor'
  };
  return models[id] || 'N/A';
};

export const getMachineLocation = (id) => {
  const locations = {
    'M101': 'Aisle 3, Bay A',
    'M102': 'Aisle 1, Bay C',
    'M103': 'Aisle 2, Bay B',
    'M104': 'Assembly Line 4',
    'M105': 'Utility Plant Room'
  };
  return locations[id] || 'N/A';
};

export const getRiskClass = (prob) => {
  if (prob >= 70) return 'danger';
  if (prob >= 30) return 'warning';
  return 'healthy';
};

export const isPointAnomaly = (tab, val) => {
  if (tab === 'air_temperature' && val > 303.0) return true;
  if (tab === 'process_temperature' && val > 313.0) return true;
  if (tab === 'rotational_speed' && (val > 2200 || val < 1100)) return true;
  if (tab === 'torque' && val > 65.0) return true;
  if (tab === 'tool_wear' && val > 180.0) return true;
  if (tab === 'failure_probability' && val > 50.0) return true;
  return false;
};

// Sparkline Generator helper
export const getSvgPathData = (history, key) => {
  if (!history || history.length === 0) return { path: '', area: '', points: [] };
  
  const width = 500;
  const height = 200;
  const padding = 20;

  const values = history.map(h => h[key] || 0);
  const maxVal = Math.max(...values, 1) * 1.05;
  const minVal = Math.min(...values, 0) * 0.95;
  const valRange = maxVal - minVal || 1;

  const points = history.map((h, i) => {
    const x = padding + (i * (width - padding * 2)) / (history.length - 1);
    const val = h[key] || 0;
    const y = height - padding - ((val - minVal) * (height - padding * 2)) / valRange;
    return { x, y };
  });

  let path = `M ${points[0].x} ${points[0].y}`;
  for (let i = 1; i < points.length; i++) {
    path += ` L ${points[i].x} ${points[i].y}`;
  }

  const area = `${path} L ${points[points.length - 1].x} ${height - padding} L ${points[0].x} ${height - padding} Z`;
  return { path, area, points, minVal, maxVal };
};
