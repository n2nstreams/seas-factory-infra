import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs'

interface WireframeElement {
  type: string
  position: {
    x: number
    y: number
    width: number
    height: number
  }
  content: string
  style_properties: {
    style: string
    glassmorphism?: boolean
  }
}

interface PageWireframe {
  page_name: string
  page_type: string
  elements: WireframeElement[]
  figma_url?: string
  preview_url?: string
  metadata: {
    generated_by: string
    style: string
    project_type: string
  }
}

interface DesignRecommendation {
  project_type: string
  wireframes: PageWireframe[]
  style_guide: {
    theme: string
    primary_color: string
    secondary_color: string
    accent_color: string
    background: string
    glassmorphism_properties: {
      backdrop_filter: string
      background: string
      border: string
      border_radius: string
      box_shadow: string
    }
    typography: {
      font_family: string
      font_sizes: {
        h1: string
        h2: string
        h3: string
        body: string
        small: string
      }
    }
  }
  figma_project_url?: string
  design_system: {
    components: string[]
    glassmorphism_theme: boolean
    responsive_breakpoints: {
      mobile: string
      tablet: string
      desktop: string
    }
    spacing_scale: number[]
  }
  reasoning: string
  estimated_dev_time?: string
}

interface FigmaPreviewProps {
  onGenerateDesign?: (projectType: string, pages: string[]) => void
}

export default function FigmaPreview({ onGenerateDesign }: FigmaPreviewProps) {
  const [designs, setDesigns] = useState<DesignRecommendation[]>([])
  const [selectedDesign, setSelectedDesign] = useState<DesignRecommendation | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Mock design generation for demonstration
  const handleGenerateDesign = async (projectType: string, pages: string[]) => {
    setLoading(true)
    setError(null)
    
    try {
      // Call design agent via API gateway
      const response = await fetch('/api/design/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_type: projectType,
          pages: pages,
          style_preferences: { theme: 'glassmorphism' },
          color_scheme: 'natural',
          layout_type: 'clean',
          target_audience: 'business users'
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const design: DesignRecommendation = await response.json()
      setDesigns(prev => [design, ...prev])
      setSelectedDesign(design)
      
      if (onGenerateDesign) {
        onGenerateDesign(projectType, pages)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate design')
      console.error('Error generating design:', err)
    } finally {
      setLoading(false)
    }
  }

  const renderWireframeElement = (element: WireframeElement, index: number) => {
    const { position, content, type, style_properties } = element
    
    // Convert percentage positions to actual pixel values for preview
    const style = {
      position: 'absolute' as const,
      left: `${position.x}%`,
      top: `${position.y}px`,
      width: `${position.width}%`,
      height: `${position.height}px`,
      background: style_properties.glassmorphism 
        ? 'rgba(255, 255, 255, 0.1)' 
        : 'rgba(107, 123, 79, 0.1)',
      backdropFilter: style_properties.glassmorphism ? 'blur(8px)' : 'none',
      border: style_properties.glassmorphism 
        ? '1px solid rgba(255, 255, 255, 0.2)' 
        : '1px solid rgba(107, 123, 79, 0.3)',
      borderRadius: style_properties.glassmorphism ? '8px' : '4px',
      padding: '8px',
      fontSize: type === 'header' ? '14px' : '12px',
      fontWeight: type === 'header' ? 'bold' : 'normal',
      color: '#374151',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      textAlign: 'center' as const,
      overflow: 'hidden'
    }

    return (
      <div key={index} style={style}>
        <span className="text-xs truncate">{content}</span>
      </div>
    )
  }

  const renderWireframe = (wireframe: PageWireframe) => {
    return (
      <div className="relative bg-gray-50 border rounded-lg overflow-hidden" style={{ height: '400px' }}>
        <div className="absolute inset-0 bg-gradient-to-br from-green-50 to-green-100">
          {wireframe.elements.map((element, index) => 
            renderWireframeElement(element, index)
          )}
        </div>
        
        {/* Overlay with page info */}
        <div className="absolute top-2 left-2 right-2 flex justify-between items-start">
          <Badge variant="secondary" className="bg-white/80 backdrop-blur-sm">
            {wireframe.page_name}
          </Badge>
          {wireframe.figma_url && (
            <Button 
              size="sm" 
              variant="outline"
              className="bg-white/80 backdrop-blur-sm text-xs"
              onClick={() => window.open(wireframe.figma_url, '_blank')}
            >
              View in Figma
            </Button>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Quick Design Generator */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            🎨 Design Generator
            <Badge variant="outline">Glassmorphism Theme</Badge>
          </CardTitle>
          <CardDescription>
            Generate wireframes with natural olive green glassmorphism design
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button 
              onClick={() => handleGenerateDesign('web', ['Home', 'About', 'Contact'])}
              disabled={loading}
              className="h-20 flex flex-col items-center justify-center"
            >
              <span className="text-2xl mb-1">🌐</span>
              <span>Web Project</span>
            </Button>
            <Button 
              onClick={() => handleGenerateDesign('mobile', ['Welcome', 'Dashboard', 'Profile'])}
              disabled={loading}
              variant="outline"
              className="h-20 flex flex-col items-center justify-center"
            >
              <span className="text-2xl mb-1">📱</span>
              <span>Mobile App</span>
            </Button>
            <Button 
              onClick={() => handleGenerateDesign('dashboard', ['Overview', 'Analytics', 'Settings'])}
              disabled={loading}
              variant="outline"
              className="h-20 flex flex-col items-center justify-center"
            >
              <span className="text-2xl mb-1">📊</span>
              <span>Dashboard</span>
            </Button>
          </div>
          
          {loading && (
            <div className="mt-4 flex items-center justify-center">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600"></div>
              <span className="ml-2 text-sm text-gray-600">Generating design...</span>
            </div>
          )}
          
          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Design Results */}
      {designs.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Generated Designs ({designs.length})</CardTitle>
            <CardDescription>
              Click on a design to view wireframes and Figma links
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              {designs.map((design, index) => (
                <Card 
                  key={index}
                  className={`cursor-pointer transition-all hover:shadow-md ${
                    selectedDesign === design ? 'ring-2 ring-green-500' : ''
                  }`}
                  onClick={() => setSelectedDesign(design)}
                >
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <Badge variant="secondary">
                        {design.project_type}
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        {design.wireframes.length} pages
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="text-sm text-gray-600 mb-2">
                      Theme: {design.style_guide.theme}
                    </div>
                    <div className="flex items-center gap-2">
                      <div 
                        className="w-4 h-4 rounded"
                        style={{ backgroundColor: design.style_guide.primary_color }}
                      ></div>
                      <div 
                        className="w-4 h-4 rounded"
                        style={{ backgroundColor: design.style_guide.secondary_color }}
                      ></div>
                      <div 
                        className="w-4 h-4 rounded"
                        style={{ backgroundColor: design.style_guide.accent_color }}
                      ></div>
                    </div>
                    {design.figma_project_url && (
                      <Button 
                        size="sm" 
                        variant="outline" 
                        className="mt-3 w-full text-xs"
                        onClick={(e) => {
                          e.stopPropagation()
                          window.open(design.figma_project_url, '_blank')
                        }}
                      >
                        Open Figma Project
                      </Button>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Selected Design Details */}
            {selectedDesign && (
              <Tabs defaultValue="wireframes" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="wireframes">Wireframes</TabsTrigger>
                  <TabsTrigger value="style-guide">Style Guide</TabsTrigger>
                  <TabsTrigger value="details">Details</TabsTrigger>
                </TabsList>
                
                <TabsContent value="wireframes" className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {selectedDesign.wireframes.map((wireframe, index) => (
                      <div key={index} className="space-y-2">
                        <h4 className="font-medium">{wireframe.page_name}</h4>
                        {renderWireframe(wireframe)}
                      </div>
                    ))}
                  </div>
                </TabsContent>
                
                <TabsContent value="style-guide" className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium mb-3">Color Palette</h4>
                      <div className="space-y-2">
                        <div className="flex items-center gap-3">
                          <div 
                            className="w-8 h-8 rounded"
                            style={{ backgroundColor: selectedDesign.style_guide.primary_color }}
                          ></div>
                          <div>
                            <div className="font-medium">Primary</div>
                            <div className="text-sm text-gray-600">
                              {selectedDesign.style_guide.primary_color}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <div 
                            className="w-8 h-8 rounded"
                            style={{ backgroundColor: selectedDesign.style_guide.secondary_color }}
                          ></div>
                          <div>
                            <div className="font-medium">Secondary</div>
                            <div className="text-sm text-gray-600">
                              {selectedDesign.style_guide.secondary_color}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <div 
                            className="w-8 h-8 rounded"
                            style={{ backgroundColor: selectedDesign.style_guide.accent_color }}
                          ></div>
                          <div>
                            <div className="font-medium">Accent</div>
                            <div className="text-sm text-gray-600">
                              {selectedDesign.style_guide.accent_color}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium mb-3">Glassmorphism Properties</h4>
                      <div className="space-y-2 text-sm">
                        <div>
                          <strong>Backdrop Filter:</strong><br />
                          <code className="text-xs bg-gray-100 px-1 py-0.5 rounded">
                            {selectedDesign.style_guide.glassmorphism_properties.backdrop_filter}
                          </code>
                        </div>
                        <div>
                          <strong>Border Radius:</strong><br />
                          <code className="text-xs bg-gray-100 px-1 py-0.5 rounded">
                            {selectedDesign.style_guide.glassmorphism_properties.border_radius}
                          </code>
                        </div>
                        <div>
                          <strong>Box Shadow:</strong><br />
                          <code className="text-xs bg-gray-100 px-1 py-0.5 rounded">
                            {selectedDesign.style_guide.glassmorphism_properties.box_shadow}
                          </code>
                        </div>
                      </div>
                    </div>
                  </div>
                </TabsContent>
                
                <TabsContent value="details" className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium mb-3">Project Details</h4>
                      <div className="space-y-2 text-sm">
                        <div><strong>Type:</strong> {selectedDesign.project_type}</div>
                        <div><strong>Pages:</strong> {selectedDesign.wireframes.length}</div>
                        <div><strong>Dev Time:</strong> {selectedDesign.estimated_dev_time}</div>
                        <div><strong>Theme:</strong> {selectedDesign.style_guide.theme}</div>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium mb-3">Design System</h4>
                      <div className="space-y-2 text-sm">
                        <div>
                          <strong>Components:</strong><br />
                          <div className="flex flex-wrap gap-1 mt-1">
                            {selectedDesign.design_system.components.map((comp, i) => (
                              <Badge key={i} variant="outline" className="text-xs">
                                {comp}
                              </Badge>
                            ))}
                          </div>
                        </div>
                        <div>
                          <strong>Responsive Breakpoints:</strong><br />
                          <code className="text-xs bg-gray-100 px-1 py-0.5 rounded">
                            Mobile: {selectedDesign.design_system.responsive_breakpoints.mobile}
                          </code>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-medium mb-2">Design Reasoning</h4>
                    <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                      {selectedDesign.reasoning}
                    </p>
                  </div>
                </TabsContent>
              </Tabs>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
} 