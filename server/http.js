export function json(data, status = 200, extra = {}) {
  return Response.json(data, { status, headers: { 'Cache-Control': 'no-store', ...extra } });
}

export async function readRequest(request) {
  if (request.method !== 'POST') throw json({ error: 'Method not allowed.' }, 405, { Allow: 'POST' });
  const origin = request.headers.get('Origin');
  if (origin !== new URL(request.url).origin || request.headers.get('Sec-Fetch-Site') === 'cross-site') {
    throw json({ error: 'Request not allowed.' }, 403);
  }
  if (!request.headers.get('Content-Type')?.toLowerCase().startsWith('application/json')) {
    throw json({ error: 'Expected JSON.' }, 415);
  }
  if (Number(request.headers.get('Content-Length')) > 2048) throw json({ error: 'Request too large.' }, 413);
  const reader = request.body?.getReader();
  if (!reader) throw json({ error: 'Missing request body.' }, 400);
  const chunks = [];
  let size = 0;
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    size += value.byteLength;
    if (size > 2048) { await reader.cancel(); throw json({ error: 'Request too large.' }, 413); }
    chunks.push(value);
  }
  const bytes = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length; }
  try {
    const data = JSON.parse(new TextDecoder().decode(bytes));
    if (!data || typeof data !== 'object' || Array.isArray(data)) throw new Error();
    return data;
  } catch { throw json({ error: 'Invalid JSON.' }, 400); }
}

export async function budget(db, endpoint, limit) {
  const minute = Math.floor(Date.now() / 60000);
  const result = await db.prepare(`INSERT INTO api_limits (endpoint, minute, count) VALUES (?, ?, 1)
    ON CONFLICT(endpoint, minute) DO UPDATE SET count = count + 1 WHERE count < ?
    RETURNING count`).bind(endpoint, minute, limit).first();
  if (!result) throw json({ error: 'Too many requests. Please try again shortly.' }, 429, { 'Retry-After': '60' });
  await db.prepare('DELETE FROM api_limits WHERE minute < ?').bind(minute - 2).run();
}

export function failure(error) {
  if (error instanceof Response) return error;
  // Do not return database errors, addresses or request contents to the browser.
  return json({ error: 'Temporarily unavailable. Please try again later.' }, 503);
}
