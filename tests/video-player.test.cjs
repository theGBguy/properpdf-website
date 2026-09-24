const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { runInNewContext } = require('node:vm');
function setup() {
  function node() {
    const classes = new Set();
    return { events: {}, attributes: {}, hidden: false,
      style: { setProperty() {} },
      classList: { add: c => classes.add(c), remove: c => classes.delete(c), toggle(c, on) { if(on) classes.add(c); else classes.delete(c); }, contains: c => classes.has(c) },
      addEventListener(name, fn) { this.events[name] = fn; },
      setAttribute(name, value) { this.attributes[name] = value; }, querySelector() { return this.symbol ||= {}; }
    };
  }
  const player = node(), document = node();
  const elements = Object.fromEntries(['video','.video-start','.video-controls','[data-video-play]','[data-video-mute]','[data-video-fullscreen]','.video-progress','.video-time','.video-status'].map(k=>[k,node()]));
  player.querySelector = key => elements[key]; document.querySelector = () => player;
  const video = elements.video;
  Object.assign(video, { paused: true, ended: false, duration: 33, currentTime: 0, muted: true,
    async play() { this.paused = false; this.events.play(); },
    pause() { this.paused = true; this.events.pause(); }
  });
  player.requestFullscreen = async () => { document.fullscreenElement = player; document.events.fullscreenchange(); };
  document.exitFullscreen = async () => { document.fullscreenElement = null; document.events.fullscreenchange(); };
  let idle;
  runInNewContext(readFileSync(new URL('../public/video-player.js', `file://${__filename}`),'utf8'), {document, setTimeout(fn) { idle=fn;return 1; },clearTimeout() {idle=null;}});
  return { player, elements, video, document, idle:()=>idle() };
}
test('plays, hides idle controls, pauses and replays', async () => {
  const { player,elements,video,idle }=setup();
  assert.equal(video.controls,false);
  await elements['.video-start'].events.click();
  assert.equal(video.paused,false);assert.ok(player.classList.contains('is-playing'));
  idle();assert.ok(player.classList.contains('controls-idle'));
  await elements['[data-video-play]'].events.click();assert.equal(video.paused,true);assert.ok(!player.classList.contains('controls-idle'));
  video.ended=true;video.currentTime=33;await elements['.video-start'].events.click();assert.equal(video.currentTime,0);
});
test('seeks, toggles sound and enters/exits fullscreen',async()=>{
  const {elements,video,document}=setup();
  elements['.video-progress'].value=50;elements['.video-progress'].events.input();assert.equal(video.currentTime,16.5);
  elements['[data-video-mute]'].events.click();video.events.volumechange();assert.equal(video.muted,false);assert.equal(elements['[data-video-mute]'].attributes['aria-label'],'Mute');
  await elements['[data-video-fullscreen]'].events.click();assert.ok(document.fullscreenElement);
  await elements['[data-video-fullscreen]'].events.click();assert.equal(document.fullscreenElement,null);
});
test('handles playback rejection and restores native controls for a media error',async()=>{
  const {elements,video}=setup();video.play=async()=>{throw new Error('blocked');};
  await elements['.video-start'].events.click();assert.equal(elements['.video-status'].hidden,false);
  video.events.error();assert.equal(video.controls,true);assert.equal(elements['.video-controls'].hidden,true);
});
