import type { APIRoute } from 'astro';
import { loginUrl } from '../../lib/auth';
export const GET: APIRoute = async ({ cookies, redirect }) => redirect(await loginUrl(cookies));
