(function () {
  const params = new URLSearchParams(window.location.search);
  const useMock = params.get('use_mock') === '1';
  const courseId = params.get('course_id') || 'C101';
  const video = document.getElementById('courseVideo');
  const notesContainer = document.getElementById('notes');
  const speedSelect = document.getElementById('speedSelect');
  const autoSkipToggle = document.getElementById('autoSkipToggle');
  const markSegmentBtn = document.getElementById('markSegmentBtn');
  const forceSwitchBtn = document.getElementById('forceSwitchBtn');
  const networkText = document.getElementById('networkProfileText');
  const bw = parseInt(params.get('bw_kbps') || '1200', 10);
  const latency = parseInt(params.get('latency_ms') || '50', 10);
  const jitter = parseInt(params.get('jitter_ms') || '10', 10);
  networkText.textContent = `${bw} kbps / ${latency} ms / jitter ${jitter} ms`;

  const storageKey = `course_progress_${courseId}`;
  const speedKey = `course_speed_${courseId}`;
  const allowedSpeeds = [0.75, 1.0, 1.25, 1.5, 2.0];
  let learnedSegments = [];
  let currentQuality = '720p';
  let stallStart = null;

  window.enhancedMetrics = {
    timeToFirstFrameMs: null,
    stalls: [],
    switches: [],
    resumeApplied: false,
    resumeTarget: 0,
    playbackRates: [],
    skippedSegments: [],
    noteJumps: [],
    currentQuality
  };

  function saveProgress() {
    const payload = { courseId, t: video.currentTime || 0, updated_at: Date.now() };
    try {
      localStorage.setItem(storageKey, JSON.stringify(payload));
      navigator.sendBeacon('/progress', JSON.stringify(payload));
    } catch (err) {
      console.debug('progress save failed', err);
    }
  }

  function restoreProgress() {
    try {
      const raw = localStorage.getItem(storageKey);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (typeof parsed.t === 'number') {
          video.currentTime = parsed.t;
          window.enhancedMetrics.resumeApplied = true;
          window.enhancedMetrics.resumeTarget = parsed.t;
        }
      }
    } catch (err) {
      console.debug('restore failed', err);
    }
  }

  function applySavedSpeed() {
    const saved = parseFloat(sessionStorage.getItem(speedKey) || '1.0');
    if (allowedSpeeds.includes(saved)) {
      video.playbackRate = saved;
      speedSelect.value = String(saved);
    }
  }

  speedSelect.addEventListener('change', () => {
    const desired = parseFloat(speedSelect.value);
    const closest = allowedSpeeds.reduce((prev, curr) => {
      return Math.abs(curr - desired) < Math.abs(prev - desired) ? curr : prev;
    }, 1.0);
    video.playbackRate = closest;
    sessionStorage.setItem(speedKey, String(closest));
    window.enhancedMetrics.playbackRates.push({ t: Date.now(), rate: closest });
  });

  autoSkipToggle.addEventListener('change', () => {
    if (!autoSkipToggle.checked) {
      window.enhancedMetrics.skippedSegments.push({ disabled_at: Date.now() });
    }
  });

  markSegmentBtn.addEventListener('click', () => {
    const start = Math.floor((video.currentTime || 0) / 30) * 30;
    const end = start + 30;
    learnedSegments.push([start, end]);
    fetch('/learned_segments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(learnedSegments)
    });
  });

  forceSwitchBtn.addEventListener('click', () => {
    const next = currentQuality === '720p' ? '1080p' : '720p';
    switchQuality(next);
  });

  function chooseQuality(bandwidth) {
    if (bandwidth < 400) return '240p';
    if (bandwidth < 900) return '480p';
    if (bandwidth < 1800) return '720p';
    return '1080p';
  }

  function switchQuality(targetQuality) {
    if (targetQuality === currentQuality) return;
    const before = currentQuality;
    const now = Date.now();
    const previousTime = video.currentTime || 0;
    currentQuality = targetQuality;
    window.enhancedMetrics.switches.push({
      from: before,
      to: targetQuality,
      started_at: now
    });
    window.enhancedMetrics.currentQuality = targetQuality;
    const src = video.querySelector('source');
    src.src = `/video/${targetQuality}?bw_kbps=${bw}&latency_ms=${latency}`;
    video.pause();
    video.load();
    video.currentTime = previousTime;
    video.play().catch(() => {});
  }

  function checkAdaptive() {
    const desired = chooseQuality(bw);
    if (desired !== currentQuality) {
      switchQuality(desired);
    }
  }

  function skipIfNeeded() {
    if (!autoSkipToggle.checked) return;
    const t = video.currentTime || 0;
    for (const [start, end] of learnedSegments) {
      if (t >= start && t <= end) {
        video.currentTime = end + 0.01;
        window.enhancedMetrics.skippedSegments.push({ from: start, to: end });
        break;
      }
    }
  }

  let baseNotes = [];
  const dynamicNotes = [];

  function renderNotes(notes) {
    notesContainer.innerHTML = '';
    notes.forEach((note, idx) => {
      const div = document.createElement('div');
      div.className = 'note';
      div.dataset.t = note.t;
      div.textContent = `[${note.t.toFixed(1)}s] ${note.text}`;
      div.addEventListener('mouseenter', () => {
        div.classList.add('active');
      });
      div.addEventListener('mouseleave', () => {
        div.classList.remove('active');
      });
      div.addEventListener('click', () => {
        jumpTo(note.t);
        setTimeout(() => {
          const diff = Math.abs((video.currentTime || 0) - note.t);
          window.enhancedMetrics.noteJumps.push({ noteIndex: idx, diff });
        }, 200);
      });
      notesContainer.appendChild(div);
    });
  }

  async function loadNotes() {
    try {
      const res = await fetch('/notes');
      const data = await res.json();
      baseNotes = data;
      renderNotes([...baseNotes, ...dynamicNotes]);
    } catch (err) {
      console.debug('failed to load notes', err);
      baseNotes = [
        { t: 5.2, text: 'Intro' },
        { t: 22.0, text: 'Concept' },
        { t: 40.5, text: 'Summary' }
      ];
      renderNotes([...baseNotes, ...dynamicNotes]);
    }
  }

  function jumpTo(t) {
    video.currentTime = t;
  }

  video.addEventListener('waiting', () => {
    stallStart = Date.now();
  });

  video.addEventListener('playing', () => {
    if (window.enhancedMetrics.timeToFirstFrameMs === null) {
      window.enhancedMetrics.timeToFirstFrameMs = performance.now() - window.__playerStartTime;
    }
    if (stallStart) {
      window.enhancedMetrics.stalls.push(Date.now() - stallStart);
      stallStart = null;
    }
  });

  video.addEventListener('timeupdate', () => {
    skipIfNeeded();
  });

  video.addEventListener('pause', saveProgress);
  video.addEventListener('ended', saveProgress);
  setInterval(saveProgress, 4000);

  window.__playerStartTime = performance.now();
  restoreProgress();
  applySavedSpeed();
  loadNotes();
  checkAdaptive();

  if (useMock) {
    // deterministic mock playback
    const start = performance.now();
    const mockDelay = Math.min(
      5000,
      Math.max(60, latency + jitter + 4000 / Math.max(200, bw))
    );
    setTimeout(() => {
      video.dispatchEvent(new Event('playing'));
      let current = video.currentTime || 0;
      const timer = setInterval(() => {
        current += video.playbackRate * 0.5;
        video.currentTime = current;
        video.dispatchEvent(new Event('timeupdate'));
        if (current > 240) clearInterval(timer);
      }, 500);
      window.enhancedMetrics.timeToFirstFrameMs = performance.now() - start;
    }, mockDelay);
  }

  window.playerApi = {
    setLearnedSegments(segments) {
      learnedSegments = segments || [];
    },
    getMetrics() {
      return window.enhancedMetrics;
    },
    forceQuality(q) {
      switchQuality(q);
    },
    markSegment(range) {
      learnedSegments.push(range);
    },
    addNote(note) {
      dynamicNotes.push(note);
      renderNotes([...baseNotes, ...dynamicNotes]);
    }
  };
})();
