import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import worker from '../server/worker.js';

test('Worker entry point routes both APIs and rejects unknown API paths', async () => {
  const env = { ASSETS: { fetch() { throw new Error('API requests must not fall back to static files'); } } };
  for (const path of ['/api/subscribe', '/api/events']) {
    const response = await worker.fetch(new Request(`https://tryproperpdf.app${path}`), env);
    assert.equal(response.status, 405);
    assert.equal(response.headers.get('Allow'), 'POST');
  }
  const response = await worker.fetch(new Request('https://tryproperpdf.app/api/unknown'), env);
  assert.equal(response.status, 404);
});

test('Worker forwards non-API requests to the asset binding unchanged', async () => {
  const request = new Request('https://tryproperpdf.app/assets/sign-pdf-demo.mp4', { headers: { Range: 'bytes=0-1023' } });
  const response = new Response('asset', { status: 206 });
  const result = await worker.fetch(request, { ASSETS: { fetch(value) { assert.equal(value, request); return response; } } });
  assert.equal(result, response);
});

test('deployment targets the existing Worker and preserves the D1 binding', () => {
  const config = JSON.parse(readFileSync(new URL('../wrangler.jsonc', import.meta.url), 'utf8'));
  assert.equal(config.name, 'properpdf-website');
  assert.equal(config.main, 'server/worker.js');
  assert.equal(config.assets.binding, 'ASSETS');
  assert.deepEqual(config.assets.run_worker_first, ['/api', '/api/*']);
  assert.equal(config.d1_databases[0].binding, 'DB');
  assert.equal(config.pages_build_output_dir, undefined);
});
