(() => {
  const player = document.querySelector('[data-video-player]');
  if (!player) return;
  const video = player.querySelector('video');
  const start = player.querySelector('.video-start');
  const controls = player.querySelector('.video-controls');
  const play = player.querySelector('[data-video-play]');
  const mute = player.querySelector('[data-video-mute]');
  const fullscreen = player.querySelector('[data-video-fullscreen]');
  const progress = player.querySelector('.video-progress');
  const time = player.querySelector('.video-time');
  const status = player.querySelector('.video-status');
  let timer;
  function icon(button, name, label) {
    button.querySelector('span').textContent = name;
    button.setAttribute('aria-label', label);
  }
  function reveal() {
    player.classList.remove('controls-idle');
    clearTimeout(timer);
    if (!video.paused) timer = setTimeout(() => player.classList.add('controls-idle'), 2400);
  }
  function format(seconds) {
    return `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`;
  }
  function sync() {
    const duration = Number.isFinite(video.duration) ? video.duration : 0;
    progress.disabled = duration === 0;
    progress.value = duration ? video.currentTime / duration * 100 : 0;
    progress.style.setProperty('--progress', `${progress.value}%`);
    progress.setAttribute('aria-valuetext', `${format(video.currentTime)} of ${format(duration)}`);
    time.textContent = `${format(video.currentTime)}${duration ? ' / ' + format(duration) : ''}`;
    player.classList.toggle('is-playing', !video.paused);
    icon(play, video.paused ? 'play_arrow' : 'pause', video.paused ? 'Play' : 'Pause');
    icon(mute, video.muted ? 'volume_off' : 'volume_up', video.muted ? 'Unmute' : 'Mute');
    start.setAttribute('aria-label', video.ended ? 'Replay signing demo' : 'Play signing demo');
  }
  async function toggle() {
    status.hidden = true;
    if (video.paused) {
      try { if (video.ended) video.currentTime = 0; await video.play(); }
      catch { status.textContent = 'Unable to play. Please try again.'; status.hidden = false; }
    } else video.pause();
    reveal();
  }
  start.addEventListener('click', toggle);
  play.addEventListener('click', toggle);
  video.addEventListener('click', toggle);
  video.addEventListener('keydown', event => {
    if (event.key === ' ' || event.key === 'Enter') { event.preventDefault(); toggle(); }
  });
  mute.addEventListener('click', () => { video.muted = !video.muted; });
  progress.addEventListener('input', () => {
    if (Number.isFinite(video.duration)) video.currentTime = Number(progress.value) / 100 * video.duration;
    reveal();
  });
  fullscreen.addEventListener('click', async () => {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else if (player.requestFullscreen) await player.requestFullscreen();
      else if (video.webkitEnterFullscreen) video.webkitEnterFullscreen();
    } catch { status.textContent = 'Fullscreen is unavailable in this browser.'; status.hidden = false; }
  });
  if (!player.requestFullscreen && !video.webkitEnterFullscreen) fullscreen.hidden = true;
  document.addEventListener('fullscreenchange', () => {
    const expanded = document.fullscreenElement === player;
    icon(fullscreen, expanded ? 'fullscreen_exit' : 'fullscreen', expanded ? 'Exit fullscreen' : 'Enter fullscreen');
  });
  ['timeupdate', 'loadedmetadata', 'durationchange', 'volumechange'].forEach(event => video.addEventListener(event, sync));
  ['play', 'pause', 'ended'].forEach(event => video.addEventListener(event, () => { sync(); reveal(); }));
  video.addEventListener('error', () => {
    video.controls = true;
    player.classList.remove('player-enhanced');
    start.hidden = controls.hidden = true;
    status.textContent = 'The video could not load. Please refresh and try again.';
    status.hidden = false;
  });
  player.addEventListener('pointermove', reveal);
  player.addEventListener('pointerdown', reveal);
  player.addEventListener('focusin', reveal);
  video.controls = false;
  video.tabIndex = 0;
  video.setAttribute('aria-label', 'Signing demo. Press Space or Enter to play or pause.');
  player.classList.add('player-enhanced');
  start.hidden = controls.hidden = false;
  sync();
})();
