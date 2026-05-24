import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { useStore } from '../store/store'
import { LogIn, AlertCircle } from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export default function Login() {
  const navigate = useNavigate()
  const { setUser, setToken, setExchangeRate, setBcvAlert } = useStore()
  
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // Iniciar sesión
      const loginResponse = await axios.post(
        `${API_URL}/auth/login`,
        null,
        { params: { username, password } }
      )

      const { access_token } = loginResponse.data
      setToken(access_token)

      // Decodificar token para obtener información del usuario
      const tokenPayload = JSON.parse(atob(access_token.split('.')[1]))
      setUser({
        username: tokenPayload.sub,
        role: tokenPayload.role,
        full_name: 'Usuario'
      })

      // Inicializar sistema y obtener tasa BCV
      const initResponse = await axios.get(`${API_URL}/system/init`)
      const { exchange_rate, alert, bcv_message } = initResponse.data
      
      setExchangeRate(exchange_rate)
      
      if (alert) {
        setBcvAlert(true, bcv_message)
      }

      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al iniciar sesión')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-900 to-blue-700">
      <div className="bg-white p-8 rounded-lg shadow-2xl w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <LogIn className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-800">Ferretería Venezuela</h1>
          <p className="text-gray-600 mt-2">Sistema de Inventario y Facturación</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center">
            <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Usuario
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Ingrese su usuario"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Contraseña
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Ingrese su contraseña"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-xs text-gray-500">
            Sistema compatible con normativa SENIAT Venezuela
          </p>
        </div>
      </div>
    </div>
  )
}
