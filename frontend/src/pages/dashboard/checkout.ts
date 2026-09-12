import type { APIRoute } from 'astro';
import { backend, getSession } from '../../lib/auth';
export const POST: APIRoute = async ({ request, cookies, redirect }) => { const session = getSession(cookies); const plan = (await request.formData()).get('plan_id'); const response = await fetch(`${backend}/billing/checkout?plan_id=${encodeURIComponent(String(plan))}`, { method: 'POST', headers: { Authorization: `Bearer ${session?.accessToken}` } }); return response.ok ? redirect((await response.json()).url) : new Response('Checkout unavailable', { status: response.status }); };
