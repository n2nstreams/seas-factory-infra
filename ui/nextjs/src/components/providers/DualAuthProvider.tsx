'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'
import { useFeatureFlags } from './FeatureFlagProvider'
import { supabase, getSupabaseSession, getSupabaseUser } from '@/lib/supabase'

interface User {
  id: string
  email: string
  name?: string
  avatar?: string
  tenant_id?: string
  role?: string
  provider?: 'legacy' | 'supabase'
}

interface DualAuthContextType {
  user: User | null
  loading: boolean
  signInWithSupabase: (email: string, password: string) => Promise<void>
  signInWithOAuth: (provider: 'google' | 'github') => Promise<void>
  signOut: () => Promise<void>
  refreshUser: () => Promise<void>
}

const DualAuthContext = createContext<DualAuthContextType | undefined>(undefined)

export const useDualAuth = () => {
  const context = useContext(DualAuthContext)
  if (context === undefined) {
    throw new Error('useDualAuth must be used within a DualAuthProvider')
  }
  return context
}

interface DualAuthProviderProps {
  children: React.ReactNode
}

export const DualAuthProvider: React.FC<DualAuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const { flags } = useFeatureFlags()

  // Initialize authentication state
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        if (flags.auth_supabase) {
          // Try Supabase authentication first
          const session = await getSupabaseSession()
          if (session?.user) {
            const supabaseUser = await getSupabaseUser()
            if (supabaseUser) {
              setUser({
                id: supabaseUser.id,
                email: supabaseUser.email || '',
                name: supabaseUser.user_metadata?.full_name,
                avatar: supabaseUser.user_metadata?.avatar_url,
                provider: 'supabase'
              })
            }
          }
        }
        
        // TODO: Add legacy authentication check here
        // This will be implemented when we connect to your existing OAuth system
        
      } catch (error) {
        console.error('Error initializing authentication:', error)
      } finally {
        setLoading(false)
      }
    }

    initializeAuth()
  }, [flags.auth_supabase])

  // Listen for Supabase auth changes
  useEffect(() => {
    if (!flags.auth_supabase) return

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        if (event === 'SIGNED_IN' && session?.user) {
          const supabaseUser = await getSupabaseUser()
          if (supabaseUser) {
            setUser({
              id: supabaseUser.id,
              email: supabaseUser.email || '',
              name: supabaseUser.user_metadata?.full_name,
              avatar: supabaseUser.user_metadata?.avatar_url,
              provider: 'supabase'
            })
          }
        } else if (event === 'SIGNED_OUT') {
          setUser(null)
        }
      }
    )

    return () => subscription.unsubscribe()
  }, [flags.auth_supabase])

  const signInWithSupabase = async (email: string, password: string) => {
    if (!flags.auth_supabase) {
      throw new Error('Supabase authentication is not enabled')
    }

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password
      })

      if (error) throw error

      if (data.user) {
        setUser({
          id: data.user.id,
          email: data.user.email || '',
          name: data.user.user_metadata?.full_name,
          avatar: data.user.user_metadata?.avatar_url,
          provider: 'supabase'
        })
      }
    } catch (error) {
      console.error('Error signing in with Supabase:', error)
      throw error
    }
  }

  const signInWithOAuth = async (provider: 'google' | 'github') => {
    if (!flags.auth_supabase) {
      // Fall back to legacy OAuth
      // TODO: Implement legacy OAuth flow
      console.log('Using legacy OAuth for:', provider)
      return
    }

    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider,
        options: {
          redirectTo: `${window.location.origin}/auth/callback`
        }
      })

      if (error) throw error
    } catch (error) {
      console.error('Error signing in with OAuth:', error)
      throw error
    }
  }

  const signOut = async () => {
    try {
      if (flags.auth_supabase && user?.provider === 'supabase') {
        await supabase.auth.signOut()
      }
      
      // TODO: Add legacy sign out logic here
      
      setUser(null)
    } catch (error) {
      console.error('Error signing out:', error)
      throw error
    }
  }

  const refreshUser = async () => {
    try {
      if (flags.auth_supabase) {
        const session = await getSupabaseSession()
        if (session?.user) {
          const supabaseUser = await getSupabaseUser()
          if (supabaseUser) {
            setUser({
              id: supabaseUser.id,
              email: supabaseUser.email || '',
              name: supabaseUser.user_metadata?.full_name,
              avatar: supabaseUser.user_metadata?.avatar_url,
              provider: 'supabase'
            })
          }
        }
      }
      
      // TODO: Add legacy user refresh logic here
      
    } catch (error) {
      console.error('Error refreshing user:', error)
    }
  }

  const value: DualAuthContextType = {
    user,
    loading,
    signInWithSupabase,
    signInWithOAuth,
    signOut,
    refreshUser
  }

  return (
    <DualAuthContext.Provider value={value}>
      {children}
    </DualAuthContext.Provider>
  )
}
