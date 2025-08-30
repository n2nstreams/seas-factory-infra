'use client'

import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Brain, 
  Code, 
  Palette, 
  TestTube, 
  Settings, 
  Activity,
  Play,
  Pause,
  Square,
  BarChart3
} from 'lucide-react'
import Link from 'next/link'

export default function AgentsPage() {
  const agents = [
    {
      id: 'dev-agent',
      name: 'DevAgent',
      description: 'AI-powered code generation and development assistance',
      icon: Code,
      status: 'active',
      type: 'Code Generation',
      lastActivity: '2 minutes ago',
      performance: '98%',
      color: 'bg-blue-500'
    },
    {
      id: 'design-agent',
      name: 'DesignAgent',
      description: 'UI/UX design generation and prototyping',
      icon: Palette,
      status: 'active',
      type: 'Design',
      lastActivity: '5 minutes ago',
      performance: '95%',
      color: 'bg-purple-500'
    },
    {
      id: 'qa-agent',
      name: 'QAAgent',
      description: 'Automated testing and quality assurance',
      icon: TestTube,
      status: 'idle',
      type: 'Testing',
      lastActivity: '1 hour ago',
      performance: '92%',
      color: 'bg-orange-500'
    },
    {
      id: 'ops-agent',
      name: 'OpsAgent',
      description: 'DevOps and infrastructure management',
      icon: Settings,
      status: 'active',
      type: 'Operations',
      lastActivity: '10 minutes ago',
      performance: '96%',
      color: 'bg-green-500'
    }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'idle':
        return 'bg-yellow-100 text-yellow-800'
      case 'error':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <Play className="h-4 w-4" />
      case 'idle':
        return <Pause className="h-4 w-4" />
      case 'error':
        return <Square className="h-4 w-4" />
      default:
        return <Activity className="h-4 w-4" />
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-primary-900 mb-2">
            AI Agents Dashboard
          </h1>
          <p className="text-lg text-primary-700">
            Manage and monitor your AI-powered development agents
          </p>
        </div>

        {/* Agent Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {agents.map((agent) => (
            <Card key={agent.id} className="glass-card hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center space-x-3">
                  <div className={`p-3 rounded-lg ${agent.color}`}>
                    <agent.icon className="h-6 w-6 text-white" />
                  </div>
                  <div className="flex-1">
                    <CardTitle className="text-xl text-primary-900">{agent.name}</CardTitle>
                    <CardDescription className="text-primary-600">
                      {agent.description}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Status and Type */}
                <div className="flex items-center justify-between">
                  <Badge variant="secondary" className={getStatusColor(agent.status)}>
                    <div className="flex items-center space-x-1">
                      {getStatusIcon(agent.status)}
                      <span>{agent.status}</span>
                    </div>
                  </Badge>
                  <Badge variant="outline" className="text-primary-600">
                    {agent.type}
                  </Badge>
                </div>

                {/* Performance and Activity */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-primary-600">Performance</p>
                    <p className="font-semibold text-primary-900">{agent.performance}</p>
                  </div>
                  <div>
                    <p className="text-primary-600">Last Activity</p>
                    <p className="font-semibold text-primary-900">{agent.lastActivity}</p>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex space-x-2">
                  <Button asChild size="sm" className="flex-1">
                    <Link href={`/dashboard/agents/${agent.id}`}>
                      Manage
                    </Link>
                  </Button>
                  <Button size="sm" variant="outline">
                    <Activity className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Quick Actions */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="text-xl text-primary-900">Quick Actions</CardTitle>
            <CardDescription>
              Common tasks and agent management operations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-4">
              <Button asChild>
                <Link href="/dashboard/agents/new">
                  <Brain className="h-4 w-4 mr-2" />
                  Create New Agent
                </Link>
              </Button>
              <Button variant="outline">
                <Activity className="h-4 w-4 mr-2" />
                View All Logs
              </Button>
              <Button variant="outline">
                <Settings className="h-4 w-4 mr-2" />
                Agent Settings
              </Button>
              <Button variant="outline">
                <BarChart3 className="h-4 w-4 mr-2" />
                Performance Report
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
