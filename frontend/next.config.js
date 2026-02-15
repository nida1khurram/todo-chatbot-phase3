/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    turbo: {
      // Disable Turbopack for now due to compatibility issues
      enabled: false,
    },
  },
};

module.exports = nextConfig;