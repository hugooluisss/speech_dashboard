import type { APIRoute } from 'astro';
import { authenticatedFetch, AuthRefreshError, backend, getSession } from '../../lib/auth';
import { resolveLocale } from '../../i18n';
export const GET: APIRoute = async ({ request, cookies, redirect }) => { const session = getSession(cookies); const locale = resolveLocale(request); try { const response = await authenticatedFetch(session, cookies, `${backend}/billing/portal`, { method: 'POST', headers: { 'Accept-Language': locale } }); return response.ok ? redirect((await response.json()).url) : new Response(await response.text(), { status: response.status, headers: { 'Content-Type': 'application/json' } }); } catch (error) { if (error instanceof AuthRefreshError) return redirect('/auth/login'); throw error; } };
