/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost', 'ngrok-free.app', 'ngrok.io'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.ngrok-free.app',
      },
      {
        protocol: 'https',
        hostname: '**.ngrok.io',
      }
    ],
    unoptimized: true,
  },
  // Cấu hình cho Azure Static Web Apps
  trailingSlash: true,
  output: 'export',
}

module.exports = nextConfig 