import type { APIRoute } from 'astro';
import { authenticatedFetch, AuthRefreshError, backend, getSession } from '../../lib/auth';
import { resolveLocale } from '../../i18n';
import { appPath } from '../../lib/paths';
export const POST: APIRoute = async ({ request, cookies, redirect }) => { const session = getSession(cookies); const locale = resolveLocale(request); const plan = (await request.formData()).get('plan_id'); try { const response = await authenticatedFetch(session, cookies, `${backend}/billing/checkout?plan_id=${encodeURIComponent(String(plan))}`, { method: 'POST', headers: { 'Accept-Language': locale } }); return response.ok ? new Response(await response.text(), { status: 200, headers: { 'Content-Type': 'application/json' } }) : new Response(await response.text(), { status: response.status, headers: { 'Content-Type': 'application/json' } }); } catch (error) { if (error instanceof AuthRefreshError) return redirect(appPath('auth/login')); throw error; } };
