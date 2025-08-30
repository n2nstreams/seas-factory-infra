import React, { useState } from 'react'
import { supabase } from '../../../supabase/config/client'

interface ModuleSpec {
  name: string
  description: string
  module_type: 'service' | 'api' | 'component' | 'model' | 'utility' | 'page'
  language: 'python' | 'javascript' | 'typescript' | 'html' | 'css'
  framework?: string
  dependencies?: string[]
  functions?: Array<{
    name: string
    description: string
    parameters: string[]
  }>
  api_endpoints?: Array<{
    method: string
    path: string
    handler_name: string
    description: string
  }>
  requirements?: string[]
}

interface StylePreferences {
  follow_pep8?: boolean
  use_type_hints?: boolean
  include_docstrings?: boolean
}

interface GeneratedCode {
  module_name: string
  files: Array<{
    filename: string
    content: string
    file_type: string
    language: string
    size_bytes: number
    functions: string[]
    imports: string[]
    lines: number
  }>
  total_files: number
  total_lines: number
  estimated_complexity: string
  validation_results: Record<string, { valid: boolean; errors: string[] }>
  setup_instructions: string[]
  next_steps: string[]
  reasoning: string
}

export const DevAgent: React.FC = () => {
  const [moduleSpec, setModuleSpec] = useState<ModuleSpec>({
    name: '',
    description: '',
    module_type: 'service',
    language: 'python',
    framework: 'fastapi',
    dependencies: [],
    functions: [],
    api_endpoints: [],
    requirements: []
  })

  const [stylePreferences, setStylePreferences] = useState<StylePreferences>({
    follow_pep8: true,
    use_type_hints: true,
    include_docstrings: true
  })

  const [includeTests, setIncludeTests] = useState(true)
  const [includeDocumentation, setIncludeDocumentation] = useState(true)
  const [projectId, setProjectId] = useState('')
  const [generatedCode, setGeneratedCode] = useState<GeneratedCode | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleGenerateCode = async () => {
    setIsGenerating(true)
    setError(null)

    try {
      const response = await fetch('/api/ai-agent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${(await supabase.auth.getSession()).data.session?.access_token}`
        },
        body: JSON.stringify({
          module_spec: moduleSpec,
          project_id: projectId || undefined,
          style_preferences: stylePreferences,
          include_tests: includeTests,
          include_documentation: includeDocumentation
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      setGeneratedCode(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsGenerating(false)
    }
  }

  const addFunction = () => {
    setModuleSpec(prev => ({
      ...prev,
      functions: [...(prev.functions || []), { name: '', description: '', parameters: [] }]
    }))
  }

  const updateFunction = (index: number, field: keyof ModuleSpec['functions'][0], value: any) => {
    setModuleSpec(prev => ({
      ...prev,
      functions: prev.functions?.map((func, i) => 
        i === index ? { ...func, [field]: value } : func
      )
    }))
  }

  const removeFunction = (index: number) => {
    setModuleSpec(prev => ({
      ...prev,
      functions: prev.functions?.filter((_, i) => i !== index)
    }))
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">🚀 DevAgent</h1>
        <p className="text-gray-600 mt-2">AI-powered code generation with Supabase integration</p>
      </div>

      {/* Module Specification Form */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">Module Specification</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Module Name
            </label>
            <input
              type="text"
              value={moduleSpec.name}
              onChange={(e) => setModuleSpec(prev => ({ ...prev, name: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., UserService"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Module Type
            </label>
            <select
              value={moduleSpec.module_type}
              onChange={(e) => setModuleSpec(prev => ({ ...prev, module_type: e.target.value as ModuleSpec['module_type'] }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="Select module type"
            >
              <option value="service">Service</option>
              <option value="api">API</option>
              <option value="component">Component</option>
              <option value="model">Model</option>
              <option value="utility">Utility</option>
              <option value="page">Page</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Language
            </label>
            <select
              value={moduleSpec.language}
              onChange={(e) => setModuleSpec(prev => ({ ...prev, language: e.target.value as ModuleSpec['language'] }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="Select programming language"
            >
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
              <option value="typescript">TypeScript</option>
              <option value="html">HTML</option>
              <option value="css">CSS</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Framework
            </label>
            <input
              type="text"
              value={moduleSpec.framework || ''}
              onChange={(e) => setModuleSpec(prev => ({ ...prev, framework: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., fastapi, react, express"
            />
          </div>
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            value={moduleSpec.description}
            onChange={(e) => setModuleSpec(prev => ({ ...prev, description: e.target.value }))}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Describe what this module does..."
          />
        </div>

        {/* Functions Section */}
        <div className="mt-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-medium">Functions</h3>
            <button
              onClick={addFunction}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Add Function
            </button>
          </div>

          {moduleSpec.functions?.map((func, index) => (
            <div key={index} className="border border-gray-200 rounded-md p-4 mb-3">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <input
                  type="text"
                  value={func.name}
                  onChange={(e) => updateFunction(index, 'name', e.target.value)}
                  placeholder="Function name"
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="text"
                  value={func.description}
                  onChange={(e) => updateFunction(index, 'description', e.target.value)}
                  placeholder="Function description"
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <div className="flex items-center space-x-2">
                  <input
                    type="text"
                    value={func.parameters.join(', ')}
                    onChange={(e) => updateFunction(index, 'parameters', e.target.value.split(',').map(p => p.trim()))}
                    placeholder="Parameters (comma-separated)"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={() => removeFunction(index)}
                    className="px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
                  >
                    Remove
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Style Preferences */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">Style Preferences</h2>
        
        <div className="space-y-3">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={stylePreferences.follow_pep8}
              onChange={(e) => setStylePreferences(prev => ({ ...prev, follow_pep8: e.target.checked }))}
              className="mr-2"
            />
            Follow PEP 8 (Python style guide)
          </label>
          
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={stylePreferences.use_type_hints}
              onChange={(e) => setStylePreferences(prev => ({ ...prev, use_type_hints: e.target.checked }))}
              className="mr-2"
            />
            Use type hints
          </label>
          
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={stylePreferences.include_docstrings}
              onChange={(e) => setStylePreferences(prev => ({ ...prev, include_docstrings: e.target.checked }))}
              className="mr-2"
            />
            Include docstrings
          </label>
        </div>
      </div>

      {/* Options */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">Options</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Project ID (optional)
            </label>
            <input
              type="text"
              value={projectId}
              onChange={(e) => setProjectId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Store in project..."
            />
          </div>
          
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={includeTests}
              onChange={(e) => setIncludeTests(e.target.checked)}
              className="mr-2"
            />
            Include unit tests
          </label>
          
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={includeDocumentation}
              onChange={(e) => setIncludeDocumentation(e.target.checked)}
              className="mr-2"
            />
            Include documentation
          </label>
        </div>
      </div>

      {/* Generate Button */}
      <div className="text-center">
        <button
          onClick={handleGenerateCode}
          disabled={isGenerating || !moduleSpec.name || !moduleSpec.description}
          className="px-8 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isGenerating ? 'Generating...' : 'Generate Code'}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Generated Code Display */}
      {generatedCode && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Generated Code</h2>
          
          <div className="mb-4 p-4 bg-gray-50 rounded-md">
            <p><strong>Module:</strong> {generatedCode.module_name}</p>
            <p><strong>Files:</strong> {generatedCode.total_files}</p>
            <p><strong>Lines:</strong> {generatedCode.total_lines}</p>
            <p><strong>Complexity:</strong> {generatedCode.estimated_complexity}</p>
          </div>

          {generatedCode.files.map((file, index) => (
            <div key={index} className="mb-4">
              <h3 className="font-medium text-gray-900 mb-2">{file.filename}</h3>
              <pre className="bg-gray-900 text-green-400 p-4 rounded-md overflow-x-auto text-sm">
                <code>{file.content}</code>
              </pre>
            </div>
          ))}

          <div className="mt-6">
            <h3 className="font-medium text-gray-900 mb-2">Setup Instructions</h3>
            <ol className="list-decimal list-inside space-y-1 text-gray-700">
              {generatedCode.setup_instructions.map((instruction, index) => (
                <li key={index}>{instruction}</li>
              ))}
            </ol>
          </div>

          <div className="mt-4">
            <h3 className="font-medium text-gray-900 mb-2">Next Steps</h3>
            <ol className="list-decimal list-inside space-y-1 text-gray-700">
              {generatedCode.next_steps.map((step, index) => (
                <li key={index}>{step}</li>
              ))}
            </ol>
          </div>
        </div>
      )}
    </div>
  )
}

export default DevAgent
