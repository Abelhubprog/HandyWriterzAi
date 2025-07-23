/** @type {import('next').NextConfig} */
const nextConfig = {
  // Performance optimizations for faster dev builds
  reactStrictMode: false,
  swcMinify: true,
  
  // Enable standalone output for Railway deployment
  output: 'standalone',
  
  // Reduce bundle analysis and optimization overhead in development
  productionBrowserSourceMaps: false,
  
  // Experimental features for performance
  experimental: {
    optimizePackageImports: [
      'lucide-react',
      '@radix-ui/react-icons',
      'framer-motion'
    ],
    // Enable Turbopack for faster builds (Next.js 14+)
    turbo: {
      rules: {
        '*.svg': {
          loaders: ['@svgr/webpack'],
          as: '*.js',
        },
      },
    },
    // Reduce memory usage
    workerThreads: false,
    esmExternals: true,
  },

  // Transpile packages that need it
  transpilePackages: [
    '@dynamic-labs/sdk-react-core',
    '@dynamic-labs/ethereum', 
    '@dynamic-labs/solana',
    '@langchain/langgraph-sdk'
  ],

  // Webpack optimizations
  webpack: (config, { isServer, dev }) => {
    // Development-specific optimizations
    if (dev) {
      // Reduce module resolution complexity
      config.resolve.symlinks = false;
      
      // Faster development builds
      config.optimization = {
        ...config.optimization,
        removeAvailableModules: false,
        removeEmptyChunks: false,
        splitChunks: false,
      };
      
      // Disable source maps in development for speed
      config.devtool = false;
    }

    // Handle Node.js polyfills only in production
    if (!dev && !isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
        crypto: 'crypto-browserify',
        stream: 'stream-browserify',
        url: 'url',
        zlib: 'browserify-zlib',
        http: 'stream-http',
        https: 'https-browserify',
        assert: 'assert',
        os: 'os-browserify/browser',
        path: 'path-browserify',
      };
    }

    // Externalize heavy dependencies in browser
    if (!isServer) {
      config.externals = config.externals || [];
      config.externals.push('pino-pretty', 'encoding');
    }

    return config;
  },

  // Headers for development CORS
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET,POST,PUT,DELETE,OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'Content-Type, Authorization' },
        ],
      },
    ];
  },
};

export default nextConfig;
