'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useAuth } from '@/components/providers/AuthProvider'
import { useFeatureFlag } from '@/components/providers/FeatureFlagProvider'
import { cn } from '@/lib/utils'

interface NavigationProps {
  className?: string
}

export default function Navigation({ className }: NavigationProps) {
  const { user, logout } = useAuth()
  const uiShellV2 = useFeatureFlag('ui_shell_v2')
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  const navigationItems = [
    { name: 'Dashboard', href: '/app2/dashboard', protected: true },
    { name: 'Projects', href: '/app2/projects', protected: true },
    { name: 'Jobs', href: '/app2/jobs', protected: true },
    { name: 'Performance', href: '/app2/performance', protected: true },
    { name: 'Marketplace', href: '/app2/marketplace', protected: false },
    { name: 'Pricing', href: '/app2/pricing', protected: false },
    { name: 'Support', href: '/app2/support', protected: false },
  ]

  const adminItems = [
    { name: 'Feature Flags', href: '/app2/admin/feature-flags', protected: true, adminOnly: true },
    { name: 'Email System', href: '/app2/admin/email-system', protected: true, adminOnly: true },
  ]

  const handleLogout = () => {
    logout()
  }

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen)
  }

  return (
    <nav className={cn('glass-dark sticky top-0 z-50 backdrop-blur-md', className)}>
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/app2" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
              </svg>
            </div>
            <span className="text-xl font-bold text-primary-800">AI SaaS Factory</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navigationItems.map((item) => {
              if (item.protected && !user) return null
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className="text-primary-700 hover:text-primary-900 transition-colors duration-200 font-medium"
                >
                  {item.name}
                </Link>
              )
            })}
          </div>

          {/* User Menu / Auth Buttons */}
          <div className="hidden md:flex items-center space-x-4">
            {user ? (
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <p className="text-sm font-medium text-primary-800">{user.name}</p>
                  <p className="text-xs text-primary-600">{user.plan} plan</p>
                </div>
                <div className="relative group">
                  <button 
                    className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center text-primary-700 hover:bg-primary-200 transition-colors"
                    aria-label="User menu"
                    aria-expanded="false"
                    aria-haspopup="true"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </button>
                  
                  {/* Dropdown Menu */}
                  <div className="absolute right-0 mt-2 w-48 glass-card opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                    <div className="py-2">
                      <Link
                        href="/app2/profile"
                        className="block px-4 py-2 text-sm text-primary-700 hover:bg-primary-50 rounded transition-colors"
                      >
                        Profile
                      </Link>
                      <Link
                        href="/app2/settings"
                        className="block px-4 py-2 text-sm text-primary-700 hover:bg-primary-50 rounded transition-colors"
                      >
                        Settings
                      </Link>
                      <Link
                        href="/app2/billing"
                        className="block px-4 py-2 text-sm text-primary-700 hover:bg-primary-50 rounded transition-colors"
                      >
                        Billing
                      </Link>
                      {user?.plan === 'growth' && (
                        <>
                          <hr className="my-2 border-primary-200" />
                          <div className="px-4 py-2">
                            <p className="text-xs font-medium text-primary-600 uppercase tracking-wide">Admin</p>
                          </div>
                          <Link
                            href="/app2/admin/feature-flags"
                            className="block px-4 py-2 text-sm text-primary-700 hover:bg-primary-50 rounded transition-colors"
                          >
                            Feature Flags
                          </Link>
                          <Link
                            href="/app2/admin/database-migration"
                            className="block px-4 py-2 text-sm text-primary-700 hover:bg-primary-50 rounded transition-colors"
                          >
                            Database Migration
                          </Link>
                          <Link
                            href="/app2/admin/etl-management"
                            className="block px-4 py-2 text-sm text-primary-700 hover:bg-primary-50 rounded transition-colors"
                          >
                            ETL Management
                          </Link>
                          <Link
                            href="/app2/admin/email-system"
                            className="block px-4 py-2 text-sm text-primary-700 hover:bg-primary-50 rounded transition-colors"
                          >
                            Email System
                          </Link>
                          <Link
                            href="/app2/admin/final-data-migration"
                            className="block px-4 py-2 text-sm text-primary-700 hover:bg-primary-50 rounded transition-colors"
                          >
                            Final Data Migration
                          </Link>
                        </>
                      )}
                      <hr className="my-2 border-primary-200" />
                      <button
                        onClick={handleLogout}
                        className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded transition-colors"
                      >
                        Sign Out
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center space-x-4">
                <Link
                  href="/app2/signin"
                  className="text-primary-700 hover:text-primary-900 transition-colors duration-200 font-medium"
                >
                  Sign In
                </Link>
                <Link
                  href="/app2/signup"
                  className="glass-button text-primary-800 font-semibold"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={toggleMobileMenu}
            className="md:hidden p-2 rounded-md text-primary-700 hover:text-primary-900 hover:bg-primary-100 transition-colors"
            aria-label="Toggle mobile menu"
            aria-expanded={isMobileMenuOpen}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {isMobileMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden glass-card mt-4 mb-4">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {navigationItems.map((item) => {
                if (item.protected && !user) return null
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className="block px-3 py-2 text-base font-medium text-primary-700 hover:text-primary-900 hover:bg-primary-50 rounded-md transition-colors"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    {item.name}
                  </Link>
                )
              })}
              
              {user ? (
                <>
                  <hr className="my-2 border-primary-200" />
                  <div className="px-3 py-2">
                    <p className="text-sm font-medium text-primary-800">{user.name}</p>
                    <p className="text-xs text-primary-600">{user.plan} plan</p>
                  </div>
                  <Link
                    href="/app2/profile"
                    className="block px-3 py-2 text-base font-medium text-primary-700 hover:text-primary-900 hover:bg-primary-50 rounded-md transition-colors"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Profile
                  </Link>
                  <Link
                    href="/app2/settings"
                    className="block px-3 py-2 text-base font-medium text-primary-700 hover:text-primary-900 hover:bg-primary-50 rounded-md transition-colors"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Settings
                  </Link>
                  {user.plan === 'growth' && (
                    <>
                      <hr className="my-2 border-primary-200" />
                      <div className="px-3 py-2">
                        <p className="text-xs font-medium text-primary-600 uppercase tracking-wide">Admin</p>
                      </div>
                      <Link
                        href="/app2/admin/feature-flags"
                        className="block px-3 py-2 text-base font-medium text-primary-700 hover:text-primary-900 hover:bg-primary-50 rounded-md transition-colors"
                        onClick={() => setIsMobileMenuOpen(false)}
                      >
                        Feature Flags
                      </Link>
                      <Link
                        href="/app2/admin/email-system"
                        className="block px-3 py-2 text-base font-medium text-primary-700 hover:text-primary-900 hover:bg-primary-50 rounded-md transition-colors"
                        onClick={() => setIsMobileMenuOpen(false)}
                      >
                        Email System
                      </Link>
                    </>
                  )}
                  <button
                    onClick={() => {
                      handleLogout()
                      setIsMobileMenuOpen(false)
                    }}
                    className="block w-full text-left px-3 py-2 text-base font-medium text-red-600 hover:text-red-800 hover:bg-red-50 rounded-md transition-colors"
                  >
                    Sign Out
                  </button>
                </>
              ) : (
                <>
                  <hr className="my-2 border-primary-200" />
                  <Link
                    href="/app2/signin"
                    className="block px-3 py-2 text-base font-medium text-primary-700 hover:text-primary-900 hover:bg-primary-50 rounded-md transition-colors"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Sign In
                  </Link>
                  <Link
                    href="/app2/signup"
                    className="block px-3 py-2 text-base font-medium text-primary-700 hover:text-primary-900 hover:bg-primary-50 rounded-md transition-colors"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Get Started
                  </Link>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
