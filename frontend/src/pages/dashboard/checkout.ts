import type { APIRoute } from 'astro';
import { backend, getSession } from '../../lib/auth';
import { resolveLocale } from '../../i18n';
export const POST: APIRoute = async ({ request, cookies, redirect }) => { const session = getSession(cookies); const locale = resolveLocale(request); const plan = (await request.formData()).get('plan_id'); const response = await fetch(`${backend}/billing/checkout?plan_id=${encodeURIComponent(String(plan))}`, { method: 'POST', headers: { Authorization: `Bearer ${session?.accessToken}`, 'Accept-Language': locale } }); return response.ok ? redirect((await response.json()).url) : new Response(await response.text(), { status: response.status, headers: { 'Content-Type': 'application/json' } }); };
