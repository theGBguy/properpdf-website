import { onRequest as subscribe } from '../functions/api/subscribe.js';
import { onRequest as events } from '../functions/api/events.js';
import { json } from './http.js';

export default {
  async fetch(request, env) {
    const path = new URL(request.url).pathname;
    if (path === '/api/subscribe') return subscribe({ request, env });
    if (path === '/api/events') return events({ request, env });
    if (path === '/api' || path.startsWith('/api/')) return json({ error: 'Not found.' }, 404);
    return env.ASSETS.fetch(request);
  }
};
