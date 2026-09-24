import { readRequest, json, budget, failure } from '../../server/http.js';

export async function onRequest({ request, env }) {
  try {
    const data = await readRequest(request);
    if (data.website) return json({ ok: true }); // Honeypot; never store bot submissions.
    const email = typeof data.email === 'string' ? data.email.trim().toLowerCase() : '';
    if (email.length > 254 || !/^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(email)) {
      return json({ error: 'Enter a valid email address.' }, 400);
    }
    if (data.consent !== true) return json({ error: 'Please agree to receive development updates.' }, 400);
    if (!env.DB) return json({ error: 'Signups are temporarily unavailable. Please try again later.' }, 503);
    await budget(env.DB, 'subscribe', 30);
    await env.DB.prepare(`INSERT INTO development_subscribers (email, consent_version)
      VALUES (?, ?) ON CONFLICT(email) DO NOTHING`).bind(email, 'development-updates-v1').run();
    // The same response for existing addresses avoids exposing the subscriber list.
    return json({ ok: true });
  } catch (error) { return failure(error); }
}
