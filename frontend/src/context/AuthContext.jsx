import { createContext, useContext, useEffect, useState, useCallback, useMemo } from 'react'
import { getMeApi, loginApi, logoutApi, registerApi, getCsrfApi } from '../api/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const refreshUser = useCallback(async () => {
    try {
      const data = await getMeApi()
      setUser(data || null)
      return data
    } catch (err) {
      setUser(null)
      throw err
    }
  }, [])

  useEffect(() => {
    let isMounted = true

    async function initAuth() {
      try {
        await getCsrfApi()
        const currentUser = await getMeApi()
        if (isMounted) {
          setUser(currentUser || null)
        }
      } catch (err) {
        if (isMounted) {
          setUser(null)
          setError(err)
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    initAuth()

    return () => {
      isMounted = false
    }
  }, [])

  const login = useCallback(async ({ username_or_email, password, remember_me }) => {
    setError(null)
    const loggedInUser = await loginApi({ username_or_email, password, remember_me })
    setUser(loggedInUser)
    return loggedInUser
  }, [])

  const register = useCallback(
    async ({ username, email, password, password2, role, phone }) => {
      setError(null)
      const registeredUser = await registerApi({
        username,
        email,
        password,
        password2,
        role,
        phone,
      })

      // Attempt immediate session login with credentials for seamless user experience
      try {
        const loggedInUser = await loginApi({
          username_or_email: username,
          password,
          remember_me: true,
        })
        setUser(loggedInUser)
        return loggedInUser
      } catch {
        // If auto-login fails, return the registered user info
        setUser(null)
        return registeredUser
      }
    },
    []
  )

  const logout = useCallback(async () => {
    setError(null)
    try {
      await logoutApi()
    } finally {
      setUser(null)
    }
  }, [])

  const value = useMemo(
    () => ({
      user,
      loading,
      error,
      isAuthenticated: Boolean(user),
      isVerified: Boolean(user?.email_verified),
      isManager: user?.role === 'manager',
      isGuest: user?.role === 'guest',
      login,
      register,
      logout,
      refreshUser,
    }),
    [user, loading, error, login, register, logout, refreshUser]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export default AuthContext
