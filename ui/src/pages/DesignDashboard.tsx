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
    <div className="min-h-screen bg-gradient-to-br from-stone-50 via-stone-100 to-stone-200 p-4">
      {/* Glassmorphism background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-20 w-96 h-96 bg-gradient-to-br from-emerald-300/20 to-teal-400/20 rounded-full blur-3xl"></div>
        <div className="absolute top-40 right-32 w-80 h-80 bg-gradient-to-br from-green-300/20 to-emerald-400/20 rounded-full blur-3xl"></div>
        <div className="absolute bottom-32 left-1/3 w-64 h-64 bg-gradient-to-br from-teal-300/20 to-green-400/20 rounded-full blur-3xl"></div>
      </div>

      <div className="max-w-7xl mx-auto relative">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-stone-900 mb-2">
                🎨 Design Studio
              </h1>
              <p className="text-stone-600 text-lg">
                AI-powered wireframe and design generation with glassmorphism theme
              </p>
            </div>
            <Badge variant="outline" className="text-sm glass-card border-stone-200">
              Powered by DesignAgent
            </Badge>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="glass-card border-stone-200/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-stone-600">
                Design Theme
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded bg-gradient-to-r from-emerald-400 to-teal-500"></div>
                <span className="text-lg font-semibold text-stone-900">Glassmorphism</span>
              </div>
              <p className="text-xs text-stone-500 mt-1">Natural stone palette with green accents</p>
            </CardContent>
          </Card>

          <Card className="glass-card border-stone-200/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-stone-600">
                Supported Platforms
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-emerald-600">3</div>
              <p className="text-xs text-stone-500">Web, Mobile, Dashboard</p>
            </CardContent>
          </Card>

          <Card className="glass-card border-stone-200/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-stone-600">
                Figma Integration
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
                <span className="text-sm font-medium text-stone-900">Active</span>
              </div>
              <p className="text-xs text-stone-500 mt-1">Auto-export to Figma</p>
            </CardContent>
          </Card>

          <Card className="glass-card border-stone-200/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-stone-600">
                Design System
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm font-medium text-stone-900">Components Ready</div>
              <p className="text-xs text-stone-500">Button, Card, Modal, Nav+</p>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity */}
        {recentActivity.length > 0 && (
          <Card className="mb-8 glass-card border-stone-200/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-stone-900">
                📋 Recent Design Activity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {recentActivity.map((activity, index) => (
                  <div key={index} className="flex items-center gap-3 p-2 bg-stone-100/40 rounded-lg backdrop-blur-sm">
                    <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
                    <span className="text-sm text-stone-700">{activity}</span>
                    <Badge variant="outline" className="ml-auto text-xs border-stone-200">
                      {index === 0 ? 'Just now' : `${index + 1}m ago`}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Main Design Interface */}
        <div className="glass-card border-stone-200/50 p-6">
          <FigmaPreview onGenerateDesign={handleDesignGenerated} />
        </div>

        {/* Footer Info */}
        <div className="mt-8 text-center">
          <Card className="glass-card border-stone-200/50">
            <CardContent className="p-4">
              <div className="flex items-center justify-center gap-6 text-sm text-stone-600">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
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