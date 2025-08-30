/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  async rewrites() {
    return [
      // Legacy backend proxy - REMOVED (legacy system decommissioned)
      // {
      //   source: '/api/:path*',
      //   destination: 'http://localhost:8000/api/:path*', // Legacy FastAPI backend (decommissioned)
      // },
      
      // Canary routing for /app2
      {
        source: '/app2/:path*',
        destination: '/app2/:path*',
        has: [
          {
            type: 'header',
            key: 'X-Canary-Version',
            value: 'v2',
          },
        ],
      },
    ];
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=31536000; includeSubDomains; preload',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()',
          },
        ],
      },
      {
        source: '/app2/(.*)',
        headers: [
          {
            key: 'X-Canary-Version',
            value: 'v2',
          },
          {
            key: 'X-Migration-Status',
            value: 'active',
          },
          {
            key: 'Cache-Control',
            value: 'public, max-age=300, s-maxage=600',
          },
        ],
      },
    ];
  },
  // Sentry configuration
  sentry: {
    hideSourceMaps: true,
    disableServerWebpackPlugin: process.env.NODE_ENV === 'development',
    disableClientWebpackPlugin: process.env.NODE_ENV === 'development',
  },
  // Cache policies for canary deployments
  generateEtags: true,
  compress: true,
  poweredByHeader: false,
  // Image optimization
  images: {
    domains: ['localhost', 'vercel.app'],
    formats: ['image/webp', 'image/avif'],
  },
  // Performance optimizations
  swcMinify: true,
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
};

module.exports = nextConfig;
