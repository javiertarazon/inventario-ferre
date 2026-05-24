import { useState, useEffect } from 'react';
import { DollarSign, RefreshCw, AlertCircle, CheckCircle, TrendingUp } from 'lucide-react';
import { useExchangeRate } from '../hooks/useExchangeRate';
import { exchangeRateService } from '../services';
import Alert from '../components/Alert';

export default function ExchangeRate() {
  const { rate, loading, error, lastUpdate, refresh, updateFromBCV, updateManual } = useExchangeRate();
  const [manualRate, setManualRate] = useState('');
  const [updating, setUpdating] = useState(false);
  const [history, setHistory] = useState([]);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const data = await exchangeRateService.getHistory({ limit: 10 });
      setHistory(data);
    } catch (error) {
      console.error('Error loading history:', error);
    }
  };

  const handleUpdateBCV = async () => {
    setUpdating(true);
    setMessage(null);
    
    const result = await updateFromBCV();
    
    if (result.success) {
      setMessage({
        type: 'success',
        text: `Tasa actualizada exitosamente desde BCV: ${result.data.rate.toFixed(2)} VES/USD`,
      });
      loadHistory();
    } else {
      setMessage({
        type: 'error',
        text: result.error || 'Error al actualizar desde BCV',
      });
    }
    
    setUpdating(false);
  };

  const handleManualUpdate = async (e) => {
    e.preventDefault();
    if (!manualRate || parseFloat(manualRate) <= 0) {
      setMessage({ type: 'error', text: 'Ingrese una tasa válida' });
      return;
    }

    setUpdating(true);
    setMessage(null);
    
    const result = await updateManual(parseFloat(manualRate));
    
    if (result.success) {
      setMessage({
        type: 'success',
        text: `Tasa actualizada manualmente: ${result.data.rate.toFixed(2)} VES/USD`,
      });
      setManualRate('');
      loadHistory();
    } else {
      setMessage({ type: 'error', text: 'Error al actualizar manualmente' });
    }
    
    setUpdating(false);
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Tasa de Cambio BCV</h1>
        <p className="text-gray-600 mt-2">
          Gestión de la tasa oficial del Banco Central de Venezuela
        </p>
      </div>

      {/* Message Alert */}
      {message && (
        <Alert
          type={message.type}
          title={message.type === 'success' ? 'Éxito' : 'Error'}
          message={message.text}
          onDismiss={() => setMessage(null)}
        />
      )}

      {/* Current Rate Card */}
      <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="bg-green-100 p-3 rounded-lg">
              <DollarSign className="h-8 w-8 text-green-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Tasa Actual</h2>
              <p className="text-sm text-gray-500">
                {lastUpdate 
                  ? `Actualizado: ${new Date(lastUpdate).toLocaleString('es-VE')}`
                  : 'Sin actualizar'}
              </p>
            </div>
          </div>
          <button
            onClick={refresh}
            disabled={loading}
            className="p-2 text-gray-400 hover:text-gray-600"
          >
            <RefreshCw className={`h-5 w-5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        <div className="flex items-baseline gap-2">
          <span className="text-4xl font-bold text-gray-900">
            {rate ? `${rate.toFixed(2)}` : '--.--'}
          </span>
          <span className="text-lg text-gray-600">VES/USD</span>
        </div>

        {error && (
          <div className="mt-4 flex items-center gap-2 text-red-600">
            <AlertCircle className="h-5 w-5" />
            <span className="text-sm">{error}</span>
          </div>
        )}
      </div>

      {/* Action Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Update from BCV */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Actualizar desde BCV
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Obtiene automáticamente la tasa oficial del sitio web del BCV.
            El sistema realiza hasta 3 intentos automáticos al iniciar.
          </p>
          <button
            onClick={handleUpdateBCV}
            disabled={updating || loading}
            className="w-full bg-primary-600 text-white py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <RefreshCw className={`h-5 w-5 ${updating ? 'animate-spin' : ''}`} />
            {updating ? 'Actualizando...' : 'Actualizar desde BCV'}
          </button>
        </div>

        {/* Manual Update */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Actualización Manual
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Ingrese manualmente la tasa si no puede conectarse al BCV.
          </p>
          <form onSubmit={handleManualUpdate} className="space-y-4">
            <div>
              <label htmlFor="manualRate" className="block text-sm font-medium text-gray-700 mb-2">
                Tasa VES/USD
              </label>
              <input
                id="manualRate"
                type="number"
                step="0.01"
                value={manualRate}
                onChange={(e) => setManualRate(e.target.value)}
                placeholder="36.50"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            <button
              type="submit"
              disabled={updating || !manualRate}
              className="w-full bg-green-600 text-white py-3 rounded-lg font-medium hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <CheckCircle className="h-5 w-5" />
              Actualizar Manualmente
            </button>
          </form>
        </div>
      </div>

      {/* History Table */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          Historial de Tasas
        </h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Fecha
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tasa (VES/USD)
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Fuente
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {history.length === 0 ? (
                <tr>
                  <td colSpan="3" className="px-6 py-4 text-center text-gray-500">
                    No hay historial disponible
                  </td>
                </tr>
              ) : (
                history.map((item, index) => (
                  <tr key={index} className={index === 0 ? 'bg-green-50' : ''}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(item.created_at).toLocaleString('es-VE')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {item.rate.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.source === 'bcv' ? 'BCV Automático' : 'Manual'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
