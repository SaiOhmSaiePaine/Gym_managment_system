import axios from 'axios';

// Configure API base URL based on deployment mode
const getApiBaseUrl = () => {
  // If running in admin mode (served from backend), use same origin
  if ((window as any).ADMIN_MODE || window.location.port === '8000') {
    return `${window.location.protocol}//${window.location.host}`;
  }
  
  // Default API URL for regular frontend
  return process.env.REACT_APP_API_URL || 'http://localhost:8000';
};

console.log('🔧 API Configuration:', {
  baseURL: getApiBaseUrl(),
  adminMode: (window as any).ADMIN_MODE,
  port: window.location.port
});

// Create axios instance
const api = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 30000, // 30 second timeout for all requests
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add a request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    // Get token from local storage (check both regular and admin tokens)
    const token = localStorage.getItem('token') || localStorage.getItem('adminToken');
    
    // If token exists, add it to headers
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;
