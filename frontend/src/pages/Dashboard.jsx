import { useState, useEffect } from 'react';
import { Package, Users, ShoppingCart, DollarSign, TrendingUp, AlertTriangle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { productService, saleService, customerService } from '../services';

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    products: 0,
    lowStock: 0,
    customers: 0,
    salesToday: 0,
    salesMonth: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const [products, customers, sales] = await Promise.all([
        productService.getAll(),
        customerService.getAll(),
        saleService.getAll(),
      ]);

      const today = new Date().toISOString().split('T')[0];
      const currentMonth = today.substring(0, 7);

      const salesTodayData = sales.filter(s => s.created_at.startsWith(today));
      const salesMonthData = sales.filter(s => s.created_at.startsWith(currentMonth));

      const lowStockProducts = products.filter(p => p.stock <= p.min_stock);

      setStats({
        products: products.length,
        lowStock: lowStockProducts.length,
        customers: customers.length,
        salesToday: salesTodayData.reduce((sum, s) => sum + s.total, 0),
        salesMonth: salesMonthData.reduce((sum, s) => sum + s.total, 0),
      });
    } catch (error) {
      console.error('Error loading stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: 'Productos',
      value: stats.products,
      icon: Package,
      color: 'bg-blue-500',
      subtitle: 'Total en inventario',
    },
    {
      title: 'Stock Bajo',
      value: stats.lowStock,
      icon: AlertTriangle,
      color: 'bg-red-500',
      subtitle: 'Requieren atención',
    },
    {
      title: 'Clientes',
      value: stats.customers,
      icon: Users,
      color: 'bg-green-500',
      subtitle: 'Registrados',
    },
    {
      title: 'Ventas Hoy',
      value: `$${stats.salesToday.toFixed(2)}`,
      icon: DollarSign,
      color: 'bg-purple-500',
      subtitle: 'Dólares USD',
    },
    {
      title: 'Ventas Mes',
      value: `$${stats.salesMonth.toFixed(2)}`,
      icon: TrendingUp,
      color: 'bg-orange-500',
      subtitle: 'Acumulado mensual',
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Bienvenido, {user?.full_name || user?.email}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6 mb-8">
        {statCards.map((stat) => (
          <div
            key={stat.title}
            className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`${stat.color} p-3 rounded-lg`}>
                <stat.icon className="h-6 w-6 text-white" />
              </div>
            </div>
            <h3 className="text-2xl font-bold text-gray-900">{stat.value}</h3>
            <p className="text-sm text-gray-600 mt-1">{stat.title}</p>
            <p className="text-xs text-gray-500 mt-1">{stat.subtitle}</p>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Accesos Rápidos</h2>
          <div className="grid grid-cols-2 gap-4">
            <a
              href="/products"
              className="p-4 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors"
            >
              <Package className="h-6 w-6 text-primary-600 mb-2" />
              <p className="font-medium text-primary-900">Gestionar Productos</p>
            </a>
            <a
              href="/sales"
              className="p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
            >
              <ShoppingCart className="h-6 w-6 text-green-600 mb-2" />
              <p className="font-medium text-green-900">Nueva Venta</p>
            </a>
            <a
              href="/customers"
              className="p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
            >
              <Users className="h-6 w-6 text-blue-600 mb-2" />
              <p className="font-medium text-blue-900">Clientes</p>
            </a>
            <a
              href="/exchange-rate"
              className="p-4 bg-orange-50 rounded-lg hover:bg-orange-100 transition-colors"
            >
              <DollarSign className="h-6 w-6 text-orange-600 mb-2" />
              <p className="font-medium text-orange-900">Tasa BCV</p>
            </a>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Información Fiscal</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <span className="text-sm text-gray-600">IVA General</span>
              <span className="font-semibold">16%</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <span className="text-sm text-gray-600">IGTF (Pagos en USD)</span>
              <span className="font-semibold">3%</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <span className="text-sm text-gray-600">Moneda Base</span>
              <span className="font-semibold">USD</span>
            </div>
            <p className="text-xs text-gray-500 mt-4">
              * Precios en dólares americanos. Conversión a Bolívares según tasa BCV del día.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
