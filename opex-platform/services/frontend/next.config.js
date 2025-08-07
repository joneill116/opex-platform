/** @type {import('next').NextConfig} */
const nextConfig = {
  // App Router optimizations
  experimental: {
    optimizePackageImports: ['lucide-react', '@tanstack/react-query']
  },
  
  // Docker standalone output
  output: 'standalone',
  
  // Image optimization
  images: {
    minimumCacheTTL: 60 * 60 * 24 * 30 // 30 days
  },
  
  // Build configuration
  typescript: {
    ignoreBuildErrors: false
  },
  
  eslint: {
    ignoreDuringBuilds: false
  }
}

module.exports = nextConfig
