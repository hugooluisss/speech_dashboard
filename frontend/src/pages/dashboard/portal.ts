import type { APIRoute } from 'astro';
import { backend, getSession } from '../../lib/auth';
export const GET: APIRoute = async ({ cookies, redirect }) => { const session = getSession(cookies); const response = await fetch(`${backend}/billing/portal`, { method: 'POST', headers: { Authorization: `Bearer ${session?.accessToken}` } }); return response.ok ? redirect((await response.json()).url) : new Response('Billing portal unavailable', { status: response.status }); };
