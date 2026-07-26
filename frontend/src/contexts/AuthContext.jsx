import { createContext, useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { login as loginApi, getProfile, logoutApi } from '../services/authService'
import toast from 'react-hot-toast'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  const clearSession = useCallback(() => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setToken(null)
    setUser(null)
  }, [])

  const loadUser = useCallback(async () => {
    const storedToken = localStorage.getItem('token')
    if (!storedToken) {
      setLoading(false)
      return
    }
    try {
      const res = await getProfile()
      setUser(res.data)
    } catch {
      clearSession()
    } finally {
      setLoading(false)
    }
  }, [clearSession])

  useEffect(() => {
    loadUser()
  }, [loadUser])

  useEffect(() => {
    const handleUnauthorized = () => {
      clearSession()
      navigate('/login', { replace: true })
    }
    window.addEventListener('auth:unauthorized', handleUnauthorized)
    return () => {
      window.removeEventListener('auth:unauthorized', handleUnauthorized)
    }
  }, [clearSession, navigate])

  const login = async (identifier, password, role) => {
    const res = await loginApi(identifier, password, role)
    const { access_token, user: userData } = res.data
    localStorage.setItem('token', access_token)
    localStorage.setItem('user', JSON.stringify(userData))
    setToken(access_token)
    setUser(userData)
    toast.success('Login successful')
    return res.data
  }

  const logout = async () => {
    try {
      if (localStorage.getItem('token')) await logoutApi()
    } catch {
      // Local logout must still succeed if the token is already expired.
    }
    clearSession()
    toast.success('Logged out')
    navigate('/login', { replace: true })
  }

  const updateUser = (userData) => {
    setUser(userData)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  )
}
