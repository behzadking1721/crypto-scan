import {test} from 'node:test';
import assert from 'node:assert';
import {readFileSync} from 'node:fs';

const locales = ['en', 'fa'];
const defaultLocale = 'en';

const enMessages = JSON.parse(readFileSync(new URL('../../messages/en.json', import.meta.url), 'utf8'));
const faMessages = JSON.parse(readFileSync(new URL('../../messages/fa.json', import.meta.url), 'utf8'));

test('i18n: defines supported locales en and fa', () => {
  assert.deepStrictEqual(locales, ['en', 'fa']);
});

test('i18n: sets default locale to en', () => {
  assert.strictEqual(defaultLocale, 'en');
});

test('i18n: loads English messages from messages/en.json', () => {
  assert.strictEqual(enMessages.Home.title, 'Crypto Intelligence Platform');
  assert.strictEqual(enMessages.Home.subtitle, 'Smart Money & Trader Intelligence System');
});

test('i18n: loads Persian messages from messages/fa.json', () => {
  assert.strictEqual(faMessages.Home.title, 'پلتفرم هوش ارز دیجیتال');
  assert.strictEqual(faMessages.Home.subtitle, 'سیستم هوش تریدر و پول هوشمند');
});

test('i18n: message files have identical key structure', () => {
  const enKeys = Object.keys(enMessages).sort();
  const faKeys = Object.keys(faMessages).sort();
  assert.deepStrictEqual(enKeys, faKeys);
  const enHomeKeys = Object.keys(enMessages.Home).sort();
  const faHomeKeys = Object.keys(faMessages.Home).sort();
  assert.deepStrictEqual(enHomeKeys, faHomeKeys);
});
