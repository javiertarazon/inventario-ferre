import React, { useState, useEffect } from 'react';
import saleService from '../services/saleService';
import Alert from '../components/Alert';

const Invoices = () => {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [dateFilter, setDateFilter] = useState({ start: '', end: '' });
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    loadInvoices();
  }, []);

  const loadInvoices = async () => {
    try {
      setLoading(true);
      const params = {};
      if (dateFilter.start) params.start_date = dateFilter.start;
      if (dateFilter.end) params.end_date = dateFilter.end;
      if (searchTerm) params.search = searchTerm;

      const data = await saleService.getSales(params);
      setInvoices(data.results || []);
      setError(null);
    } catch (err) {
      setError('Error al cargar facturas: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    loadInvoices();
  };

  const viewInvoice = async (id) => {
    try {
      const invoice = await saleService.getSale(id);
      setSelectedInvoice(invoice);
      setShowModal(true);
    } catch (err) {
      setError('Error al cargar factura: ' + err.message);
      setTimeout(() => setError(null), 5000);
    }
  };

  const printInvoice = () => {
    window.print();
  };

  const downloadPDF = async (id) => {
    try {
      await saleService.downloadInvoicePDF(id);
    } catch (err) {
      setError('Error al descargar PDF: ' + err.message);
      setTimeout(() => setError(null), 5000);
    }
  };

  const formatCurrency = (amount) => {
    return `$${amount.toFixed(2)}`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-VE', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getPaymentMethodLabel = (method) => {
    const labels = {
      cash_usd: 'Efectivo USD',
      card_usd: 'Tarjeta USD',
      transfer_usd: 'Transferencia USD',
      cash_vef: 'Efectivo Bs',
      card_vef: 'Tarjeta Bs',
      transfer_vef: 'Transferencia Bs'
    };
    return labels[method] || method;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Facturas Emitidas</h1>

      {error && <Alert type="error" message={error} onClose={() => setError(null)} />}

      {/* Filtros */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Buscar</label>
            <input
              type="text"
              placeholder="N° Factura o Cliente"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Desde</label>
            <input
              type="date"
              value={dateFilter.start}
              onChange={(e) => setDateFilter({ ...dateFilter, start: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Hasta</label>
            <input
              type="date"
              value={dateFilter.end}
              onChange={(e) => setDateFilter({ ...dateFilter, end: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={handleSearch}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
            >
              Filtrar
            </button>
          </div>
        </div>
      </div>

      {/* Tabla de Facturas */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">N° Factura</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cliente</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">RIF</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Método Pago</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Total USD</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Total Bs</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {invoices.length === 0 ? (
                <tr>
                  <td colSpan="8" className="px-6 py-4 text-center text-gray-500">
                    No hay facturas registradas
                  </td>
                </tr>
              ) : (
                invoices.map((invoice) => (
                  <tr key={invoice.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">
                      {invoice.invoice_number}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDate(invoice.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {invoice.customer_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {invoice.customer_rif}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {getPaymentMethodLabel(invoice.payment_method)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-medium text-gray-900">
                      {formatCurrency(invoice.total_usd)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                      Bs. {invoice.total_vef.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => viewInvoice(invoice.id)}
                        className="text-blue-600 hover:text-blue-900 mr-3"
                      >
                        Ver
                      </button>
                      <button
                        onClick={() => downloadPDF(invoice.id)}
                        className="text-green-600 hover:text-green-900"
                      >
                        PDF
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal de Detalle de Factura */}
      {showModal && selectedInvoice && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-10 mx-auto p-5 border w-full max-w-3xl shadow-lg rounded-md bg-white">
            <div className="print:hidden flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">Detalle de Factura</h3>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div id="invoice-detail" className="p-4 border rounded">
              <div className="text-center mb-6">
                <h2 className="text-2xl font-bold">FERRETERÍA EL CONSTRUCTOR</h2>
                <p className="text-sm">RIF: J-12345678-9</p>
                <p className="text-sm">Teléfono: (0212) 123-4567</p>
                <p className="text-sm">Dirección: Av. Principal, Caracas, Venezuela</p>
                <p className="text-sm">Email: contacto@ferreteriaelconstructor.com</p>
              </div>

              <div className="border-t-2 border-b-2 py-4 my-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="font-bold text-lg">FACTURA N° {selectedInvoice.invoice_number}</p>
                    <p><strong>Fecha:</strong> {formatDate(selectedInvoice.created_at)}</p>
                  </div>
                  <div className="text-right">
                    <p><strong>Cliente:</strong> {selectedInvoice.customer_name}</p>
                    <p><strong>RIF:</strong> {selectedInvoice.customer_rif}</p>
                    <p><strong>Método de Pago:</strong> {getPaymentMethodLabel(selectedInvoice.payment_method)}</p>
                  </div>
                </div>
              </div>

              <table className="w-full mb-6">
                <thead>
                  <tr className="bg-gray-100 border-b-2 border-gray-300">
                    <th className="text-left py-3 px-2">#</th>
                    <th className="text-left py-3 px-2">Cant.</th>
                    <th className="text-left py-3 px-2">Código</th>
                    <th className="text-left py-3 px-2">Descripción</th>
                    <th className="text-right py-3 px-2">Precio Unit.</th>
                    <th className="text-right py-3 px-2">Total</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedInvoice.items.map((item, index) => (
                    <tr key={index} className="border-b">
                      <td className="py-3 px-2">{index + 1}</td>
                      <td className="py-3 px-2">{item.quantity}</td>
                      <td className="py-3 px-2 text-sm">{item.product_code}</td>
                      <td className="py-3 px-2">{item.product_name}</td>
                      <td className="text-right py-3 px-2">${item.price_usd.toFixed(2)}</td>
                      <td className="text-right py-3 px-2 font-medium">
                        ${(item.price_usd * item.quantity).toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <div className="flex justify-end">
                <div className="w-64 space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Subtotal:</span>
                    <span className="font-medium">${selectedInvoice.subtotal_usd.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">IVA:</span>
                    <span className="font-medium">${selectedInvoice.tax_usd.toFixed(2)}</span>
                  </div>
                  {selectedInvoice.igtf_usd > 0 && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">IGTF (3%):</span>
                      <span className="font-medium">${selectedInvoice.igtf_usd.toFixed(2)}</span>
                    </div>
                  )}
                  <div className="flex justify-between text-lg font-bold pt-2 border-t-2">
                    <span>Total USD:</span>
                    <span className="text-blue-600">${selectedInvoice.total_usd.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-sm pt-2 border-t">
                    <span className="text-gray-600">Total Bs:</span>
                    <span className="font-medium">Bs. {selectedInvoice.total_vef.toFixed(2)}</span>
                  </div>
                  <p className="text-xs text-gray-500 text-right">
                    Tasa BCV: {selectedInvoice.exchange_rate.toFixed(2)} Bs/$
                  </p>
                </div>
              </div>

              <div className="mt-8 pt-6 border-t text-center text-xs text-gray-500">
                <p>Este documento tiene validez fiscal según la normativa SENIAT</p>
                <p>Gracias por su compra</p>
              </div>
            </div>

            <div className="print:hidden flex justify-end mt-4 space-x-3">
              <button
                onClick={printInvoice}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Imprimir
              </button>
              <button
                onClick={() => downloadPDF(selectedInvoice.id)}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                Descargar PDF
              </button>
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Invoices;
