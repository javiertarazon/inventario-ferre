import apiClient from './api';
import { ENDPOINTS } from './api';

export const saleService = {
  getSales: async (params = {}) => {
    const response = await apiClient.get(ENDPOINTS.SALES.BASE, { params });
    return response.data;
  },

  getSale: async (id) => {
    const response = await apiClient.get(`${ENDPOINTS.SALES.BASE}/${id}`);
    return response.data;
  },

  createSale: async (saleData) => {
    const response = await apiClient.post(ENDPOINTS.SALES.BASE, saleData);
    return response.data;
  },

  downloadInvoicePDF: async (id) => {
    const response = await apiClient.get(`${ENDPOINTS.SALES.BASE}/${id}/pdf`, {
      responseType: 'blob',
    });
    
    // Crear blob y descargar
    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `factura-${id}.pdf`;
    link.click();
    window.URL.revokeObjectURL(url);
    
    return response.data;
  },

  getSalesSummary: async (params = {}) => {
    const response = await apiClient.get(`${ENDPOINTS.SALES.BASE}/summary`, { params });
    return response.data;
  },
};

export default saleService;
