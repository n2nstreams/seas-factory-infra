import { useState } from 'react'
import FigmaPreview from '../components/FigmaPreview'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'

export default function DesignDashboard() {
  const [recentActivity, setRecentActivity] = useState<string[]>([])

  const handleDesignGenerated = (projectType: string, pages: string[]) => {
    const activity = `Generated ${projectType} design with ${pages.length} pages: ${pages.join(', ')}`
    setRecentActivity(prev => [activity, ...prev.slice(0, 4)]) // Keep last 5 activities
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                🎨 Design Studio
              </h1>
              <p className="text-gray-600 text-lg">
                AI-powered wireframe and design generation with glassmorphism theme
              </p>
            </div>
            <Badge variant="outline" className="text-sm bg-white/80 backdrop-blur-sm">
              Powered by DesignAgent
            </Badge>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-white/60 backdrop-blur-sm border-green-200">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Design Theme
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded bg-gradient-to-r from-green-400 to-green-600"></div>
                <span className="text-lg font-semibold">Glassmorphism</span>
              </div>
              <p className="text-xs text-gray-500 mt-1">Natural olive green palette</p>
            </CardContent>
          </Card>

          <Card className="bg-white/60 backdrop-blur-sm border-green-200">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Supported Platforms
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-700">3</div>
              <p className="text-xs text-gray-500">Web, Mobile, Dashboard</p>
            </CardContent>
          </Card>

          <Card className="bg-white/60 backdrop-blur-sm border-green-200">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Figma Integration
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
                <span className="text-sm font-medium">Active</span>
              </div>
              <p className="text-xs text-gray-500 mt-1">Auto-export to Figma</p>
            </CardContent>
          </Card>

          <Card className="bg-white/60 backdrop-blur-sm border-green-200">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Design System
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm font-medium">Components Ready</div>
              <p className="text-xs text-gray-500">Button, Card, Modal, Nav+</p>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity */}
        {recentActivity.length > 0 && (
          <Card className="mb-8 bg-white/60 backdrop-blur-sm border-green-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                📋 Recent Design Activity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {recentActivity.map((activity, index) => (
                  <div key={index} className="flex items-center gap-3 p-2 bg-white/40 rounded-lg">
                    <div className="w-2 h-2 rounded-full bg-green-500"></div>
                    <span className="text-sm text-gray-700">{activity}</span>
                    <Badge variant="outline" className="ml-auto text-xs">
                      {index === 0 ? 'Just now' : `${index + 1}m ago`}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Main Design Interface */}
        <div className="bg-white/40 backdrop-blur-sm rounded-2xl border border-green-200 p-6">
          <FigmaPreview onGenerateDesign={handleDesignGenerated} />
        </div>

        {/* Footer Info */}
        <div className="mt-8 text-center">
          <Card className="bg-white/60 backdrop-blur-sm border-green-200">
            <CardContent className="p-4">
              <div className="flex items-center justify-center gap-6 text-sm text-gray-600">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-green-500"></div>
                  <span>DesignAgent Online</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                  <span>Figma API Connected</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-purple-500"></div>
                  <span>Glassmorphism Theme Active</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
} 