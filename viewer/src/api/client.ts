import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_URL,
});

export const getAssetUrl = (path?: string) => {
  if (!path) return '';

  // Already an absolute URL
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }

  // Convert /storage/file.jpg
  // into http://localhost:8000/storage/file.jpg
  return `${API_URL}${path.startsWith('/') ? path : `/${path}`}`;
};

export const getCatalog = async () => {
  const res = await apiClient.get('/catalog');
  return res.data;
};

export const searchCatalog = async (params: {
  q?: string;
  category?: string;
  language?: string;
}) => {
  const res = await apiClient.get('/catalog/search', { params });
  return res.data;
};