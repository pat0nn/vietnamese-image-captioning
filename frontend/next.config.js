/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  trailingSlash: true,
  output: 'export',
  images: {
    unoptimized: true,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api'
  },
  // Chỉ bao gồm các trang thực sự tồn tại trong thư mục pages
  exportPathMap: async function() {
    return {
      '/': { page: '/' },
      '/admin': { page: '/admin' },
      '/success': { page: '/success' },
      '/profile': { page: '/profile' }
    }
  }
};

module.exports = nextConfig;
