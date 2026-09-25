const baseUrl = import.meta.env.BASE_URL;

/** Build an app-local URL that respects Astro's configured base path. */
export function appPath(path: string) {
  const segment = path.replace(/^\/+/, '');
  const prefix = baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`;
  return segment ? `${prefix}${segment}` : baseUrl === '/' ? '/' : prefix.slice(0, -1);
}
