import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  }
})

// Helper function to get user session
export const getSupabaseSession = async () => {
  try {
    // Add timeout to prevent hanging
    const timeoutPromise = new Promise((_, reject) => 
      setTimeout(() => reject(new Error('Session check timeout')), 5000)
    )
    
    const sessionPromise = supabase.auth.getSession()
    const { data: { session }, error } = await Promise.race([sessionPromise, timeoutPromise]) as any
    
    if (error) {
      console.error('Error getting Supabase session:', error)
      return null
    }
    return session
  } catch (error) {
    console.error('Error getting Supabase session:', error)
    return null
  }
}

// Helper function to sign out
export const signOutSupabase = async () => {
  try {
    const { error } = await supabase.auth.signOut()
    if (error) {
      console.error('Error signing out from Supabase:', error)
      throw error
    }
  } catch (error) {
    console.error('Error signing out from Supabase:', error)
    throw error
  }
}

// Helper function to get user
export const getSupabaseUser = async () => {
  try {
    // Add timeout to prevent hanging
    const timeoutPromise = new Promise((_, reject) => 
      setTimeout(() => reject(new Error('User check timeout')), 5000)
    )
    
    const userPromise = supabase.auth.getUser()
    const { data: { user }, error } = await Promise.race([userPromise, timeoutPromise]) as any
    
    if (error) {
      console.error('Error getting Supabase user:', error)
      return null
    }
    return user
  } catch (error) {
    console.error('Error getting Supabase user:', error)
    return null
  }
}
