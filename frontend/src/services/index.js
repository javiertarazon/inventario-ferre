import axios from 'axios';
import API_BASE_URL, { ENDPOINTS } from './api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token JWT
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar errores de autenticación
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: async (email, password) => {
    const response = await apiClient.post(ENDPOINTS.AUTH.LOGIN, { email, password });
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  register: async (userData) => {
    const response = await apiClient.post(ENDPOINTS.AUTH.REGISTER, userData);
    return response.data;
  },

  getMe: async () => {
    const response = await apiClient.get(ENDPOINTS.AUTH.ME);
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
};

export const productService = {
  getAll: async (params = {}) => {
    const response = await apiClient.get(ENDPOINTS.PRODUCTS, { params });
    return response.data;
  },

  getById: async (id) => {
    const response = await apiClient.get(`${ENDPOINTS.PRODUCTS}/${id}`);
    return response.data;
  },

  create: async (productData) => {
    const response = await apiClient.post(ENDPOINTS.PRODUCTS, productData);
    return response.data;
  },

  update: async (id, productData) => {
    const response = await apiClient.put(`${ENDPOINTS.PRODUCTS}/${id}`, productData);
    return response.data;
  },

  delete: async (id) => {
    const response = await apiClient.delete(`${ENDPOINTS.PRODUCTS}/${id}`);
    return response.data;
  },
};

export const customerService = {
  getAll: async (params = {}) => {
    const response = await apiClient.get(ENDPOINTS.CUSTOMERS, { params });
    return response.data;
  },

  getById: async (id) => {
    const response = await apiClient.get(`${ENDPOINTS.CUSTOMERS}/${id}`);
    return response.data;
  },

  create: async (customerData) => {
    const response = await apiClient.post(ENDPOINTS.CUSTOMERS, customerData);
    return response.data;
  },

  update: async (id, customerData) => {
    const response = await apiClient.put(`${ENDPOINTS.CUSTOMERS}/${id}`, customerData);
    return response.data;
  },

  delete: async (id) => {
    const response = await apiClient.delete(`${ENDPOINTS.CUSTOMERS}/${id}`);
    return response.data;
  },

  validateRIF: async (rif) => {
    const response = await apiClient.get(`${ENDPOINTS.CUSTOMERS}/validate-rif/${rif}`);
    return response.data;
  },
};

export const saleService = {
  getAll: async (params = {}) => {
    const response = await apiClient.get(ENDPOINTS.SALES, { params });
    return response.data;
  },

  getById: async (id) => {
    const response = await apiClient.get(`${ENDPOINTS.SALES}/${id}`);
    return response.data;
  },

  create: async (saleData) => {
    const response = await apiClient.post(ENDPOINTS.SALES, saleData);
    return response.data;
  },

  generatePDF: async (id) => {
    const response = await apiClient.get(`${ENDPOINTS.SALES}/${id}/pdf`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

export const exchangeRateService = {
  getCurrent: async () => {
    const response = await apiClient.get(`${ENDPOINTS.EXCHANGE_RATE}/current`);
    return response.data;
  },

  updateFromBCV: async () => {
    const response = await apiClient.post(`${ENDPOINTS.EXCHANGE_RATE}/update-bcv`);
    return response.data;
  },

  updateManual: async (rate) => {
    const response = await apiClient.post(`${ENDPOINTS.EXCHANGE_RATE}/update`, { rate });
    return response.data;
  },

  getHistory: async (params = {}) => {
    const response = await apiClient.get(`${ENDPOINTS.EXCHANGE_RATE}/history`, { params });
    return response.data;
  },
};

export default apiClient;
