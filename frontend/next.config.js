/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost', 'ngrok.io', 'ngrok-free.app'],
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '5000',
        pathname: '/uploads/**',
      },
      {
        protocol: 'https',
        hostname: '*.ngrok-free.app',
        pathname: '/uploads/**',
      },
      {
        protocol: 'https',
        hostname: '*.ngrok.io',
        pathname: '/uploads/**',
      },
      {
        protocol: 'http',
        hostname: process.env.NEXT_PUBLIC_BACKEND_HOST || 'localhost',
        port: process.env.NEXT_PUBLIC_BACKEND_PORT || '5000',
        pathname: '/uploads/**',
      },
      {
        protocol: 'https',
        hostname: process.env.NEXT_PUBLIC_BACKEND_HOST,
        pathname: '/uploads/**',
      },
      {
        protocol: 'https',
        hostname: '*.azureml.ms',
        pathname: '/uploads/**',
      },
    ],
    unoptimized: true,
  },
  output: 'export',
  trailingSlash: true,
}

module.exports = nextConfig
