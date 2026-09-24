(() => {
  const root = document.getElementById('platform-preview');
  if (!root) return;
  const panels = [...root.querySelectorAll('[data-preview-platform]')];
  const initial = document.body.dataset.platform === 'android' ? 1 : 0;
  const hold = 1800;
  const travel = 1600;
  const cycle = hold + travel;
  let elapsed = initial * cycle;
  let frame;
  let lastTime = null;
  let hovered = false;
  let focused = false;
  let keyboardInput = false;
  let resumeAfter = 0;
  let active = initial;

  function render() {
    const step = Math.floor(elapsed / cycle);
    const progress = Math.max(0, (elapsed % cycle - hold) / travel);
    const eased = progress * progress * (3 - 2 * progress);
    const angle = (step + eased) * Math.PI;
    // Scale the orbit to the column so it remains inside narrow viewports.
    const radius = Math.min(100, root.clientWidth * 0.2);
    active = (step + (eased >= 0.5 ? 1 : 0)) % 2;
    panels.forEach((panel, index) => {
      const phase = angle + index * Math.PI;
      const depth = Math.cos(phase);
      const x = Math.sin(phase) * radius;
      const z = (depth - 1) * 150;
      const tilt = Math.sin(phase) * -18;
      panel.style.transform = `translate3d(${x}px, 0, ${z}px) rotateY(${tilt}deg)`;
      panel.style.opacity = String(Math.max(0, (depth + 0.6) / 1.6));
      panel.style.zIndex = index === active ? '2' : '1';
      panel.inert = index !== active;
      panel.setAttribute('aria-hidden', String(index !== active));
    });
    root.dataset.active = panels[active].dataset.previewPlatform;
  }

  function blocked() {
    // This showcase explicitly opts into rotation, including on devices with
    // Reduce Motion enabled. Hover, touch, keyboard focus and hidden tabs pause it.
    return hovered || focused || document.hidden;
  }

  function tick(time) {
    frame = null;
    if (blocked()) { lastTime = null; return; }
    if (lastTime !== null && time >= resumeAfter) {
      elapsed += Math.min(time - Math.max(lastTime, resumeAfter), 64);
    }
    lastTime = time;
    render();
    frame = requestAnimationFrame(tick);
  }

  function update() {
    if (frame !== null && frame !== undefined) cancelAnimationFrame(frame);
    frame = null;
    lastTime = null;
    if (!blocked()) frame = requestAnimationFrame(tick);
  }

  // Only keyboard focus should hold the carousel. Pointer focus otherwise
  // survives mouseleave and can prevent automatic rotation from ever resuming.
  document.addEventListener('keydown', event => {
    if (event.key === 'Tab') keyboardInput = true;
  });
  document.addEventListener('pointerdown', () => {
    keyboardInput = false;
    focused = false;
    update();
  }, true);
  root.addEventListener('pointerenter', event => {
    if (event.pointerType === 'mouse' || event.pointerType === 'pen') {
      hovered = true;
      update();
    }
  });
  root.addEventListener('pointerleave', () => { hovered = false; update(); });
  root.addEventListener('pointerdown', event => {
    resumeAfter = performance.now() + 10000;
    // Keep pointer taps temporary without interfering with QR links or scrolling.
    keyboardInput = false;
    focused = false;
    update();
  });
  root.addEventListener('focusin', () => { focused = keyboardInput; update(); });
  root.addEventListener('focusout', event => {
    if (!root.contains(event.relatedTarget)) { focused = false; update(); }
  });
  document.addEventListener('visibilitychange', update);
  window.addEventListener('resize', render);
  render();
  update();
})();
