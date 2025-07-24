import React, { useState, useEffect } from 'react';
import FigmaPreview from '../components/FigmaPreview'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { 
  Palette, 
  Download, 
  RefreshCw, 
  Eye, 
  Settings,
  Layers,
  Grid,
  Sparkles,
  Code2
} from 'lucide-react';

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

        <div className="space-y-6">
          <Card className="card-glass">
            <CardHeader>
              <CardTitle className="text-heading flex items-center">
                <Settings className="w-5 h-5 mr-2" />
                Theme Settings
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-body">Glass Effect Intensity</span>
                  <div className="w-32 h-2 bg-stone-200 rounded-full">
                    <div className="w-3/4 h-2 bg-accent rounded-full"></div>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-body">Blur Radius</span>
                  <div className="w-32 h-2 bg-stone-200 rounded-full">
                    <div className="w-1/2 h-2 bg-accent rounded-full"></div>
                  </div>
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

      {/* Footer */}
      <footer className="bg-stone-900/95 backdrop-blur-lg text-white py-12 border-t border-stone-400/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <div className="w-10 h-10 bg-gradient-to-r from-green-800 to-green-900 rounded-xl flex items-center justify-center shadow-lg">
                  <Code2 className="w-6 h-6 text-white" />
                </div>
                <span className="text-xl font-bold">AI SaaS Factory</span>
              </div>
              <p className="text-stone-300">
                Turn any idea into a live SaaS business - no code required.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-stone-200">Product</h4>
              <div className="space-y-2 text-stone-400">
                <a href="/" className="block hover:text-white transition-colors">Features</a>
                <a href="/pricing" className="block hover:text-white transition-colors">Pricing</a>
                <a href="/dashboard" className="block hover:text-white transition-colors">Dashboard</a>
              </div>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-stone-200">Company</h4>
              <div className="space-y-2 text-stone-400">
                <a href="#" className="block hover:text-white transition-colors">About</a>
                <a href="#" className="block hover:text-white transition-colors">Blog</a>
                <a href="#" className="block hover:text-white transition-colors">Contact</a>
              </div>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-stone-200">Support</h4>
              <div className="space-y-2 text-stone-400">
                <a href="#" className="block hover:text-white transition-colors">Documentation</a>
                <a href="#" className="block hover:text-white transition-colors">Community</a>
                <a href="#" className="block hover:text-white transition-colors">Help Center</a>
              </div>
            </div>
          </div>
          <div className="border-t border-stone-700/50 mt-8 pt-8 text-center text-stone-300">
            <p>&copy; 2024 AI SaaS Factory. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
} 