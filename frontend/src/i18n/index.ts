export type Locale = 'en' | 'es';

export function resolveLocale(request: Request): Locale {
  const cookie = request.headers.get('cookie')?.match(/(?:^|;\s*)speech_locale=(en|es)(?:;|$)/)?.[1];
  if (cookie) return cookie as Locale;
  return request.headers.get('accept-language')?.toLowerCase().split(',').some((value) => value.trim().startsWith('es')) ? 'es' : 'en';
}

export function assertKeyParity(name: string, dictionaries: Record<Locale, Record<string, string>>) {
  const english = Object.keys(dictionaries.en).sort().join('|');
  const spanish = Object.keys(dictionaries.es).sort().join('|');
  if (english !== spanish) throw new Error(`${name} translations have mismatched keys`);
}
