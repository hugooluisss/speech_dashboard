import { defineConfig } from 'astro/config';
import node from '@astrojs/node';

export default defineConfig({
  output: 'server',
  adapter: node({ mode: 'standalone' }),
  // Allows the dev server to accept requests through a tunnel (e.g.
  // Cloudflare Tunnel) whose hostname isn't known ahead of time. Dev-only:
  // production builds use the standalone Node adapter, which doesn't have
  // this host check.
  server: {
    allowedHosts: true,
  },
  vite: {
    server: {
      allowedHosts: true,
    },
  },
});
