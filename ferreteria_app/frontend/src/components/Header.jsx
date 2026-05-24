import { Bell, DollarSign } from 'lucide-react'
import { useStore } from '../store/store'

export default function Header() {
  const { user, exchangeRate, bcvAlert, bcvMessage } = useStore()

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="flex items-center justify-between px-6 py-4">
        <div>
          <h2 className="text-lg font-semibold text-gray-800">
            Sistema de Ferretería
          </h2>
          <p className="text-sm text-gray-500">
            {new Date().toLocaleDateString('es-VE', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            })}
          </p>
        </div>

        <div className="flex items-center space-x-4">
          {/* Tasa BCV */}
          <div className="flex items-center px-4 py-2 bg-blue-50 rounded-lg">
            <DollarSign className="w-5 h-5 text-blue-600 mr-2" />
            <div>
              <p className="text-xs text-gray-500">Tasa BCV</p>
              <p className="text-sm font-semibold text-gray-800">
                Bs. {exchangeRate?.toFixed(2) || '---'}
              </p>
            </div>
          </div>

          {/* Alerta BCV */}
          {bcvAlert && (
            <div className="relative">
              <Bell className="w-6 h-6 text-red-500 animate-pulse" />
              <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
            </div>
          )}

          {/* Usuario */}
          <div className="flex items-center">
            <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
              {user?.full_name?.charAt(0) || 'U'}
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-700">
                {user?.full_name || 'Usuario'}
              </p>
              <p className="text-xs text-gray-500">
                {user?.role || 'rol'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Alerta de BCV */}
      {bcvAlert && (
        <div className="px-6 py-3 bg-red-50 border-t border-red-200">
          <div className="flex items-center">
            <Bell className="w-5 h-5 text-red-600 mr-2" />
            <p className="text-sm text-red-700">{bcvMessage}</p>
          </div>
        </div>
      )}
    </header>
  )
}
