import { readRequest, json, budget, failure } from '../../server/http.js';
import { analyticsPaths } from '../../server/analytics-paths.js';

export async function onRequest({ request, env }) {
  try {
    const data = await readRequest(request);
    if (request.headers.get('DNT') === '1' || request.headers.get('Sec-GPC') === '1') return json({ ok: true });
    if (!['page_view', 'download_click'].includes(data.event) || !analyticsPaths.includes(data.path)) {
      return json({ error: 'Invalid event.' }, 400);
    }
    const platform = data.event === 'page_view' ? 'none' : data.platform;
    if (!['none', 'ios', 'android'].includes(platform) || (data.event === 'download_click' && platform === 'none')) {
      return json({ error: 'Invalid platform.' }, 400);
    }
    const source = data.source ?? 'unknown';
    const landing = data.landing ?? data.path;
    if (!['unknown', 'google', 'bing', 'duckduckgo', 'yahoo', 'facebook', 'instagram', 'reddit', 'youtube', 'tiktok', 'linkedin', 'x', 'chatgpt', 'perplexity', 'email', 'other_campaign', 'other_referral', 'direct'].includes(source) || !analyticsPaths.includes(landing)) {
      return json({ error: 'Invalid attribution.' }, 400);
    }
    if (!env.DB) return json({ error: 'Analytics unavailable.' }, 503);
    await budget(env.DB, 'events', 2000);
    const day = new Date().toISOString().slice(0, 10);
    await env.DB.batch([
      env.DB.prepare(`INSERT INTO analytics_daily (day, event, path, platform) VALUES (?, ?, ?, ?)
        ON CONFLICT(day, event, path, platform) DO UPDATE SET count = count + 1`).bind(day, data.event, data.path, platform),
      env.DB.prepare(`INSERT INTO analytics_sources_daily (day, event, path, platform, source, landing) VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(day, event, path, platform, source, landing) DO UPDATE SET count = count + 1`).bind(day, data.event, data.path, platform, source, landing),
      env.DB.prepare("DELETE FROM analytics_sources_daily WHERE day < date('now', '-730 days')"),
      env.DB.prepare("DELETE FROM analytics_daily WHERE day < date('now', '-730 days')")
    ]);
    return json({ ok: true });
  } catch (error) { return failure(error); }
}
