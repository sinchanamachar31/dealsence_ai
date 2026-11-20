const configuredApiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const API_BASE_URL = configuredApiUrl.replace(/\/+$/, '');

export function apiUrl(path) {
  return `${API_BASE_URL}/${path.replace(/^\/+/, '')}`;
}
