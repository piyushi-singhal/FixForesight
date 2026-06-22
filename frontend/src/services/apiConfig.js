// Resolve backend API URL dynamically based on current page origin/port
export const API_URL = window.location.port === '3000'
  ? `${window.location.protocol}//${window.location.hostname}:8000`
  : window.location.origin;
