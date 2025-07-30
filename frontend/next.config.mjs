/** @type {import('next').NextConfig} */
const nextConfig = {
  // Performance optimizations
  reactStrictMode: false,
  
  // Proxy to backend
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ]
  },
  
  // Essential transpilation
  transpilePackages: [
    '@dynamic-labs/sdk-react-core',
    '@dynamic-labs/ethereum', 
    '@dynamic-labs/solana'
  ],

  // Experimental features
  experimental: {
    optimizePackageImports: ['@radix-ui/react-icons'],
  },

  // Turbopack configuration (stable in Next.js 15)
  turbopack: {
    rules: {
      '*.svg': {
        loaders: ['@svgr/webpack'],
        as: '*.js',
      },
    },
    resolveAlias: {
      '@': './src',
    },
  },

  // Conditional webpack config - only when not using turbopack
  ...(!process.env.TURBOPACK && {
    webpack: (config, { isServer, webpack, dev }) => {
      if (dev) {
        // Remove devtool override to prevent performance regression
        // Next.js will use its optimized default devtool
        config.optimization = {
          ...config.optimization,
          removeAvailableModules: false,
          removeEmptyChunks: false,
          splitChunks: false,
        };
      }

      if (!isServer) {
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
          'pino-pretty': false,
        };

        config.plugins = config.plugins || [];
        config.plugins.push(
          new webpack.IgnorePlugin({
            resourceRegExp: /pino-pretty/,
          }),
          new webpack.IgnorePlugin({
            resourceRegExp: /^encoding$/,
            contextRegExp: /node-fetch/,
          })
        );
      }

      return config;
    },
  }),
};

export default nextConfig;