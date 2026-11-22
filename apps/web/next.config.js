const createNextIntlPlugin = require('next-intl/plugin');

const withNextIntl = createNextIntlPlugin();

const nextConfig = withNextIntl({
  experimental: { typedRoutes: true },
  generateBuildId: () => 'build-' + Date.now()
});

module.exports = nextConfig;
