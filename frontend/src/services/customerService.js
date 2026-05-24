import apiClient from './api';
import { ENDPOINTS } from './api';

export const customerService = {
  getCustomers: async (params = {}) => {
    const response = await apiClient.get(ENDPOINTS.CUSTOMERS.BASE, { params });
    return response.data;
  },

  getCustomer: async (id) => {
    const response = await apiClient.get(`${ENDPOINTS.CUSTOMERS.BASE}/${id}`);
    return response.data;
  },

  createCustomer: async (customerData) => {
    const response = await apiClient.post(ENDPOINTS.CUSTOMERS.BASE, customerData);
    return response.data;
  },

  updateCustomer: async (id, customerData) => {
    const response = await apiClient.put(`${ENDPOINTS.CUSTOMERS.BASE}/${id}`, customerData);
    return response.data;
  },

  deleteCustomer: async (id) => {
    const response = await apiClient.delete(`${ENDPOINTS.CUSTOMERS.BASE}/${id}`);
    return response.data;
  },
};

export default customerService;
