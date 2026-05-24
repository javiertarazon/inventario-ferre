import { useEffect, useState } from 'react'
import axios from 'axios'
import { Package, AlertTriangle, DollarSign, TrendingUp } from 'lucide-react'
import { useStore } from '../store/store'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export default function Dashboard() {
  const { exchangeRate } = useStore()
  const [stats, setStats] = useState({
    totalProducts: 0,
    lowStock: 0,
    todayInvoices: 0,
    todayRevenue: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const [productsRes, lowStockRes, invoicesRes] = await Promise.all([
        axios.get(`${API_URL}/products`),
        axios.get(`${API_URL}/products/low-stock`),
        axios.get(`${API_URL}/invoices`)
      ])

      setStats({
        totalProducts: productsRes.data.length,
        lowStock: lowStockRes.data.length,
        todayInvoices: invoicesRes.data.length,
        todayRevenue: invoicesRes.data.reduce((sum, inv) => sum + inv.total_usd, 0)
      })
    } catch (error) {
      console.error('Error loading dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  const statCards = [
    {
      title: 'Total Productos',
      value: stats.totalProducts,
      icon: Package,
      color: 'bg-blue-500'
    },
    {
      title: 'Stock Bajo',
      value: stats.lowStock,
      icon: AlertTriangle,
      color: 'bg-red-500',
      alert: stats.lowStock > 0
    },
    {
      title: 'Facturas Hoy',
      value: stats.todayInvoices,
      icon: DollarSign,
      color: 'bg-green-500'
    },
    {
      title: 'Ingresos (USD)',
      value: `$${stats.todayRevenue.toFixed(2)}`,
      icon: TrendingUp,
      color: 'bg-purple-500'
    }
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Dashboard</h1>

      {/* Tarjetas de estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((card, index) => {
          const Icon = card.icon
          return (
            <div
              key={index}
              className={`bg-white rounded-lg shadow p-6 ${card.alert ? 'border-2 border-red-500' : ''}`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{card.title}</p>
                  <p className="text-2xl font-bold text-gray-800 mt-1">
                    {card.value}
                  </p>
                </div>
                <div className={`${card.color} p-3 rounded-full`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
              {card.alert && (
                <p className="text-xs text-red-600 mt-2 font-semibold">
                  ¡Requiere atención!
                </p>
              )}
            </div>
          )
        })}
      </div>

      {/* Tasa de cambio */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">
          Información del Sistema
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center">
            <DollarSign className="w-5 h-5 text-blue-600 mr-2" />
            <span className="text-gray-700">Tasa BCV: </span>
            <span className="font-semibold ml-1">
              Bs. {exchangeRate?.toFixed(2) || 'No disponible'}
            </span>
          </div>
          <div className="flex items-center">
            <Package className="w-5 h-5 text-green-600 mr-2" />
            <span className="text-gray-700">Moneda Base: </span>
            <span className="font-semibold ml-1">USD ($)</span>
          </div>
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 text-yellow-600 mr-2" />
            <span className="text-gray-700">IVA General: </span>
            <span className="font-semibold ml-1">16%</span>
          </div>
        </div>
      </div>

      {/* Accesos rápidos */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">
          Accesos Rápidos
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a
            href="/pos"
            className="block p-4 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
          >
            <h3 className="font-semibold text-blue-800">Punto de Venta</h3>
            <p className="text-sm text-blue-600 mt-1">
              Crear nueva factura
            </p>
          </a>
          <a
            href="/products"
            className="block p-4 bg-green-50 hover:bg-green-100 rounded-lg transition-colors"
          >
            <h3 className="font-semibold text-green-800">Productos</h3>
            <p className="text-sm text-green-600 mt-1">
              Gestionar inventario
            </p>
          </a>
          <a
            href="/customers"
            className="block p-4 bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors"
          >
            <h3 className="font-semibold text-purple-800">Clientes</h3>
            <p className="text-sm text-purple-600 mt-1">
              Administrar clientes
            </p>
          </a>
        </div>
      </div>
    </div>
  )
}
