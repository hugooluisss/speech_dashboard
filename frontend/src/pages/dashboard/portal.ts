import type { APIRoute } from 'astro';
import { backend, getSession } from '../../lib/auth';
import { resolveLocale } from '../../i18n';
export const GET: APIRoute = async ({ request, cookies, redirect }) => { const session = getSession(cookies); const locale = resolveLocale(request); const response = await fetch(`${backend}/billing/portal`, { method: 'POST', headers: { Authorization: `Bearer ${session?.accessToken}`, 'Accept-Language': locale } }); return response.ok ? redirect((await response.json()).url) : new Response(await response.text(), { status: response.status, headers: { 'Content-Type': 'application/json' } }); };
