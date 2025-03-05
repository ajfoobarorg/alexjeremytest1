const isDevelopment = import.meta.env.DEV;

// In development, use localhost:8000
// In production, use the BACKEND_URL environment variable
export const API_BASE_URL = isDevelopment ? 'http://localhost:8000' : import.meta.env.BACKEND_URL;
