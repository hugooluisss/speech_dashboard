import { defineMiddleware } from 'astro:middleware';
import { getSession, loginUrl } from './lib/auth';

export const onRequest = defineMiddleware(async (context, next) => {
  if (context.url.pathname.startsWith('/dashboard') && !getSession(context.cookies)) return context.redirect(await loginUrl(context.cookies));
  return next();
});
