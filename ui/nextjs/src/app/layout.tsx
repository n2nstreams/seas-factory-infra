import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { AuthProvider } from '@/components/providers/AuthProvider'
import { FeatureFlagProvider } from '@/components/providers/FeatureFlagProvider'
import { DualAuthProvider } from '@/components/providers/DualAuthProvider'
import { ObservabilityProvider } from '@/components/providers/ObservabilityProvider'
import { Analytics } from '@vercel/analytics/react'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AI SaaS Factory',
  description: 'Build, deploy, and scale AI-powered SaaS applications',
  keywords: ['AI', 'SaaS', 'Factory', 'Development', 'Automation'],
  authors: [{ name: 'AI SaaS Factory Team' }],
  viewport: 'width=device-width, initial-scale=1',
  robots: 'index, follow',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <FeatureFlagProvider>
          <ObservabilityProvider>
            <DualAuthProvider>
              <AuthProvider>
                {children}
              </AuthProvider>
            </DualAuthProvider>
          </ObservabilityProvider>
        </FeatureFlagProvider>
        <Analytics />
      </body>
    </html>
  )
}
