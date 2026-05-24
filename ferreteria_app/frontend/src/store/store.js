import { create } from 'zustand'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const useStore = create((set, get) => ({
  // Usuario actual
  user: null,
  token: localStorage.getItem('token'),
  
  // Tasa de cambio
  exchangeRate: null,
  bcvAlert: false,
  bcvMessage: '',
  
  // Carrito de factura
  cart: [],
  
  // Configuración
  companyInfo: {
    name: 'FERRETERÍA VENEZUELA C.A.',
    rif: 'J-12345678-9',
    address: 'Calle Principal #123, Ciudad, Venezuela',
    phone: '(0212) 123-4567',
    email: 'ventas@ferreteria.com.ve'
  },

  // Acciones de autenticación
  setUser: (user) => set({ user }),
  setToken: (token) => {
    localStorage.setItem('token', token)
    set({ token })
  },
  logout: () => {
    localStorage.removeItem('token')
    set({ user: null, token: null })
  },

  // Acciones de tasa de cambio
  setExchangeRate: (rate) => set({ exchangeRate: rate }),
  setBcvAlert: (alert, message = '') => set({ bcvAlert: alert, bcvMessage: message }),

  // Acciones del carrito
  addToCart: (product, quantity = 1) => {
    const { cart } = get()
    const existing = cart.find(item => item.product_id === product.id)
    
    if (existing) {
      set({
        cart: cart.map(item =>
          item.product_id === product.id
            ? { ...item, quantity: item.quantity + quantity }
            : item
        )
      })
    } else {
      set({
        cart: [...cart, {
          product_id: product.id,
          product_name: product.name,
          unit_price_usd: product.unit_price_usd,
          iva_rate: product.iva_rate || 0.16,
          quantity: quantity
        }]
      })
    }
  },
  
  removeFromCart: (productId) => {
    const { cart } = get()
    set({ cart: cart.filter(item => item.product_id !== productId) })
  },
  
  updateCartItem: (productId, quantity) => {
    const { cart } = get()
    if (quantity <= 0) {
      set({ cart: cart.filter(item => item.product_id !== productId) })
    } else {
      set({
        cart: cart.map(item =>
          item.product_id === productId ? { ...item, quantity } : item
        )
      })
    }
  },
  
  clearCart: () => set({ cart: [] }),

  // Calcular totales del carrito
  getCartTotals: () => {
    const { cart } = get()
    const subtotal = cart.reduce((sum, item) => sum + (item.unit_price_usd * item.quantity), 0)
    const iva = cart.reduce((sum, item) => sum + (item.unit_price_usd * item.quantity * item.iva_rate), 0)
    return { subtotal, iva, total: subtotal + iva }
  }
}))
