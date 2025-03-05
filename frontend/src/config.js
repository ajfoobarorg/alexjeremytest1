const isDevelopment = import.meta.env.DEV;

// In development, use localhost:8000
// In production, use the VITE_BACKEND_URL environment variable
export const API_BASE_URL = isDevelopment ? 'http://localhost:8000' : import.meta.env.VITE_BACKEND_URL;

console.log('Environment:', isDevelopment ? 'development' : 'production');
console.log('API_BASE_URL:', API_BASE_URL);

