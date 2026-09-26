(() => {
  const form = document.querySelector('[data-email-capture]');
  if (form) {
    form.addEventListener('submit', async event => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      const button = form.querySelector('button[type="submit"]');
      if (button.disabled) return;
      const status = form.querySelector('.updates-status');
      button.disabled = true;
      button.textContent = 'Saving…';
      status.hidden = false;
      status.textContent = 'Saving your request…';
      try {
        const response = await fetch('/api/subscribe', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: form.elements.email.value, consent: form.elements.consent.checked, website: form.elements.website.value })
        });
        const data = await response.json();
        if (!response.ok || !data.ok) throw new Error(data.error || 'Please try again later.');
        form.reset();
        status.textContent = 'Your request has been saved. We’ll email you about ProperPDF development updates.';
      } catch {
        status.textContent = 'We couldn’t save your request. Please try again, or email hello@tryproperpdf.app to request updates.';
      } finally {
        button.disabled = false;
        button.textContent = 'Get updates';
      }
    });
  }

  if (navigator.doNotTrack === '1' || navigator.globalPrivacyControl === true) return;
  // Only send canonical paths and fixed source categories, never raw URLs or user IDs.
  const canonical = document.querySelector('link[rel="canonical"]');
  const path = canonical ? new URL(canonical.href).pathname : location.pathname;
  const sources = ['google', 'bing', 'duckduckgo', 'yahoo', 'facebook', 'instagram', 'reddit', 'youtube', 'tiktok', 'linkedin', 'x', 'chatgpt', 'perplexity', 'email', 'other_campaign', 'other_referral', 'direct'];
  const params = new URLSearchParams(location.search);
  const tagged = params.has('utm_source') || params.has('utm_medium') || params.has('utm_campaign');
  const utmSource = (params.get('utm_source') || '').toLowerCase();
  let source = 'direct';
  let external = false;
  try {
    const referrer = new URL(document.referrer);
    external = referrer.origin !== location.origin;
    if (external) {
      const host = referrer.hostname.replace(/^www\./, '');
      const domains = { 'google.com': 'google', 'bing.com': 'bing', 'duckduckgo.com': 'duckduckgo', 'search.yahoo.com': 'yahoo', 'facebook.com': 'facebook', 'instagram.com': 'instagram', 'reddit.com': 'reddit', 'youtube.com': 'youtube', 'tiktok.com': 'tiktok', 'linkedin.com': 'linkedin', 't.co': 'x', 'x.com': 'x', 'twitter.com': 'x', 'chatgpt.com': 'chatgpt', 'chat.openai.com': 'chatgpt', 'perplexity.ai': 'perplexity' };
      source = Object.entries(domains).find(([domain]) => host === domain || host.endsWith('.' + domain))?.[1] || 'other_referral';
      if (/^google\.(?:[a-z]{2,3}|co\.[a-z]{2}|com\.[a-z]{2})$/.test(host)) source = 'google';
    }
  } catch { /* Missing or suppressed referrer counts as direct/unknown. */ }
  if (tagged) source = (params.get('utm_medium') || '').toLowerCase() === 'email' ? 'email' : sources.includes(utmSource) && !['direct', 'other_referral'].includes(utmSource) ? utmSource : 'other_campaign';
  let attribution = { source, landing: path, expires: Date.now() + 30 * 60 * 1000 };
  try {
    const saved = JSON.parse(sessionStorage.getItem('properpdf-attribution'));
    if (!tagged && !external && saved && saved.expires > Date.now() && sources.includes(saved.source) && typeof saved.landing === 'string') attribution = saved;
    sessionStorage.setItem('properpdf-attribution', JSON.stringify(attribution));
  } catch { /* Tracking still works on the current page if storage is unavailable. */ }
  function record(event, platform = 'none') {
    fetch('/api/events', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ event, path, platform, source: attribution.source, landing: attribution.landing }), keepalive: true, credentials: 'omit'
    }).catch(() => {});
  }
  record('page_view');
  document.addEventListener('click', event => {
    const link = event.target.closest('a[href]');
    if (!link) return;
    const url = new URL(link.href, location.href);
    if (url.hostname === 'apps.apple.com') record('download_click', 'ios');
    else if (url.hostname === 'play.google.com') record('download_click', 'android');
  });
})();
