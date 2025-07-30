/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false,
  transpilePackages: ['@dynamic-labs/sdk-react-core'],
  experimental: {
    optimizePackageImports: ['@radix-ui/react-icons'],
  },
  async rewrites() {
    return [{
      source: '/api/:path*',
      destination: 'http://localhost:8000/api/:path*',
    }]
  },
};

export default nextConfig;
