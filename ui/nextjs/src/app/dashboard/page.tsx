'use client'

import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Settings, 
  Database, 
  Mail, 
  Flag, 
  Brain, 
  BarChart3,
  Shield,
  Users,
  Activity,
  Code,
  Palette,
  TestTube
} from 'lucide-react'
import Link from 'next/link'

export default function DashboardPage() {
  const dashboardModules = [
    {
      name: 'AI Agents',
      description: 'Manage and interact with AI agents',
      icon: Brain,
      href: '/dashboard/agents',
      status: 'active',
      color: 'bg-emerald-500'
    },
    {
      name: 'Code Generation',
      description: 'Generate code using AI agents',
      icon: Code,
      href: '/dashboard/code-generation',
      status: 'active',
      color: 'bg-blue-500'
    },
    {
      name: 'Design System',
      description: 'UI/UX design and prototyping',
      icon: Palette,
      href: '/dashboard/design',
      status: 'active',
      color: 'bg-purple-500'
    },
    {
      name: 'Testing & QA',
      description: 'Automated testing and quality assurance',
      icon: TestTube,
      href: '/dashboard/testing',
      status: 'active',
      color: 'bg-orange-500'
    },
    {
      name: 'Analytics',
      description: 'Performance metrics and insights',
      icon: BarChart3,
      href: '/dashboard/analytics',
      status: 'active',
      color: 'bg-indigo-500'
    },
    {
      name: 'Settings',
      description: 'Application configuration',
      icon: Settings,
      href: '/dashboard/settings',
      status: 'active',
      color: 'bg-gray-500'
    }
  ]

  const systemStats = {
    totalUsers: 1250,
    activeAgents: 8,
    codeGenerations: 156,
    designPrototypes: 89
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-primary-900 mb-2">
            AI SaaS Factory Dashboard
          </h1>
          <p className="text-lg text-primary-700">
            Welcome to your AI-powered development workspace
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="glass-card">
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-blue-100 rounded-lg">
                  <Users className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-primary-600">Total Users</p>
                  <p className="text-2xl font-bold text-primary-900">{systemStats.totalUsers}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-card">
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-emerald-100 rounded-lg">
                  <Brain className="h-6 w-6 text-emerald-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-primary-600">Active Agents</p>
                  <p className="text-2xl font-bold text-primary-900">{systemStats.activeAgents}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-card">
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-purple-100 rounded-lg">
                  <Code className="h-6 w-6 text-purple-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-primary-600">Code Generations</p>
                  <p className="text-2xl font-bold text-primary-900">{systemStats.codeGenerations}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-card">
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-orange-100 rounded-lg">
                  <Palette className="h-6 w-6 text-orange-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-primary-600">Design Prototypes</p>
                  <p className="text-2xl font-bold text-primary-900">{systemStats.designPrototypes}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Module Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {dashboardModules.map((module) => (
            <Card key={module.name} className="glass-card hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${module.color}`}>
                    <module.icon className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-lg text-primary-900">{module.name}</CardTitle>
                    <CardDescription className="text-primary-600">
                      {module.description}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <Badge variant="secondary" className="bg-green-100 text-green-800">
                    {module.status}
                  </Badge>
                  <Button asChild size="sm" variant="outline">
                    <Link href={module.href}>
                      Open
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
