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
  const { data: { session }, error } = await supabase.auth.getSession()
  if (error) {
    console.error('Error getting Supabase session:', error)
    return null
  }
  return session
}

// Helper function to sign out
export const signOutSupabase = async () => {
  const { error } = await supabase.auth.signOut()
  if (error) {
    console.error('Error signing out from Supabase:', error)
    throw error
  }
}

// Helper function to get user
export const getSupabaseUser = async () => {
  const { data: { user }, error } = await supabase.auth.getUser()
  if (error) {
    console.error('Error getting Supabase user:', error)
    return null
  }
  return user
}
