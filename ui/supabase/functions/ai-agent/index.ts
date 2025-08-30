import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { module_spec, project_id, style_preferences, include_tests, include_documentation } = await req.json()

    // Validate input
    if (!module_spec || !module_spec.name || !module_spec.module_type) {
      throw new Error('Invalid module specification')
    }

    // Generate code based on module specification
    const generatedCode = await generateCode(module_spec, style_preferences)

    // Store in database if project_id is provided
    if (project_id) {
      await storeGeneratedCode(project_id, module_spec, generatedCode)
    }

    return new Response(
      JSON.stringify({
        module_name: module_spec.name,
        files: generatedCode.files,
        total_files: generatedCode.files.length,
        total_lines: generatedCode.files.reduce((sum, file) => sum + file.lines, 0),
        estimated_complexity: generatedCode.complexity,
        validation_results: generatedCode.validation,
        setup_instructions: generatedCode.instructions,
        next_steps: generatedCode.nextSteps,
        reasoning: generatedCode.reasoning
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200,
      },
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 400,
      },
    )
  }
})

async function generateCode(moduleSpec: any, stylePreferences: any) {
  // This is where you'd integrate with OpenAI or other AI services
  // For now, returning a template structure
  
  const templates = {
    service: generateServiceTemplate,
    component: generateComponentTemplate,
    api: generateAPITemplate,
    model: generateModelTemplate,
    utility: generateUtilityTemplate,
    page: generatePageTemplate
  }

  const generator = templates[moduleSpec.module_type as keyof typeof templates]
  if (!generator) {
    throw new Error(`Unsupported module type: ${moduleSpec.module_type}`)
  }

  return generator(moduleSpec, stylePreferences)
}

function generateServiceTemplate(moduleSpec: any, stylePreferences: any) {
  const { name, description, language, framework } = moduleSpec
  
  if (language === 'python' && framework === 'fastapi') {
    return {
      files: [{
        filename: `${name.toLowerCase()}_service.py`,
        content: `# ${description}
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

class ${name}Service:
    def __init__(self):
        self.app = FastAPI(title="${name} Service")
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "service": "${name}"}
        
        @self.app.get("/")
        async def root():
            return {"message": "${description}"}
    
    def run(self, host="0.0.0.0", port=8000):
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)

if __name__ == "__main__":
    service = ${name}Service()
    service.run()
`,
        file_type: 'source',
        language: 'python',
        size_bytes: 0,
        functions: ['health_check', 'root'],
        imports: ['fastapi', 'pydantic'],
        lines: 25
      }],
      complexity: 'Low',
      validation: { [`${name.toLowerCase()}_service.py`]: { valid: true, errors: [] } },
      instructions: [
        '1. Install dependencies: pip install fastapi uvicorn pydantic',
        '2. Run the service: python ${name.toLowerCase()}_service.py'
      ],
      nextSteps: [
        '1. Add your business logic methods',
        '2. Implement database models',
        '3. Add authentication and authorization'
      ],
      reasoning: 'Generated a basic FastAPI service template with health check and root endpoints'
    }
  }
  
  throw new Error(`Unsupported language/framework combination: ${language}/${framework}`)
}

function generateComponentTemplate(moduleSpec: any, stylePreferences: any) {
  const { name, description, language, framework } = moduleSpec
  
  if (language === 'typescript' && framework === 'react') {
    return {
      files: [{
        filename: `${name}.tsx`,
        content: `import React from 'react'

interface ${name}Props {
  // Add your props here
}

export const ${name}: React.FC<${name}Props> = ({ /* destructure props */ }) => {
  return (
    <div className="p-4 border rounded-lg">
      <h2 className="text-xl font-semibold mb-2">${name}</h2>
      <p className="text-gray-600">${description}</p>
      {/* Add your component content here */}
    </div>
  )
}

export default ${name}
`,
        file_type: 'source',
        language: 'typescript',
        size_bytes: 0,
        functions: ['render'],
        imports: ['react'],
        lines: 20
      }],
      complexity: 'Low',
      validation: { [`${name}.tsx`]: { valid: true, errors: [] } },
      instructions: [
        '1. Import the component in your page',
        '2. Add props and state as needed',
        '3. Style with Tailwind CSS classes'
      ],
      nextSteps: [
        '1. Add state management if needed',
        '2. Implement event handlers',
        '3. Add proper TypeScript types'
      ],
      reasoning: 'Generated a React TypeScript component with basic structure and Tailwind CSS styling'
    }
  }
  
  throw new Error(`Unsupported language/framework combination: ${language}/${framework}`)
}

function generateAPITemplate(moduleSpec: any, stylePreferences: any) {
  // Similar structure for API endpoints
  return generateServiceTemplate(moduleSpec, stylePreferences)
}

function generateModelTemplate(moduleSpec: any, stylePreferences: any) {
  // Similar structure for data models
  return generateServiceTemplate(moduleSpec, stylePreferences)
}

function generateUtilityTemplate(moduleSpec: any, stylePreferences: any) {
  // Similar structure for utility functions
  return generateServiceTemplate(moduleSpec, stylePreferences)
}

function generatePageTemplate(moduleSpec: any, stylePreferences: any) {
  // Similar structure for web pages
  return generateServiceTemplate(moduleSpec, stylePreferences)
}

async function storeGeneratedCode(projectId: string, moduleSpec: any, generatedCode: any) {
  // Store generated code in Supabase database
  // This would integrate with your database schema
  console.log(`Storing generated code for project ${projectId}`)
}
