import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Package, 
  Users, 
  FileText, 
  ShoppingCart, 
  Settings as SettingsIcon,
  LogOut
} from 'lucide-react'
import { useStore } from '../store/store'

const menuItems = [
  { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/pos', icon: ShoppingCart, label: 'Punto de Venta' },
  { path: '/products', icon: Package, label: 'Productos' },
  { path: '/customers', icon: Users, label: 'Clientes' },
  { path: '/invoices', icon: FileText, label: 'Facturas' },
  { path: '/settings', icon: SettingsIcon, label: 'Configuración' },
]

export default function Sidebar() {
  const location = useLocation()
  const { logout } = useStore()

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-blue-900 text-white z-50">
      <div className="p-6">
        <h1 className="text-xl font-bold">Ferretería Venezuela</h1>
        <p className="text-xs text-blue-300 mt-1">Sistema de Gestión</p>
      </div>

      <nav className="mt-6">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center px-6 py-3 text-sm transition-colors ${
                isActive
                  ? 'bg-blue-800 border-r-4 border-white'
                  : 'hover:bg-blue-800'
              }`}
            >
              <Icon className="w-5 h-5 mr-3" />
              {item.label}
            </Link>
          )
        })}
      </nav>

      <div className="absolute bottom-0 left-0 right-0 p-6">
        <button
          onClick={logout}
          className="flex items-center w-full px-4 py-2 text-sm text-red-300 hover:bg-red-900 rounded transition-colors"
        >
          <LogOut className="w-5 h-5 mr-3" />
          Cerrar Sesión
        </button>
      </div>
    </aside>
  )
}
