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
      try {
        // Check for existing session in localStorage
        const savedUser = localStorage.getItem('saas-factory-user')
        if (savedUser) {
          const parsedUser = JSON.parse(savedUser)
          setUser(parsedUser)
        }

        // Check for existing session token
        const token = localStorage.getItem('saas-factory-token')
        if (token) {
          // Validate token with backend
          try {
            const response = await fetch('/api/auth/validate', {
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
              },
            })
            
            if (response.ok) {
              const userData = await response.json()
              setUser(userData)
              localStorage.setItem('saas-factory-user', JSON.stringify(userData))
            } else {
              // Token invalid, clear storage
              localStorage.removeItem('saas-factory-token')
              localStorage.removeItem('saas-factory-user')
              setUser(null)
            }
          } catch (error) {
            console.error('Error validating token:', error)
            // On error, keep user logged in but mark as potentially stale
          }
        }
      } catch (error) {
        console.error('Error loading user:', error)
      } finally {
        setIsLoading(false)
      }
    }

    loadUser()
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
