import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';
const script = readFileSync(new URL('../public/site-data.js', import.meta.url), 'utf8');
function visit({ url = 'https://tryproperpdf.app/', referrer = '', storage = new Map(), navigator = {} } = {}) {
  const sent = [];
  let click;
  runInNewContext(script, {
    URL, URLSearchParams, Date, navigator, location: new URL(url),
    sessionStorage: { getItem: key => storage.get(key) ?? null, setItem: (key, value) => storage.set(key, value) },
    document: { referrer, querySelector: selector => selector.includes('canonical') ? { href: new URL(new URL(url).pathname, url).href } : null,
      addEventListener: (event, handler) => { click = handler; } },
    fetch: (url, options) => { sent.push(JSON.parse(options.body)); return Promise.resolve(); }
  });
  return { sent, click: () => click({ target: { closest: () => ({ href: 'https://apps.apple.com/app/id6760956540' }) } }) };
}
test('keeps Google attribution across internal navigation and store clicks without raw URLs', () => {
  const storage = new Map();
  assert.equal(visit({ referrer: 'https://www.google.com/search?q=private', storage }).sent[0].source, 'google');
  const next = visit({ url: 'https://tryproperpdf.app/merge-pdf?secret=private', referrer: 'https://tryproperpdf.app/', storage });
  next.click();
  assert.deepEqual(next.sent[1], { event: 'download_click', path: '/merge-pdf', platform: 'ios', source: 'google', landing: '/' });
});
test('campaigns override referrers; unknown campaign values are not transmitted', () => {
  assert.equal(visit({ url: 'https://tryproperpdf.app/?utm_source=reddit', referrer: 'https://google.com/' }).sent[0].source, 'reddit');
  assert.equal(visit({ url: 'https://tryproperpdf.app/?utm_source=person@example.com' }).sent[0].source, 'other_campaign');
  assert.equal(visit({ referrer: 'https://google.com.evil.test/' }).sent[0].source, 'other_referral');
  assert.equal(visit().sent[0].source, 'direct');
});
test('privacy signals suppress events; expired attribution is discarded', () => {
  for (const navigator of [{ doNotTrack: '1' }, { globalPrivacyControl: true }]) assert.equal(visit({ navigator }).sent.length, 0);
  const storage = new Map([['properpdf-attribution', JSON.stringify({ source: 'reddit', landing: '/', expires: 1 })]]);
  assert.equal(visit({ storage }).sent[0].source, 'direct');
});
