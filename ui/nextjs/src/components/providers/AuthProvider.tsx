'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface User {
  id: string
  name: string
  email: string
  plan: 'starter' | 'pro' | 'growth'
  buildHours: {
    used: number
    total: number | 'unlimited'
  }
}

interface AuthContextType {
  user: User | null
  setUser: (user: User | null) => void
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Load user from localStorage on app start (maintaining compatibility)
  useEffect(() => {
    const loadUser = async () => {
      console.log('AuthProvider: Starting user load...')
      try {
        // Check for existing session in localStorage
        const savedUser = localStorage.getItem('saas-factory-user')
        if (savedUser) {
          try {
            const parsedUser = JSON.parse(savedUser)
            console.log('AuthProvider: Found saved user:', parsedUser)
            setUser(parsedUser)
          } catch (parseError) {
            console.warn('Invalid user data in localStorage, clearing...')
            localStorage.removeItem('saas-factory-user')
          }
        } else {
          console.log('AuthProvider: No saved user found')
        }

        // Check for existing session token
        const token = localStorage.getItem('saas-factory-token')
        if (token) {
          console.log('AuthProvider: Found token, attempting validation...')
          // Try to validate token with backend, but don't block on failure
          try {
            const response = await fetch('/api/auth/validate', {
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
              },
            })
            
            if (response.ok) {
              const userData = await response.json()
              console.log('AuthProvider: Token validation successful:', userData)
              setUser(userData)
              localStorage.setItem('saas-factory-user', JSON.stringify(userData))
            } else {
              console.log('AuthProvider: Token validation failed, clearing storage')
              // Token invalid, clear storage
              localStorage.removeItem('saas-factory-token')
              localStorage.removeItem('saas-factory-user')
              setUser(null)
            }
          } catch (error) {
            console.warn('Auth validation endpoint not available, using local storage fallback:', error)
            // On error, keep user logged in from localStorage but mark as potentially stale
            // This prevents the app from getting stuck in loading state
          }
        } else {
          console.log('AuthProvider: No token found')
        }
      } catch (error) {
        console.error('Error loading user:', error)
      } finally {
        console.log('AuthProvider: Setting loading to false')
        // Always set loading to false, even if there are errors
        setIsLoading(false)
      }
    }

    // Add a timeout to prevent infinite loading
    const timeoutId = setTimeout(() => {
      console.warn('Auth loading timeout reached, forcing loading state to false')
      setIsLoading(false)
    }, 5000) // 5 second timeout

    loadUser()

    return () => clearTimeout(timeoutId)
  }, [])

  const handleSetUser = (newUser: User | null) => {
    setUser(newUser)
    if (newUser) {
      localStorage.setItem('saas-factory-user', JSON.stringify(newUser))
    } else {
      localStorage.removeItem('saas-factory-user')
      localStorage.removeItem('saas-factory-token')
    }
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('saas-factory-user')
    localStorage.removeItem('saas-factory-token')
    
    // Redirect to home page
    if (typeof window !== 'undefined') {
      window.location.href = '/'
    }
  }

  const value: AuthContextType = {
    user,
    setUser: handleSetUser,
    logout,
    isLoading,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
