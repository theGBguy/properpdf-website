const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { runInNewContext } = require('node:vm');

function setup({ platform = 'ios', reduced = false } = {}) {
  function element(dataset = {}) {
    return { dataset, style: {}, events: {}, setAttribute(key, value) { this[key] = value; }, addEventListener(name, callback) { this.events[name] = callback; } };
  }
  const root = element();
  const panels = ['ios', 'android'].map(previewPlatform => element({ previewPlatform }));
  root.clientWidth = 500;
  root.querySelectorAll = () => panels;
  root.contains = () => false;
  const document = element();
  document.body = { dataset: { platform } };
  document.getElementById = () => root;
  const motion = element();
  motion.matches = reduced;
  const window = element();
  window.matchMedia = () => motion;
  let time = 0;
  let next;
  runInNewContext(readFileSync(new URL('../public/preview.js', `file://${__filename}`), 'utf8'), {
    document, window, performance: { now: () => time },
    requestAnimationFrame(callback) { next = callback; return 1; },
    cancelAnimationFrame() { next = null; }
  });
  return { root, panels, document, motion, pending: () => Boolean(next), advance(ms) {
    for (let i = 0; i < ms; i += 16) {
      time += 16;
      if (next) { const callback = next; next = null; callback(time); }
    }
  } };
}

test('starts rotating automatically and pairs the active panel with its platform', () => {
  const view = setup();
  view.advance(2500);
  assert.notEqual(view.panels[0].style.transform, 'translate3d(0px, 0, 0px) rotateY(0deg)');
  view.advance(1000);
  assert.equal(view.root.dataset.active, 'android');
  assert.equal(view.panels[0].inert, true);
  assert.equal(view.panels[1].inert, false);
});

test('pointer focus does not permanently pause after clicking and leaving', () => {
  const view = setup();
  view.root.events.pointerenter({ pointerType: 'mouse' });
  view.document.events.pointerdown();
  view.root.events.pointerdown({ pointerType: 'mouse' });
  view.root.events.focusin();
  view.root.events.pointerleave();
  assert.ok(view.pending());
  view.advance(9000);
  assert.equal(view.root.dataset.active, 'ios');
  view.advance(4600);
  assert.equal(view.root.dataset.active, 'android');
});

test('touch pauses temporarily, while keyboard focus holds until focus leaves', () => {
  const view = setup();
  view.document.events.pointerdown();
  view.root.events.pointerdown({ pointerType: 'touch' });
  view.root.events.focusin();
  view.advance(13600);
  assert.equal(view.root.dataset.active, 'android');
  view.document.events.keydown({ key: 'Tab' });
  view.root.events.focusin();
  assert.equal(view.pending(), false);
  view.root.events.focusout({ relatedTarget: null });
  assert.ok(view.pending());
});

test('explicitly requested rotation runs with Reduce Motion enabled and pauses in hidden tabs', () => {
  const reduced = setup({ reduced: true, platform: 'android' });
  assert.equal(reduced.pending(), true);
  assert.equal(reduced.root.dataset.active, 'android');
  reduced.advance(3500);
  assert.equal(reduced.root.dataset.active, 'ios');
  const view = setup();
  view.document.hidden = true;
  view.document.events.visibilitychange();
  assert.equal(view.pending(), false);
  view.document.hidden = false;
  view.document.events.visibilitychange();
  assert.ok(view.pending());
});
