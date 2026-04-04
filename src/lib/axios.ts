import axios from 'axios';
import { getApiBase } from './apiBase';

export const api = axios.create({
  baseURL: getApiBase(),
});

// Note: Token injection will be handled dynamically in components 
// using Stack Auth's useUser or useStackApp to retrieve the access token,
// or we can set it here if we store it globally.
api.interceptors.request.use((config) => {
  return config;
});
