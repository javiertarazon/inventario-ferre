import React, { useState, useEffect } from 'react';
import productService from '../services/productService';
import customerService from '../services/customerService';
import saleService from '../services/saleService';
import exchangeRateService from '../services/exchangeRateService';
import Alert from '../components/Alert';

const PointOfSale = () => {
  const [products, setProducts] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [cart, setCart] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCustomer, setSelectedCustomer] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('cash_usd');
  const [exchangeRate, setExchangeRate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showCheckoutModal, setShowCheckoutModal] = useState(false);
  const [showReceiptModal, setShowReceiptModal] = useState(false);
  const [lastSale, setLastSale] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [productsData, customersData, rateData] = await Promise.all([
        productService.getProducts({ limit: 100 }),
        customerService.getCustomers({ limit: 100 }),
        exchangeRateService.getCurrentRate()
      ]);
      
      setProducts(productsData.results || []);
      setCustomers(customersData.results || []);
      setExchangeRate(rateData.rate || 36.5);
      setError(null);
    } catch (err) {
      setError('Error al cargar datos: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const addToCart = (product) => {
    const existingItem = cart.find(item => item.id === product.id);
    
    if (existingItem) {
      if (existingItem.quantity >= product.stock) {
        setError('No hay suficiente stock disponible');
        setTimeout(() => setError(null), 3000);
        return;
      }
      setCart(cart.map(item =>
        item.id === product.id
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
    } else {
      setCart([...cart, { ...product, quantity: 1 }]);
    }
  };

  const removeFromCart = (productId) => {
    setCart(cart.filter(item => item.id !== productId));
  };

  const updateQuantity = (productId, newQuantity) => {
    if (newQuantity <= 0) {
      removeFromCart(productId);
      return;
    }
    
    const product = products.find(p => p.id === productId);
    if (newQuantity > product.stock) {
      setError('No hay suficiente stock disponible');
      setTimeout(() => setError(null), 3000);
      return;
    }
    
    setCart(cart.map(item =>
      item.id === productId
        ? { ...item, quantity: newQuantity }
        : item
    ));
  };

  const calculateSubtotal = () => {
    return cart.reduce((sum, item) => sum + (item.price_usd * item.quantity), 0);
  };

  const calculateTax = () => {
    return cart.reduce((sum, item) => {
      const taxRate = item.tax_rate === 'general' ? 0.16 : item.tax_rate === 'reduced' ? 0.08 : 0;
      return sum + (item.price_usd * item.quantity * taxRate);
    }, 0);
  };

  const calculateTotal = () => {
    return calculateSubtotal() + calculateTax();
  };

  const calculateTotalVES = () => {
    return calculateTotal() * exchangeRate;
  };

  const calculateIGTF = () => {
    // IGTF 3% para pagos en divisas
    if (paymentMethod.includes('usd')) {
      return calculateTotal() * 0.03;
    }
    return 0;
  };

  const calculateFinalTotal = () => {
    let total = calculateTotal();
    if (paymentMethod.includes('usd')) {
      total += calculateIGTF();
    }
    return total;
  };

  const handleCheckout = async () => {
    if (cart.length === 0) {
      setError('El carrito está vacío');
      setTimeout(() => setError(null), 3000);
      return;
    }

    if (!selectedCustomer) {
      setError('Debe seleccionar un cliente');
      setTimeout(() => setError(null), 3000);
      return;
    }

    try {
      const saleData = {
        customer_id: parseInt(selectedCustomer),
        payment_method: paymentMethod,
        items: cart.map(item => ({
          product_id: item.id,
          quantity: item.quantity,
          price_usd: item.price_usd
        }))
      };

      const response = await saleService.createSale(saleData);
      setLastSale(response);
      setShowCheckoutModal(false);
      setShowReceiptModal(true);
      setSuccess('Venta registrada exitosamente');
      setCart([]);
      setSearchTerm('');
      loadData(); // Recargar productos para actualizar stock
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('Error al procesar venta: ' + err.message);
      setTimeout(() => setError(null), 5000);
    }
  };

  const printReceipt = () => {
    window.print();
  };

  const getPaymentMethods = () => [
    { value: 'cash_usd', label: 'Efectivo USD', showIGTF: true },
    { value: 'card_usd', label: 'Tarjeta USD', showIGTF: true },
    { value: 'transfer_usd', label: 'Transferencia USD', showIGTF: true },
    { value: 'cash_vef', label: 'Efectivo Bs', showIGTF: false },
    { value: 'card_vef', label: 'Tarjeta Bs', showIGTF: false },
    { value: 'transfer_vef', label: 'Transferencia Bs', showIGTF: false }
  ];

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Punto de Venta</h1>

      {error && <Alert type="error" message={error} onClose={() => setError(null)} />}
      {success && <Alert type="success" message={success} onClose={() => setSuccess(null)} />}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Lista de Productos */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="mb-4">
              <input
                type="text"
                placeholder="Buscar producto por nombre o código..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-96 overflow-y-auto">
              {filteredProducts.map((product) => (
                <div
                  key={product.id}
                  onClick={() => addToCart(product)}
                  className={`border rounded-lg p-4 cursor-pointer hover:shadow-md transition-shadow ${
                    product.stock === 0 ? 'opacity-50 bg-gray-100' : 'bg-white hover:border-blue-500'
                  }`}
                >
                  <h3 className="font-medium text-gray-900 truncate">{product.name}</h3>
                  <p className="text-sm text-gray-500">{product.code}</p>
                  <div className="mt-2 flex justify-between items-center">
                    <span className="text-lg font-bold text-blue-600">${product.price_usd.toFixed(2)}</span>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      product.stock === 0 ? 'bg-red-100 text-red-800' :
                      product.stock <= product.min_stock ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {product.stock} {product.unit}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Carrito */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow p-6 sticky top-6">
            <h2 className="text-lg font-bold text-gray-800 mb-4">Carrito de Compras</h2>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Cliente *</label>
              <select
                value={selectedCustomer}
                onChange={(e) => setSelectedCustomer(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Seleccionar cliente</option>
                {customers.map(customer => (
                  <option key={customer.id} value={customer.id}>
                    {customer.name} ({customer.rif})
                  </option>
                ))}
              </select>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Método de Pago *</label>
              <select
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {getPaymentMethods().map(method => (
                  <option key={method.value} value={method.value}>{method.label}</option>
                ))}
              </select>
            </div>

            <div className="border-t pt-4 mb-4 max-h-64 overflow-y-auto">
              {cart.length === 0 ? (
                <p className="text-center text-gray-500 py-4">Carrito vacío</p>
              ) : (
                cart.map((item) => (
                  <div key={item.id} className="flex justify-between items-center mb-3 pb-3 border-b">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900 truncate">{item.name}</p>
                      <p className="text-xs text-gray-500">${item.price_usd.toFixed(2)} x {item.quantity}</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => updateQuantity(item.id, item.quantity - 1)}
                        className="w-6 h-6 rounded-full bg-gray-200 hover:bg-gray-300 flex items-center justify-center"
                      >
                        -
                      </button>
                      <span className="text-sm font-medium w-6 text-center">{item.quantity}</span>
                      <button
                        onClick={() => updateQuantity(item.id, item.quantity + 1)}
                        className="w-6 h-6 rounded-full bg-gray-200 hover:bg-gray-300 flex items-center justify-center"
                      >
                        +
                      </button>
                      <button
                        onClick={() => removeFromCart(item.id)}
                        className="text-red-500 hover:text-red-700 ml-2"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>

            <div className="border-t pt-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Subtotal:</span>
                <span className="font-medium">${calculateSubtotal().toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">IVA:</span>
                <span className="font-medium">${calculateTax().toFixed(2)}</span>
              </div>
              {calculateIGTF() > 0 && (
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">IGTF (3%):</span>
                  <span className="font-medium">${calculateIGTF().toFixed(2)}</span>
                </div>
              )}
              <div className="flex justify-between text-lg font-bold pt-2 border-t">
                <span>Total USD:</span>
                <span className="text-blue-600">${calculateFinalTotal().toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm pt-2 border-t">
                <span className="text-gray-600">Total Bs:</span>
                <span className="font-medium">Bs. {calculateTotalVES().toFixed(2)}</span>
              </div>
              <p className="text-xs text-gray-500 text-center mt-2">Tasa BCV: {exchangeRate?.toFixed(2)} Bs/$</p>
            </div>

            <button
              onClick={() => setShowCheckoutModal(true)}
              disabled={cart.length === 0}
              className="w-full mt-4 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white py-3 rounded-lg font-medium"
            >
              Procesar Venta
            </button>
          </div>
        </div>
      </div>

      {/* Modal de Confirmación */}
      {showCheckoutModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-full max-w-md shadow-lg rounded-md bg-white">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Confirmar Venta</h3>
            
            <div className="space-y-2 mb-4">
              <p><strong>Cliente:</strong> {customers.find(c => c.id === parseInt(selectedCustomer))?.name}</p>
              <p><strong>Método de Pago:</strong> {getPaymentMethods().find(m => m.value === paymentMethod)?.label}</p>
              <p><strong>Items:</strong> {cart.reduce((sum, item) => sum + item.quantity, 0)}</p>
              <p><strong>Total a Pagar:</strong> <span className="text-blue-600 font-bold">${calculateFinalTotal().toFixed(2)}</span></p>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowCheckoutModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleCheckout}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                Confirmar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Recibo */}
      {showReceiptModal && lastSale && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-10 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
            <div className="print:hidden flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">Factura Generada</h3>
              <button onClick={() => setShowReceiptModal(false)} className="text-gray-400 hover:text-gray-600">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div id="receipt" className="p-4 border rounded">
              <div className="text-center mb-4">
                <h2 className="text-xl font-bold">FERRETERÍA EL CONSTRUCTOR</h2>
                <p className="text-sm">RIF: J-12345678-9</p>
                <p className="text-sm">Teléfono: (0212) 123-4567</p>
                <p className="text-sm">Dirección: Av. Principal, Caracas</p>
              </div>

              <div className="border-t border-b py-4 my-4">
                <p><strong>Factura N°:</strong> {lastSale.invoice_number}</p>
                <p><strong>Fecha:</strong> {new Date(lastSale.created_at).toLocaleString()}</p>
                <p><strong>Cliente:</strong> {lastSale.customer_name}</p>
                <p><strong>RIF:</strong> {lastSale.customer_rif}</p>
                <p><strong>Método de Pago:</strong> {paymentMethod.replace('_', ' ').toUpperCase()}</p>
              </div>

              <table className="w-full mb-4">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2">Cant.</th>
                    <th className="text-left py-2">Descripción</th>
                    <th className="text-right py-2">Precio</th>
                    <th className="text-right py-2">Total</th>
                  </tr>
                </thead>
                <tbody>
                  {lastSale.items.map((item, index) => (
                    <tr key={index} className="border-b">
                      <td className="py-2">{item.quantity}</td>
                      <td className="py-2">{item.product_name}</td>
                      <td className="text-right py-2">${item.price_usd.toFixed(2)}</td>
                      <td className="text-right py-2">${(item.price_usd * item.quantity).toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <div className="text-right space-y-1">
                <p>Subtotal: ${lastSale.subtotal_usd.toFixed(2)}</p>
                <p>IVA: ${lastSale.tax_usd.toFixed(2)}</p>
                {lastSale.igtf_usd > 0 && <p>IGTF (3%): ${lastSale.igtf_usd.toFixed(2)}</p>}
                <p className="text-lg font-bold">Total: ${lastSale.total_usd.toFixed(2)}</p>
                <p className="text-sm text-gray-600">Total Bs: Bs. {lastSale.total_vef.toFixed(2)}</p>
                <p className="text-xs text-gray-500">Tasa BCV: {lastSale.exchange_rate.toFixed(2)} Bs/$</p>
              </div>

              <div className="mt-6 text-center text-xs text-gray-500">
                <p>Gracias por su compra</p>
                <p>Este documento tiene validez fiscal</p>
              </div>
            </div>

            <div className="print:hidden flex justify-end mt-4 space-x-3">
              <button
                onClick={printReceipt}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Imprimir
              </button>
              <button
                onClick={() => setShowReceiptModal(false)}
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

export default PointOfSale;
