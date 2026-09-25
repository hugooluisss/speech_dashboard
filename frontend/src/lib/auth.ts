import { createHash, randomBytes, randomUUID } from 'node:crypto';
import { appPath } from './paths';

export const issuer = import.meta.env.PUBLIC_KEYCLOAK_PUBLIC_ISSUER_URL || process.env.KEYCLOAK_PUBLIC_ISSUER_URL || process.env.KEYCLOAK_ISSUER_URL || 'http://localhost:8080/realms/speech';
// Server-to-server token calls must use the internal Keycloak address. The
// public issuer is for browser redirects and may sit behind a proxy or WAF.
const serverIssuer = process.env.KEYCLOAK_ISSUER_URL || issuer;
export const backend = process.env.BACKEND_URL || 'http://localhost:8000';
const clientId = process.env.KEYCLOAK_WEB_CLIENT_ID || 'speech-dashboard-web';
const redirectUri = process.env.DASHBOARD_URL ? `${process.env.DASHBOARD_URL}/auth/callback` : `http://localhost:4321${appPath('auth/callback')}`;
// Secure must reflect whether the dashboard is actually served over HTTPS, not
// the build mode: `import.meta.env.PROD` is true for any production build,
// including one served over plain HTTP in local/dev deployments, which would
// make a browser silently discard the cookie and break login.
const secureCookies = redirectUri.startsWith('https://');
export type Session = { accessToken: string; refreshToken: string; idToken?: string; claims: Record<string, any> };
const sessions = new Map<string, Session>();
const refreshes = new WeakMap<Session, Promise<void>>();

export class AuthRefreshError extends Error {}

async function challenge(verifier: string) { return createHash('sha256').update(verifier).digest('base64url'); }
export async function loginUrl(cookies: any) {
  const state = randomUUID(); const verifier = randomBytes(32).toString('base64url');
  cookies.set('oauth_state', `${state}.${verifier}`, { httpOnly: true, secure: secureCookies, sameSite: 'lax', path: '/', maxAge: 600 });
  return `${issuer}/protocol/openid-connect/auth?${new URLSearchParams({ client_id: clientId, response_type: 'code', redirect_uri: redirectUri, scope: 'openid', state, code_challenge: await challenge(verifier), code_challenge_method: 'S256' })}`;
}
export async function exchange(code: string, state: string, cookies: any) {
  const saved = cookies.get('oauth_state')?.value?.split('.') || [];
  if (saved.length !== 2 || saved[0] !== state) return null;
  const result = await fetch(`${serverIssuer}/protocol/openid-connect/token`, { method: 'POST', headers: { 'content-type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams({ grant_type: 'authorization_code', client_id: clientId, code, redirect_uri: redirectUri, code_verifier: saved[1] }) });
  if (!result.ok) return null;
  const tokens = await result.json(); const claims = JSON.parse(Buffer.from(tokens.access_token.split('.')[1], 'base64url').toString()); const id = randomBytes(32).toString('base64url');
  sessions.set(id, { accessToken: tokens.access_token, refreshToken: tokens.refresh_token, idToken: tokens.id_token, claims }); cookies.delete('oauth_state', { path: '/' }); cookies.set('session', id, { httpOnly: true, secure: secureCookies, sameSite: 'lax', path: '/', maxAge: 3600 }); return sessions.get(id);
}
export function getSession(cookies: any) { const id = cookies.get('session')?.value; return id ? sessions.get(id) : undefined; }
export function clearSession(cookies: any) { const id = cookies.get('session')?.value; if (id) sessions.delete(id); cookies.delete('session', { path: '/' }); }
export function endSessionUrl(idToken?: string) { return `${issuer}/protocol/openid-connect/logout?${new URLSearchParams({ post_logout_redirect_uri: redirectUri.replace('/auth/callback', '/'), client_id: clientId, ...(idToken ? { id_token_hint: idToken } : {}) })}`; }

async function refresh(session: Session, cookies: any) {
  const current = refreshes.get(session);
  if (current) return current;
  const pending = (async () => {
    const result = await fetch(`${serverIssuer}/protocol/openid-connect/token`, { method: 'POST', headers: { 'content-type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams({ grant_type: 'refresh_token', client_id: clientId, refresh_token: session.refreshToken }) });
    if (!result.ok) { clearSession(cookies); throw new AuthRefreshError('Session expired'); }
    const tokens = await result.json();
    session.accessToken = tokens.access_token;
    session.refreshToken = tokens.refresh_token || session.refreshToken;
    session.claims = JSON.parse(Buffer.from(tokens.access_token.split('.')[1], 'base64url').toString());
  })();
  refreshes.set(session, pending);
  try { await pending; } finally { refreshes.delete(session); }
}

export async function authenticatedFetch(session: Session | undefined, cookies: any, input: RequestInfo | URL, init: RequestInit = {}) {
  if (!session) throw new AuthRefreshError('No active session');
  const request = () => { const headers = new Headers(init.headers); headers.set('Authorization', `Bearer ${session.accessToken}`); return fetch(input, { ...init, headers }); };
  let response = await request();
  if (response.status !== 401) return response;
  await refresh(session, cookies);
  response = await request();
  if (response.status === 401) throw new AuthRefreshError('Session refresh rejected');
  return response;
}
