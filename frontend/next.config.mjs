/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false,
  // Transpile only what's necessary
  transpilePackages: ['@dynamic-labs/sdk-react-core'],
  // Prefer Turbopack for much faster HMR in dev on Windows
  experimental: {
    optimizePackageImports: [
      '@radix-ui/react-icons',
      '@radix-ui/react-select',
      '@radix-ui/react-dialog',
      '@radix-ui/react-dropdown-menu',
      '@radix-ui/react-popover',
      'lucide-react'
    ],
    turbo: {
      rules: {}
    }
  },
  // Reduce build overhead
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  swcMinify: true,
  productionBrowserSourceMaps: false,
  async rewrites() {
    const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000'
    return [{
      source: '/api/:path*',
      destination: `${BACKEND_URL}/api/:path*`,
    }]
  },
};

export default nextConfig;
