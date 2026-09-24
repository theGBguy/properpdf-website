import { test } from 'node:test';
import assert from 'node:assert/strict';
import { DatabaseSync } from 'node:sqlite';
import { readFileSync } from 'node:fs';
import { onRequest as subscribe } from '../functions/api/subscribe.js';
import { onRequest as events } from '../functions/api/events.js';

function database() {
  const sql = new DatabaseSync(':memory:');
  sql.exec(readFileSync(new URL('../migrations/0001_site_data.sql', import.meta.url), 'utf8'));
  return { sql, prepare(query) {
    let values = [];
    const statement = {
      bind(...args) { values = args; return statement; },
      async run() { return sql.prepare(query).run(...values); },
      async first() { return sql.prepare(query).get(...values) ?? null; }
    };
    return statement;
  }, async batch(statements) {
    sql.exec('BEGIN');
    try { const results = []; for (const statement of statements) results.push(await statement.run()); sql.exec('COMMIT'); return results; }
    catch (error) { sql.exec('ROLLBACK'); throw error; }
  } };
}
function request(route, body, headers = {}, method = 'POST') {
  return new Request(`https://tryproperpdf.app/api/${route}`, { method,
    headers: { Origin: 'https://tryproperpdf.app', 'Content-Type': 'application/json', ...headers },
    ...(method === 'POST' ? { body: JSON.stringify(body) } : {}) });
}

test('saves explicit consent once, normalizes email, and does not falsely verify ownership', async () => {
  const DB = database();
  for (const email of [' Person@Example.com ', 'person@example.com']) {
    const response = await subscribe({ request: request('subscribe', { email, consent: true }), env: { DB } });
    assert.equal(response.status, 200);
  }
  const rows = DB.sql.prepare('SELECT * FROM development_subscribers').all();
  assert.equal(rows.length, 1); assert.equal(rows[0].email, 'person@example.com');
  assert.equal(rows[0].email_verified, 0); assert.equal(rows[0].consent_version, 'development-updates-v1');
  assert.ok(rows[0].subscribed_at);
});

test('rejects invalid addresses, missing consent, cross-origin writes, and oversize bodies', async () => {
  const DB = database();
  for (const [body, headers, expected] of [
    [{ email: 'bad', consent: true }, {}, 400],
    [{ email: 'a@example.com' }, {}, 400],
    [{ email: 'a@example.com', consent: true }, { Origin: 'https://other.test' }, 403],
    [{ email: 'a@example.com', consent: true }, { 'Content-Type': 'text/plain' }, 415],
    [{ email: 'a'.repeat(3000) }, {}, 413]
  ]) assert.equal((await subscribe({ request: request('subscribe', body, headers), env: { DB } })).status, expected);
  assert.equal(DB.sql.prepare('SELECT count(*) AS n FROM development_subscribers').get().n, 0);
});

test('honeypot does not save; GET cannot read the list; missing database is not success', async () => {
  const DB = database();
  assert.equal((await subscribe({ request: request('subscribe', { website: 'spam' }), env: { DB } })).status, 200);
  assert.equal(DB.sql.prepare('SELECT count(*) AS n FROM development_subscribers').get().n, 0);
  assert.equal((await subscribe({ request: request('subscribe', null, {}, 'GET'), env: { DB } })).status, 405);
  assert.equal((await subscribe({ request: request('subscribe', { email: 'a@example.com', consent: true }), env: {} })).status, 503);
});

test('aggregates counts without recording identifiers and honors browser privacy headers', async () => {
  const DB = database();
  const body = { event: 'page_view', path: '/', platform: 'android', email: 'ignored@example.com' };
  for (let i = 0; i < 2; i++) assert.equal((await events({ request: request('events', body), env: { DB } })).status, 200);
  await events({ request: request('events', body, { DNT: '1' }), env: { DB } });
  await events({ request: request('events', body, { 'Sec-GPC': '1' }), env: { DB } });
  const rows = DB.sql.prepare('SELECT * FROM analytics_daily').all();
  assert.equal(rows.length, 1); assert.equal(rows[0].count, 2); assert.equal(rows[0].platform, 'none');
  assert.deepEqual(Object.keys(rows[0]), ['day', 'event', 'path', 'platform', 'count']);
  await events({ request: request('events', { event: 'download_click', path: '/', platform: 'ios' }), env: { DB } });
  assert.equal(DB.sql.prepare("SELECT count FROM analytics_daily WHERE event='download_click'").get().count, 1);
});

test('rejects arbitrary event dimensions, removes old counters, and limits signup bursts', async () => {
  const DB = database();
  for (const body of [
    { event: 'page_view', path: '/?email=private@example.com' },
    { event: 'unknown', path: '/' },
    { event: 'download_click', path: '/', platform: 'none' }
  ]) assert.equal((await events({ request: request('events', body), env: { DB } })).status, 400);
  DB.sql.exec("INSERT INTO analytics_daily VALUES ('2020-01-01','page_view','/','none',10)");
  await events({ request: request('events', { event: 'page_view', path: '/' }), env: { DB } });
  assert.equal(DB.sql.prepare("SELECT count(*) AS n FROM analytics_daily WHERE day='2020-01-01'").get().n, 0);
  const signup = () => subscribe({ request: request('subscribe', { email: 'a@example.com', consent: true }), env: { DB } });
  for (let i = 0; i < 30; i++) assert.equal((await signup()).status, 200);
  assert.equal((await signup()).status, 429);
});
