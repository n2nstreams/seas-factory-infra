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
  Activity
} from 'lucide-react'
import Link from 'next/link'

export default function AdminDashboard() {
  const adminModules = [
    {
      name: 'Feature Flags',
      description: 'Manage feature flags and A/B testing configurations',
      icon: Flag,
      href: '/app2/admin/feature-flags',
      status: 'active',
      color: 'bg-blue-500'
    },
    {
      name: 'Database Migration',
      description: 'Monitor and manage database schema migrations',
      icon: Database,
      href: '/app2/admin/database-migration',
      status: 'active',
      color: 'bg-green-500'
    },
    {
      name: 'ETL Management',
      description: 'Data pipeline and ETL job management',
      icon: BarChart3,
      href: '/app2/admin/etl-management',
      status: 'active',
      color: 'bg-purple-500'
    },
    {
      name: 'AI Workloads',
      description: 'Monitor AI model performance and workloads',
      icon: Brain,
      href: '/app2/admin/ai-workloads',
      status: 'active',
      color: 'bg-orange-500'
    },
    {
      name: 'AI Agents',
      description: 'Manage AI agents and orchestrator workflows',
      icon: Brain,
      href: '/app2/admin/ai-agents',
      status: 'active',
      color: 'bg-emerald-500'
    },
    {
      name: 'Email System',
      description: 'Email service configuration and monitoring',
      icon: Mail,
      href: '/app2/admin/email-system',
      status: 'active',
      color: 'bg-red-500'
    },
    {
      name: 'Final Data Migration',
      description: 'Production data migration tools',
      icon: Database,
      href: '/app2/admin/final-data-migration',
      status: 'active',
      color: 'bg-indigo-500'
    }
  ]

  const systemStats = {
    totalUsers: 1250,
    activeUsers: 892,
    systemHealth: 98,
    uptime: '99.9%',
    lastBackup: '2 hours ago',
    pendingMigrations: 0
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="text-gray-600 mt-1">System administration and management tools</p>
        </div>
        
        <div className="flex items-center gap-3">
          <Button variant="outline" className="flex items-center gap-2">
            <Settings className="w-4 h-4" />
            System Settings
          </Button>
          <Button className="flex items-center gap-2">
            <Shield className="w-4 h-4" />
            Security Audit
          </Button>
        </div>
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{systemStats.totalUsers}</div>
            <p className="text-xs text-gray-500 mt-1">
              {systemStats.activeUsers} active
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">System Health</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{systemStats.systemHealth}%</div>
            <p className="text-xs text-gray-500 mt-1">
              Uptime: {systemStats.uptime}
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Last Backup</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{systemStats.lastBackup}</div>
            <p className="text-xs text-gray-500 mt-1">
              Automated backup system
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Pending Migrations</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{systemStats.pendingMigrations}</div>
            <p className="text-xs text-gray-500 mt-1">
              Database schema updates
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Admin Modules */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Administration Modules
          </CardTitle>
          <CardDescription>
            Access various system administration tools and configurations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {adminModules.map((module) => {
              const Icon = module.icon
              return (
                <Link key={module.name} href={module.href}>
                  <Card className="hover:shadow-md transition-shadow cursor-pointer">
                    <CardHeader className="pb-3">
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${module.color}`}>
                          <Icon className="w-5 h-5 text-white" />
                        </div>
                        <div>
                          <CardTitle className="text-lg">{module.name}</CardTitle>
                          <CardDescription className="text-sm">
                            {module.description}
                          </CardDescription>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="flex items-center justify-between">
                        <Badge variant="secondary" className="bg-green-100 text-green-800">
                          {module.status}
                        </Badge>
                        <Button variant="ghost" size="sm">
                          Access
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Common administrative tasks
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Button variant="outline" className="flex items-center gap-2">
              <Users className="w-4 h-4" />
              User Management
            </Button>
            <Button variant="outline" className="flex items-center gap-2">
              <Activity className="w-4 h-4" />
              System Logs
            </Button>
            <Button variant="outline" className="flex items-center gap-2">
              <Database className="w-4 h-4" />
              Database Status
            </Button>
            <Button variant="outline" className="flex items-center gap-2">
              <Shield className="w-4 h-4" />
              Security Settings
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Footer */}
      <div className="text-center text-sm text-gray-500">
        <p>Admin Dashboard - AI SaaS Factory</p>
        <p>Last updated: {new Date().toLocaleString()}</p>
      </div>
    </div>
  )
}
