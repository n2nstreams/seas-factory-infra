export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  public: {
    Tables: {
      profiles: {
        Row: {
          id: string
          email: string
          full_name: string | null
          avatar_url: string | null
          role: 'user' | 'admin' | 'super_admin'
          company: string | null
          position: string | null
          bio: string | null
          website: string | null
          github_username: string | null
          twitter_username: string | null
          linkedin_username: string | null
          preferences: Json
          created_at: string
          updated_at: string
        }
        Insert: {
          id: string
          email: string
          full_name?: string | null
          avatar_url?: string | null
          role?: 'user' | 'admin' | 'super_admin'
          company?: string | null
          position?: string | null
          bio?: string | null
          website?: string | null
          github_username?: string | null
          twitter_username?: string | null
          linkedin_username?: string | null
          preferences?: Json
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          email?: string
          full_name?: string | null
          avatar_url?: string | null
          role?: 'user' | 'admin' | 'super_admin'
          company?: string | null
          position?: string | null
          bio?: string | null
          website?: string | null
          github_username?: string | null
          twitter_username?: string | null
          linkedin_username?: string | null
          preferences?: Json
          created_at?: string
          updated_at?: string
        }
      }
      projects: {
        Row: {
          id: string
          name: string
          description: string | null
          status: 'draft' | 'active' | 'archived' | 'deleted'
          owner_id: string
          collaborators: Json
          tags: string[]
          settings: Json
          metadata: Json
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          name: string
          description?: string | null
          status?: 'draft' | 'active' | 'archived' | 'deleted'
          owner_id: string
          collaborators?: Json
          tags?: string[]
          settings?: Json
          metadata?: Json
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          name?: string
          description?: string | null
          status?: 'draft' | 'active' | 'archived' | 'deleted'
          owner_id?: string
          collaborators?: Json
          tags?: string[]
          settings?: Json
          metadata?: Json
          created_at?: string
          updated_at?: string
        }
      }
      code_modules: {
        Row: {
          id: string
          project_id: string | null
          name: string
          description: string | null
          module_type: 'service' | 'api' | 'component' | 'model' | 'utility' | 'page'
          language: 'python' | 'javascript' | 'typescript' | 'html' | 'css'
          framework: 'fastapi' | 'react' | 'vue' | 'express' | 'flask' | 'django' | null
          dependencies: string[]
          functions: Json
          api_endpoints: Json
          requirements: string[]
          style_preferences: Json
          generated_code: Json
          validation_results: Json
          setup_instructions: string[]
          next_steps: string[]
          reasoning: string | null
          estimated_complexity: string | null
          total_files: number
          total_lines: number
          created_by: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          project_id?: string | null
          name: string
          description?: string | null
          module_type: 'service' | 'api' | 'component' | 'model' | 'utility' | 'page'
          language: 'python' | 'javascript' | 'typescript' | 'html' | 'css'
          framework?: 'fastapi' | 'react' | 'vue' | 'express' | 'flask' | 'django' | null
          dependencies?: string[]
          functions?: Json
          api_endpoints?: Json
          requirements?: string[]
          style_preferences?: Json
          generated_code: Json
          validation_results?: Json
          setup_instructions?: string[]
          next_steps?: string[]
          reasoning?: string | null
          estimated_complexity?: string | null
          total_files?: number
          total_lines?: number
          created_by?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          project_id?: string | null
          name?: string
          description?: string | null
          module_type?: 'service' | 'api' | 'component' | 'model' | 'utility' | 'page'
          language?: 'python' | 'javascript' | 'typescript' | 'html' | 'css'
          framework?: 'fastapi' | 'react' | 'vue' | 'express' | 'flask' | 'django' | null
          dependencies?: string[]
          functions?: Json
          api_endpoints?: Json
          requirements?: string[]
          style_preferences?: Json
          generated_code?: Json
          validation_results?: Json
          setup_instructions?: string[]
          next_steps?: string[]
          reasoning?: string | null
          estimated_complexity?: string | null
          total_files?: number
          total_lines?: number
          created_by?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      ai_sessions: {
        Row: {
          id: string
          user_id: string
          project_id: string | null
          session_type: string
          input_data: Json
          output_data: Json | null
          status: string
          metadata: Json
          created_at: string
          completed_at: string | null
        }
        Insert: {
          id?: string
          user_id: string
          project_id?: string | null
          session_type: string
          input_data: Json
          output_data?: Json | null
          status?: string
          metadata?: Json
          created_at?: string
          completed_at?: string | null
        }
        Update: {
          id?: string
          user_id?: string
          project_id?: string | null
          session_type?: string
          input_data?: Json
          output_data?: Json | null
          status?: string
          metadata?: Json
          created_at?: string
          completed_at?: string | null
        }
      }
      user_activity: {
        Row: {
          id: string
          user_id: string
          action: string
          resource_type: string | null
          resource_id: string | null
          details: Json
          ip_address: string | null
          user_agent: string | null
          created_at: string
        }
        Insert: {
          id?: string
          user_id: string
          action: string
          resource_type?: string | null
          resource_id?: string | null
          details?: Json
          ip_address?: string | null
          user_agent?: string | null
          created_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          action?: string
          resource_type?: string | null
          resource_id?: string | null
          details?: Json
          ip_address?: string | null
          user_agent?: string | null
          created_at?: string
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      user_role: 'user' | 'admin' | 'super_admin'
      project_status: 'draft' | 'active' | 'archived' | 'deleted'
      module_type: 'service' | 'api' | 'component' | 'model' | 'utility' | 'page'
      code_language: 'python' | 'javascript' | 'typescript' | 'html' | 'css'
      code_framework: 'fastapi' | 'react' | 'vue' | 'express' | 'flask' | 'django'
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

export type Tables<T extends keyof Database['public']['Tables']> = Database['public']['Tables'][T]['Row']
export type Enums<T extends keyof Database['public']['Enums']> = Database['public']['Enums'][T]

// Helper types for common operations
export type Profile = Tables<'profiles'>
export type Project = Tables<'projects'>
export type CodeModule = Tables<'code_modules'>
export type AISession = Tables<'ai_sessions'>
export type UserActivity = Tables<'user_activity'>

export type InsertProfile = Database['public']['Tables']['profiles']['Insert']
export type InsertProject = Database['public']['Tables']['projects']['Insert']
export type InsertCodeModule = Database['public']['Tables']['code_modules']['Insert']
export type InsertAISession = Database['public']['Tables']['ai_sessions']['Insert']
export type InsertUserActivity = Database['public']['Tables']['user_activity']['Insert']

export type UpdateProfile = Database['public']['Tables']['profiles']['Update']
export type UpdateProject = Database['public']['Tables']['projects']['Update']
export type UpdateCodeModule = Database['public']['Tables']['code_modules']['Update']
export type UpdateAISession = Database['public']['Tables']['ai_sessions']['Update']
export type UpdateUserActivity = Database['public']['Tables']['user_activity']['Update']
