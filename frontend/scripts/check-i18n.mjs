import assert from 'node:assert/strict';
import { resolveLocale } from '../src/i18n/index.ts';

assert.equal(resolveLocale(new Request('http://localhost', { headers: { cookie: 'speech_locale=es', 'accept-language': 'en' } })), 'es');
assert.equal(resolveLocale(new Request('http://localhost', { headers: { 'accept-language': 'es-MX, en;q=0.8' } })), 'es');
assert.equal(resolveLocale(new Request('http://localhost')), 'en');
