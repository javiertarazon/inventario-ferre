import apiClient from './api';
import { ENDPOINTS } from './api';

export const exchangeRateService = {
  getCurrentRate: async () => {
    const response = await apiClient.get(`${ENDPOINTS.EXCHANGE_RATE.BASE}/current`);
    return response.data;
  },

  updateFromBCV: async () => {
    const response = await apiClient.post(`${ENDPOINTS.EXCHANGE_RATE.BASE}/update-bcv`);
    return response.data;
  },

  updateManual: async (rate) => {
    const response = await apiClient.post(`${ENDPOINTS.EXCHANGE_RATE.BASE}/update`, { rate });
    return response.data;
  },

  getHistory: async (params = {}) => {
    const response = await apiClient.get(`${ENDPOINTS.EXCHANGE_RATE.BASE}/history`, { params });
    return response.data;
  },
};

export default exchangeRateService;
