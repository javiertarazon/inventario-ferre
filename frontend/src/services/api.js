const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const ENDPOINTS = {
  AUTH: {
    LOGIN: `${API_BASE_URL}/auth/login`,
    REGISTER: `${API_BASE_URL}/auth/register`,
    ME: `${API_BASE_URL}/auth/me`,
  },
  PRODUCTS: `${API_BASE_URL}/products`,
  CUSTOMERS: `${API_BASE_URL}/customers`,
  SALES: `${API_BASE_URL}/sales`,
  EXCHANGE_RATE: `${API_BASE_URL}/exchange-rate`,
  USERS: `${API_BASE_URL}/users`,
};

export default API_BASE_URL;
