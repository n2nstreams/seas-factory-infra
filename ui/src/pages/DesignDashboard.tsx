import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import FigmaPreview from '@/components/FigmaPreview';
import { 
  Settings
} from 'lucide-react';

export default function DesignDashboard() {
  const [recentActivity, setRecentActivity] = useState<string[]>([])

  const handleDesignGenerated = (projectType: string, pages: string[]) => {
    const activity = `Generated ${projectType} design with ${pages.length} pages: ${pages.join(', ')}`
    setRecentActivity(prev => [activity, ...prev.slice(0, 4)]) // Keep last 5 activities
  }

  return (
    <div className="min-h-screen bg-homepage relative overflow-hidden">
      {/* Glassmorphism Background Elements */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-20 left-20 w-96 h-96 bg-gradient-to-br from-green-800/20 to-green-900/25 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-40 right-32 w-80 h-80 bg-gradient-to-bl from-slate-700/20 to-green-800/25 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute bottom-20 left-1/3 w-64 h-64 bg-gradient-to-tr from-stone-600/20 to-green-700/25 rounded-full blur-3xl animate-pulse delay-2000"></div>
        <div className="absolute bottom-32 right-20 w-72 h-72 bg-gradient-to-tl from-green-800/20 to-stone-700/25 rounded-full blur-3xl animate-pulse delay-3000"></div>
      </div>

      <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16 py-8 relative z-10">
        <div className="space-y-8">
        {/* Header */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl xl:text-4xl font-bold text-heading mb-3">
                🎨 Design Studio
              </h1>
              <p className="text-body text-lg xl:text-xl">
                AI-powered wireframe and design generation with glassmorphism theme
              </p>
            </div>
            <Badge className="bg-green-800/20 backdrop-blur-sm text-green-800 border border-green-800/40 shadow-lg text-sm">
              Powered by DesignAgent
            </Badge>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
          <Card className="card-glass">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-body">
                Design Theme
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded bg-gradient-to-r from-green-800 to-green-900 shadow-lg"></div>
                <span className="text-lg font-semibold text-heading">Glassmorphism</span>
              </div>
              <p className="text-xs text-muted mt-1">Natural stone palette with green accents</p>
            </CardContent>
          </Card>

          <Card className="card-glass">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-body">
                Supported Platforms
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-800">3</div>
              <p className="text-xs text-muted">Web, Mobile, Dashboard</p>
            </CardContent>
          </Card>

          <Card className="card-glass">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-body">
                Figma Integration
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-green-800 shadow-lg"></div>
                <span className="text-sm font-medium text-heading">Active</span>
              </div>
              <p className="text-xs text-muted mt-1">Auto-export to Figma</p>
            </CardContent>
          </Card>

          <Card className="card-glass">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-body">
                Design System
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm font-medium text-heading">Components Ready</div>
              <p className="text-xs text-muted">Button, Card, Modal, Nav+</p>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity */}
        {recentActivity.length > 0 && (
          <Card className="card-glass">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-heading">
                📋 Recent Design Activity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {recentActivity.map((activity, index) => (
                  <div key={index} className="flex items-center gap-3 p-3 glass-card">
                    <div className="w-2 h-2 rounded-full bg-green-800 shadow-lg"></div>
                    <span className="text-sm text-body">{activity}</span>
                    <Badge className="ml-auto text-xs bg-green-800/20 text-green-800 border border-green-800/40">
                      {index === 0 ? 'Just now' : `${index + 1}m ago`}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Main Design Interface */}
        <div className="space-y-6">
          <div className="card-glass p-6">
            <FigmaPreview onGenerateDesign={handleDesignGenerated} />
          </div>
        </div>

        {/* Theme Settings */}
        <div className="space-y-6">
          <Card className="card-glass">
            <CardHeader>
              <CardTitle className="text-heading flex items-center">
                <Settings className="w-5 h-5 mr-2 text-green-800" />
                Theme Settings
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-body">Glass Effect Intensity</span>
                  <div className="w-32 h-2 bg-stone-300/60 rounded-full">
                    <div className="w-3/4 h-2 bg-gradient-to-r from-green-800 to-green-900 rounded-full"></div>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-body">Blur Radius</span>
                  <div className="w-32 h-2 bg-stone-300/60 rounded-full">
                    <div className="w-1/2 h-2 bg-gradient-to-r from-green-800 to-green-900 rounded-full"></div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-green-800 shadow-lg"></div>
                  <span className="text-body">Glassmorphism Theme Active</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
      </div>

      {/* Footer */}
      <footer className="bg-stone-900/95 backdrop-blur-lg text-white py-12 border-t border-stone-400/30 mt-16">
        <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <div className="w-10 h-10 bg-gradient-to-r from-green-800 to-green-900 rounded-xl flex items-center justify-center shadow-lg">
                  <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 1H9V3H7V1H5V7L1 9V11L7 13V21H9V19H11V21H13V19H15V21H17V13L23 11V9H21ZM19 10.5L17 11.5V17H15V15H13V17H11V15H9V17H7V11.5L5 10.5V9.5L7 8.5V7H9V9H11V7H13V9H15V7H17V8.5L19 9.5V10.5Z"/>
                  </svg>
                </div>
                <span className="text-xl font-bold">Forge95</span>
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
            <p>&copy; 2025 Forge95. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
} 