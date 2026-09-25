import type { APIRoute } from 'astro';
import { authenticatedFetch, AuthRefreshError, backend, getSession } from '../../lib/auth';
import { resolveLocale } from '../../i18n';
import { appPath } from '../../lib/paths';
export const GET: APIRoute = async ({ request, cookies, redirect }) => { const session = getSession(cookies); const locale = resolveLocale(request); try { const response = await authenticatedFetch(session, cookies, `${backend}/me`, { headers: { 'Accept-Language': locale } }); return new Response(await response.text(), { status: response.status, headers: { 'Content-Type': 'application/json' } }); } catch (error) { if (error instanceof AuthRefreshError) return redirect(appPath('auth/login')); throw error; } };
