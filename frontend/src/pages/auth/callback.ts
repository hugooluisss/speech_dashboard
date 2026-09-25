import type { APIRoute } from 'astro';
import { exchange } from '../../lib/auth';
import { appPath } from '../../lib/paths';
export const GET: APIRoute = async ({ url, cookies, redirect }) => (await exchange(url.searchParams.get('code') || '', url.searchParams.get('state') || '', cookies)) ? redirect(appPath('dashboard')) : new Response('Login failed', { status: 400 });
