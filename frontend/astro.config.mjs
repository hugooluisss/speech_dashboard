import { defineConfig } from 'astro/config';
import node from '@astrojs/node';

export default defineConfig({
  // Keep local development at the origin root; deployments behind a prefix can
  // set PUBLIC_BASE_PATH so Astro emits assets and routes under that prefix.
  base: process.env.PUBLIC_BASE_PATH || '/',
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
