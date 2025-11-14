// Enhanced player (Project B)
(function(){
  const params = new URLSearchParams(window.location.search);
  const useMock = params.get('use_mock') === '1';
  const video = document.getElementById('courseVideo');
  const notesDiv = document.getElementById('notes');
  const speedSelect = document.getElementById('speedSelect');
  const autoSkipToggle = document.getElementById('autoSkipToggle');
  const markSegmentBtn = document.getElementById('markSegmentBtn');

  // Sample notes that are time-synced
  const sampleNotes = [
    {t: 5.2, text: 'Intro'},
    {t: 22.0, text: 'Important concept'},
    {t: 40.5, text: 'Summary'},
  ];

  // Data models
  const storageKey = 'course_progress_c101';
  window.enhancedMetrics = { timeToFirstFrameMs: null, stalls: [], switches: [] };

  // Create notes UI with hover highlight & click-to-jump
  function renderNotes() {
    notesDiv.innerHTML = '';
    sampleNotes.forEach(n => {
      const d = document.createElement('div');
      d.className = 'note';
      d.dataset.t = n.t;
      d.textContent = `[${n.t.toFixed(1)}s] ${n.text}`;
      d.addEventListener('mouseenter', () => {
        d.style.background = '#e7f3ff';
      });
      d.addEventListener('mouseleave', () => {
        d.style.background = '';
      });
      d.addEventListener('click', () => {
        jumpTo(n.t);
      });
      notesDiv.appendChild(d);
    });
  }
  renderNotes();

  // Resume: store and restore progress
  function saveProgress() {
    const val = {t: video.currentTime || 0, last_updated: Date.now()};
    try {
      localStorage.setItem(storageKey, JSON.stringify(val));
      // Send to server
      navigator.sendBeacon('/progress', JSON.stringify(val));
    } catch (e) {
      console.debug('progress save failed', e);
    }
  }
  function restoreProgress() {
    try {
      const s = localStorage.getItem(storageKey);
      if (s) {
        const val = JSON.parse(s);
        if (val && typeof val.t === 'number') {
          console.debug('restoring progress', val);
          video.currentTime = val.t;
        }
      }
    } catch (e) { console.debug('restore failed', e); }
  }

  // playback speed control persisted per session
  speedSelect.addEventListener('change', () => {
    const v = parseFloat(speedSelect.value);
    video.playbackRate = v;
    sessionStorage.setItem('last_speed', String(v));
  });
  const lastSpeed = parseFloat(sessionStorage.getItem('last_speed') || '1.0');
  speedSelect.value = String(lastSpeed);
  video.playbackRate = lastSpeed;

  // Auto-skip learned segments
  let learnedSegments = [];
  function isLearnedAtTime(t) {
    return learnedSegments.some(([s,e]) => t >= s && t <= e);
  }
  function skipIfLearned() {
    if (!autoSkipToggle.checked) return;
    if (isLearnedAtTime(video.currentTime)) {
      // jump to next unlearned position
      const nextStart = learnedSegments.reduce((acc,[s,e]) => Math.max(acc, e), 0);
      console.debug('skipping learned to', nextStart);
      video.currentTime = nextStart + 0.01; // small offset
      window.enhancedMetrics.skippedTo = nextStart;
    }
  }

  markSegmentBtn.addEventListener('click', () => {
    const seg = [Math.max(0, Math.floor((video.currentTime||0)/30)*30), Math.floor((video.currentTime||0)/30)*30 + 30];
    learnedSegments.push(seg);
    console.debug('marked segment learned', seg);
    // send to server
    fetch('/learned_segments', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(learnedSegments)});
  });

  // Jumping to a timestamp
  function jumpTo(t) {
    video.currentTime = t;
    console.debug('jump to', t);
  }


  // Adaptive buffering / resolution
  let currentQuality = '720p';
  let lastSwitchTime = null;
  function chooseQuality(bw_kbps) {
    if (bw_kbps < 500) return '240p';
    if (bw_kbps < 1200) return '720p';
    return '1080p';
  }
  function switchQuality(q) {
    if (!q || q === currentQuality) return;
    const now = Date.now();
    window.enhancedMetrics.switches.push({from: currentQuality, to: q, t: now});
    currentQuality = q;
    // implement switching by changing the source and maintaining currentTime
    const cur = video.currentTime || 0;
    video.pause();
    const src = `/video/${q}?bw_kbps=1000`;
    video.querySelector('source').src = src;
    video.load();
    video.currentTime = cur;
    video.play().then(()=>{ console.debug('switched to', q); });
  }

  // track stalls/rebuffer events (mocked or real)
  let stallStart = null;
  video.addEventListener('waiting', () => {
    stallStart = Date.now();
  });
  video.addEventListener('playing', () => {
    if (stallStart) {
      window.enhancedMetrics.stalls.push(Date.now() - stallStart);
      stallStart = null;
    }
  });

  // Save progress periodically
  setInterval(saveProgress, 3000);
  video.addEventListener('pause', saveProgress);
  video.addEventListener('ended', saveProgress);

  // Detect resume and auto-restore
  if (!useMock) {
    restoreProgress();
  } else {
    // if using mock, simulate restore using localStorage
    const s = localStorage.getItem(storageKey);
    if (s) {
      const val = JSON.parse(s);
      if (val && typeof val.t === 'number') {
        video.currentTime = val.t;
      }
    }
  }

  // Expose metrics
  const start = performance.now();
  video.addEventListener('playing', () => {
    if (window.enhancedMetrics.timeToFirstFrameMs === null) {
      window.enhancedMetrics.timeToFirstFrameMs = performance.now() - start;
    }
  });

  video.addEventListener('timeupdate', () => {
    skipIfLearned();
  });

})();
