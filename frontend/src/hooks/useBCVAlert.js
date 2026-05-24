import { useState } from 'react';

export const useBCVAlert = () => {
  const [alert, setAlert] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  const maxRetries = 3;

  const checkBCVStatus = async (updateFromBCV) => {
    if (retryCount >= maxRetries) {
      setAlert({
        type: 'error',
        title: 'Error de Conexión BCV',
        message: `No se pudo conectar con el BCV después de ${maxRetries} intentos. Por favor verifique su conexión a internet o actualice la tasa manualmente.`,
        action: 'manual',
      });
      return false;
    }

    try {
      const result = await updateFromBCV();
      if (result.success) {
        setAlert(null);
        setRetryCount(0);
        return true;
      } else {
        setRetryCount(prev => prev + 1);
        if (retryCount + 1 >= maxRetries) {
          setAlert({
            type: 'warning',
            title: 'Advertencia BCV',
            message: `Intento ${retryCount + 1}/${maxRetries} fallido. Se recomienda actualizar manualmente.`,
            action: 'retry',
          });
        }
        return false;
      }
    } catch (error) {
      setRetryCount(prev => prev + 1);
      if (retryCount + 1 >= maxRetries) {
        setAlert({
          type: 'error',
          title: 'Error de Conexión BCV',
          message: `No se pudo conectar con el BCV después de ${maxRetries} intentos.`,
          action: 'manual',
        });
      }
      return false;
    }
  };

  const dismissAlert = () => {
    setAlert(null);
  };

  const resetRetries = () => {
    setRetryCount(0);
  };

  return {
    alert,
    retryCount,
    maxRetries,
    checkBCVStatus,
    dismissAlert,
    resetRetries,
  };
};
