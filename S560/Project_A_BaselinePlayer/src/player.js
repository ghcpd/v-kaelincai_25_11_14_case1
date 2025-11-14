// Baseline player script: minimal behavior
(function(){
  const params = new URLSearchParams(window.location.search);
  const useMock = params.get('use_mock') === '1';
  const video = document.getElementById('courseVideo');
  const notesDiv = document.getElementById('notes');

  // Render sample notes (not time-synced in baseline)
  const sampleNotes = [
    {t: 5.2, text: 'Intro'},
    {t: 22.0, text: 'Important concept'},
    {t: 40.5, text: 'Summary'},
  ];

  sampleNotes.forEach(n => {
    const div = document.createElement('div');
    div.className = 'note';
    div.textContent = `[${n.t.toFixed(1)}s] ${n.text}`;
    notesDiv.appendChild(div);
  });

  // Expose event hooks to tests via window.playerMetrics
  window.playerMetrics = {
    timeToFirstFrameMs: null,
    onPlayTimeMs: null,
    timeupdate_events: []
  };

  if (useMock) {
    console.debug('Using mock video behavior for test');
    // Simulate network profile via query params
    const bw = parseInt(params.get('bw_kbps') || '1000', 10);
    const latency = parseInt(params.get('latency_ms') || '20', 10);
    const start = performance.now();
    // fake loading delay proportional to latency and inverse of bandwidth
    const fakeLoadMs = Math.min(5000, Math.max(50, Math.floor(latency + 8000 / Math.max(1, bw))));
    setTimeout(() => {
      // fire loadedmetadata/playing events
      const ev = new Event('playing');
      video.dispatchEvent(ev);
      window.playerMetrics.timeToFirstFrameMs = performance.now() - start;
      // simulate timeupdate events
      let t = 0;
      window.playerMetrics.onPlayTimeMs = performance.now();
      const intervalId = setInterval(() => {
        t += 1;
        window.playerMetrics.timeupdate_events.push({t});
        const ev2 = new Event('timeupdate');
        video.currentTime = t; // fake property
        video.dispatchEvent(ev2);
        if (t > 60) clearInterval(intervalId);
      }, 500);
    }, fakeLoadMs);
  } else {
    const start = performance.now();
    video.addEventListener('playing', () => {
      if (window.playerMetrics.timeToFirstFrameMs === null) {
        window.playerMetrics.timeToFirstFrameMs = performance.now() - start;
      }
      window.playerMetrics.onPlayTimeMs = performance.now();
    });

    video.addEventListener('timeupdate', () => {
      window.playerMetrics.timeupdate_events.push({t: video.currentTime});
    });
  }

  // Baseline: just log progress updates to console (no resume store)
  video.addEventListener('timeupdate', () => {
    // log every 5 seconds
    if (Math.floor((video.currentTime || 0)) % 5 === 0) {
      console.debug('progress', {t: video.currentTime});
    }
  });
})();
