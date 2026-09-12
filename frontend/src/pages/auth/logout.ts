import type { APIRoute } from 'astro';
import { clearSession, endSessionUrl, getSession } from '../../lib/auth';
export const GET: APIRoute = ({ cookies, redirect }) => { const url = endSessionUrl(getSession(cookies)?.idToken); clearSession(cookies); return redirect(url); };
