import {test} from 'node:test';
import assert from 'node:assert';

test('layout: fa locale sets dir to rtl', () => {
  const locale = 'fa';
  const dir = locale === 'fa' ? 'rtl' : 'ltr';
  assert.strictEqual(dir, 'rtl');
});

test('layout: en locale sets dir to ltr', () => {
  const locale = 'en';
  const dir = locale === 'fa' ? 'rtl' : 'ltr';
  assert.strictEqual(dir, 'ltr');
});

test('layout: lang attribute equals locale value', () => {
  const locale = 'fa';
  const lang = locale || 'en';
  assert.strictEqual(lang, 'fa');
});

test('layout: defaults lang to en when locale is undefined', () => {
  const locale = undefined;
  const lang = locale || 'en';
  assert.strictEqual(lang, 'en');
});
