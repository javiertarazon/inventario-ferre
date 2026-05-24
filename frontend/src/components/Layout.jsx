import { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import Alert from './Alert';
import { useBCVAlert } from '../hooks/useBCVAlert';
import { useExchangeRate } from '../hooks/useExchangeRate';

export default function Layout({ children }) {
  const { alert, checkBCVStatus, dismissAlert } = useBCVAlert();
  const { updateFromBCV } = useExchangeRate();

  useEffect(() => {
    // Verificar BCV al montar el layout
    checkBCVStatus(updateFromBCV);
  }, []);

  return (
    <div className="min-h-screen bg-gray-100">
      <Sidebar />
      
      {/* Main content */}
      <main className="lg:ml-64 pt-16 lg:pt-0">
        <div className="p-4 lg:p-8">
          {/* BCV Alert */}
          {alert && (
            <Alert
              type={alert.type}
              title={alert.title}
              message={alert.message}
              onDismiss={dismissAlert}
              action={alert.action === 'manual' ? (
                <button
                  onClick={() => window.location.href = '/exchange-rate'}
                  className="text-sm font-medium underline"
                >
                  Ir a actualizar manualmente
                </button>
              ) : null}
            />
          )}
          
          {children}
        </div>
      </main>
    </div>
  );
}
