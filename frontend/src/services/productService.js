import apiClient from './api';
import { ENDPOINTS } from './api';

export const productService = {
  getProducts: async (params = {}) => {
    const response = await apiClient.get(ENDPOINTS.PRODUCTS.BASE, { params });
    return response.data;
  },

  getProduct: async (id) => {
    const response = await apiClient.get(`${ENDPOINTS.PRODUCTS.BASE}/${id}`);
    return response.data;
  },

  createProduct: async (productData) => {
    const response = await apiClient.post(ENDPOINTS.PRODUCTS.BASE, productData);
    return response.data;
  },

  updateProduct: async (id, productData) => {
    const response = await apiClient.put(`${ENDPOINTS.PRODUCTS.BASE}/${id}`, productData);
    return response.data;
  },

  deleteProduct: async (id) => {
    const response = await apiClient.delete(`${ENDPOINTS.PRODUCTS.BASE}/${id}`);
    return response.data;
  },
};

export default productService;
