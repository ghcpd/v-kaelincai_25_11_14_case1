(function () {
  const params = new URLSearchParams(window.location.search);
  const useMock = params.get('use_mock') === '1';
  const video = document.getElementById('courseVideo');
  const notesContainer = document.getElementById('notes');
  const testId = params.get('test_id') || 'manual';
  const bw = parseInt(params.get('bw_kbps') || '1000', 10);
  const latency = parseInt(params.get('latency_ms') || '50', 10);
  const jitter = parseInt(params.get('jitter_ms') || '20', 10);

  const sampleNotes = [
    { t: 5.2, text: 'Baseline intro' },
    { t: 22.0, text: 'Important concept' },
    { t: 40.5, text: 'Summary note' }
  ];

  function renderNotes() {
    notesContainer.innerHTML = '';
    sampleNotes.forEach((note) => {
      const div = document.createElement('div');
      div.className = 'note';
      div.textContent = `[${note.t.toFixed(1)}s] ${note.text}`;
      notesContainer.appendChild(div);
    });
  }
  renderNotes();

  window.playerMetrics = {
    testId,
    timeToFirstFrameMs: null,
    timeupdateEvents: [],
    networkProfile: { bw, latency, jitter },
    resumeSupported: false,
    playbackRate: 1.0
  };

  function simulatePlayback() {
    const start = performance.now();
    const jitterOffset = Math.max(0, jitter * 0.5 * Math.random());
    const fakeDelay = Math.min(
      6000,
      Math.max(80, latency + 8000 / Math.max(200, bw) + jitterOffset)
    );
    setTimeout(() => {
      window.playerMetrics.timeToFirstFrameMs = performance.now() - start;
      window.playerMetrics.playbackRate = video.playbackRate;
      video.dispatchEvent(new Event('playing'));
      let current = 0;
      const timer = setInterval(() => {
        current += 1;
        video.currentTime = current;
        const evt = new Event('timeupdate');
        video.dispatchEvent(evt);
        if (current >= 180) {
          clearInterval(timer);
        }
      }, 500);
    }, fakeDelay);
  }

  if (useMock) {
    simulatePlayback();
  } else {
    const start = performance.now();
    video.addEventListener('playing', () => {
      if (window.playerMetrics.timeToFirstFrameMs === null) {
        window.playerMetrics.timeToFirstFrameMs = performance.now() - start;
      }
    });
  }

  video.addEventListener('timeupdate', () => {
    window.playerMetrics.timeupdateEvents.push(video.currentTime);
  });
})();
