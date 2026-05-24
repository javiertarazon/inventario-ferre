import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useStore } from './store/store'

// Páginas
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Products from './pages/Products'
import Customers from './pages/Customers'
import Invoices from './pages/Invoices'
import PointOfSale from './pages/PointOfSale'
import Settings from './pages/Settings'

// Componentes de layout
import Sidebar from './components/Sidebar'
import Header from './components/Header'

function App() {
  const { token } = useStore()

  return (
    <BrowserRouter>
      <div className="flex h-screen bg-gray-100">
        {token && <Sidebar />}
        
        <div className={`flex-1 flex flex-col ${token ? 'ml-64' : ''}`}>
          {token && <Header />}
          
          <main className="flex-1 overflow-y-auto p-6">
            <Routes>
              <Route path="/login" element={!token ? <Login /> : <Navigate to="/dashboard" />} />
              
              {token ? (
                <>
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/products" element={<Products />} />
                  <Route path="/customers" element={<Customers />} />
                  <Route path="/invoices" element={<Invoices />} />
                  <Route path="/pos" element={<PointOfSale />} />
                  <Route path="/settings" element={<Settings />} />
                  <Route path="/" element={<Navigate to="/dashboard" />} />
                </>
              ) : (
                <Route path="*" element={<Navigate to="/login" />} />
              )}
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App
