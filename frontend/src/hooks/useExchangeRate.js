import { useState, useEffect } from 'react';
import { exchangeRateService } from '../services';

export const useExchangeRate = () => {
  const [rate, setRate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  const fetchRate = async () => {
    try {
      setLoading(true);
      const data = await exchangeRateService.getCurrent();
      setRate(data.rate);
      setLastUpdate(data.updated_at);
      setError(null);
    } catch (err) {
      setError('No se pudo obtener la tasa de cambio');
    } finally {
      setLoading(false);
    }
  };

  const updateFromBCV = async () => {
    try {
      setLoading(true);
      const data = await exchangeRateService.updateFromBCV();
      setRate(data.rate);
      setLastUpdate(data.updated_at);
      setError(null);
      return { success: true, data };
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Error al actualizar desde BCV';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const updateManual = async (newRate) => {
    try {
      setLoading(true);
      const data = await exchangeRateService.updateManual(newRate);
      setRate(data.rate);
      setLastUpdate(data.updated_at);
      setError(null);
      return { success: true, data };
    } catch (err) {
      setError('Error al actualizar la tasa manualmente');
      return { success: false, error: 'Error al actualizar' };
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRate();
  }, []);

  return {
    rate,
    loading,
    error,
    lastUpdate,
    refresh: fetchRate,
    updateFromBCV,
    updateManual,
  };
};
