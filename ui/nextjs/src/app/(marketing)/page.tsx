'use client'

import React from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Brain, 
  Code, 
  Palette, 
  TestTube, 
  Zap, 
  Shield,
  Users,
  ArrowRight,
  Star
} from 'lucide-react'
import Link from 'next/link'

export default function LandingPage() {
  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Development',
      description: 'Intelligent agents that understand your requirements and generate production-ready code.'
    },
    {
      icon: Code,
      title: 'Code Generation',
      description: 'Automated code generation for multiple languages and frameworks with best practices.'
    },
    {
      icon: Palette,
      title: 'Design System',
      description: 'AI-generated UI/UX designs with glassmorphism aesthetics and responsive layouts.'
    },
    {
      icon: TestTube,
      title: 'Quality Assurance',
      description: 'Automated testing and validation to ensure code quality and reliability.'
    },
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Optimized performance with Next.js 15, Server Components, and modern React patterns.'
    },
    {
      icon: Shield,
      title: 'Enterprise Security',
      description: 'Built-in authentication, authorization, and data isolation for multi-tenant applications.'
    }
  ]

  const testimonials = [
    {
      name: 'Sarah Chen',
      role: 'Senior Developer',
      company: 'TechCorp',
      content: 'AI SaaS Factory reduced our development time by 70%. The AI agents are incredibly intelligent!',
      rating: 5
    },
    {
      name: 'Marcus Rodriguez',
      role: 'CTO',
      company: 'StartupXYZ',
      content: 'We went from idea to MVP in 2 weeks. This platform is a game-changer for rapid development.',
      rating: 5
    },
    {
      name: 'Emily Watson',
      role: 'Product Manager',
      company: 'InnovateLab',
      content: 'The design system is beautiful and the code quality is production-ready. Highly recommended!',
      rating: 5
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100">
      {/* Header */}
      <header className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-primary-600/20 to-primary-800/20"></div>
        <div className="relative max-w-7xl mx-auto px-6 py-16">
          <div className="text-center">
            <Badge variant="secondary" className="mb-4 bg-primary-100 text-primary-800">
              🚀 Next.js 15 + AI Agents
            </Badge>
            <h1 className="text-5xl md:text-6xl font-bold text-primary-900 mb-6">
              AI SaaS Factory
            </h1>
            <p className="text-xl md:text-2xl text-primary-700 mb-8 max-w-3xl mx-auto">
              Transform your ideas into fully-deployed SaaS applications with AI-powered development agents
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button asChild size="lg" className="bg-primary-600 hover:bg-primary-700">
                <Link href="/dashboard">
                  Get Started
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button asChild size="lg" variant="outline" className="border-primary-300 text-primary-700 hover:bg-primary-50">
                <Link href="/dashboard/agents">
                  View AI Agents
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Features */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-primary-900 mb-4">
              Powered by AI, Built for Developers
            </h2>
            <p className="text-xl text-primary-700 max-w-2xl mx-auto">
              Our AI agents work together to handle every aspect of SaaS development, from concept to deployment.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="glass-card hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
                <CardHeader className="text-center">
                  <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <feature.icon className="h-8 w-8 text-primary-600" />
                  </div>
                  <CardTitle className="text-xl text-primary-900">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-primary-600 text-center">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 px-6 bg-white/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-primary-900 mb-4">
              Trusted by Developers Worldwide
            </h2>
            <p className="text-xl text-primary-700">
              See what our users are saying about AI SaaS Factory
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="glass-card">
                <CardContent className="p-6">
                  <div className="flex items-center mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  <p className="text-primary-700 mb-4 italic">"{testimonial.content}"</p>
                  <div>
                    <p className="font-semibold text-primary-900">{testimonial.name}</p>
                    <p className="text-sm text-primary-600">{testimonial.role} at {testimonial.company}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-primary-900 mb-6">
            Ready to Build the Future?
          </h2>
          <p className="text-xl text-primary-700 mb-8">
            Join thousands of developers who are already using AI SaaS Factory to build amazing applications.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" className="bg-primary-600 hover:bg-primary-700">
              <Link href="/dashboard">
                Start Building Now
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="border-primary-300 text-primary-700 hover:bg-primary-50">
              <Link href="/dashboard/agents">
                Explore AI Agents
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-primary-900 text-white py-12 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <h3 className="text-2xl font-bold mb-4">AI SaaS Factory</h3>
          <p className="text-primary-300 mb-6">
            Modern, Clean Architecture for AI-Powered SaaS Applications
          </p>
          <div className="flex justify-center space-x-6 text-primary-300">
            <Link href="/dashboard" className="hover:text-white transition-colors">Dashboard</Link>
            <Link href="/dashboard/agents" className="hover:text-white transition-colors">AI Agents</Link>
            <Link href="/dashboard/settings" className="hover:text-white transition-colors">Settings</Link>
          </div>
          <div className="mt-8 pt-8 border-t border-primary-800 text-primary-400">
            <p>&copy; 2025 AI SaaS Factory. Built with Next.js 15 and AI agents.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
