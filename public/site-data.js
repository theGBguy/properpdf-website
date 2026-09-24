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
  // Use the canonical path only. Never send query strings, referrers or user IDs.
  const canonical = document.querySelector('link[rel="canonical"]');
  const path = canonical ? new URL(canonical.href).pathname : location.pathname;
  function record(event, platform = 'none') {
    fetch('/api/events', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ event, path, platform }), keepalive: true, credentials: 'omit'
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
