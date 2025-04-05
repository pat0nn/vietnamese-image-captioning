/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost'],
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '5000',
        pathname: '/uploads/**',
      },
      {
        protocol: 'https',
        hostname: '*.azureml.ms',
        pathname: '/uploads/**',
      },
    ],
    unoptimized: process.env.NODE_ENV === 'production',
  },
  output: 'export',
  trailingSlash: true,
}

module.exports = nextConfig
