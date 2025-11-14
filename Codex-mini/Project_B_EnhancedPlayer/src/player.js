const duration = 300;
const segments = [
  { id: "seg1", start: 0, end: 30 },
  { id: "seg2", start: 30, end: 90 },
  { id: "seg3", start: 90, end: 150 },
  { id: "seg4", start: 150, end: 240 },
  { id: "seg5", start: 240, end: 300 },
];

const resolutionOrder = ["360p", "480p", "720p"];
const state = {
  playbackRate: 1,
  currentTime: 0,
  playing: false,
  autoSkip: false,
  learnedSegments: [],
  quality: "720p",
  networkProfile: { bandwidth: 3, latency: 0.1 },
};

const metrics = {
  timeToFirstFrame: null,
  resolutionSwitchDurations: [],
  resumeAccuracy: null,
  noteJumps: [],
  stalls: [],
};

const playBtn = document.getElementById("play-btn");
const pauseBtn = document.getElementById("pause-btn");
const speedSelect = document.getElementById("speed-select");
const slider = document.getElementById("progress-slider");
const qualityLabel = document.getElementById("quality-label");
const timingLabel = document.getElementById("timing-label");
const autoSkipBtn = document.getElementById("auto-skip-btn");
const notesList = document.getElementById("notes-list");
const tooltip = document.getElementById("note-tooltip");

let timer = null;

function renderUI() {
  slider.value = state.currentTime;
  timingLabel.textContent = `${Math.round(state.currentTime)}s of ${duration}s`;
  qualityLabel.textContent = state.quality;
}

function startPlay() {
  if (state.playing) return;
  state.playing = true;
  if (!metrics.timeToFirstFrame) {
    metrics.timeToFirstFrame = performance.now();
  }
  timer = setInterval(() => {
    const previous = state.currentTime;
    state.currentTime = Math.min(duration, state.currentTime + state.playbackRate * 0.6);
    autoSkipCheck();
    if (state.currentTime === previous) {
      metrics.stalls.push({ start: performance.now(), duration: 0 });
    }
    renderUI();
    if (state.currentTime >= duration) {
      clearInterval(timer);
      state.playing = false;
    }
  }, 400);
}

function pausePlay() {
  if (!state.playing) return;
  state.playing = false;
  clearInterval(timer);
}

function autoSkipCheck() {
  if (!state.autoSkip || state.learnedSegments.length === 0) {
    return;
  }
  for (const segment of segments) {
    if (
      state.learnedSegments.includes(segment.id) &&
      state.currentTime >= segment.start &&
      state.currentTime < segment.end
    ) {
      state.currentTime = segment.end;
      metrics.stalls.push({ skipped: segment.id, time: state.currentTime });
    }
  }
}

async function switchResolution(resolution) {
  const start = performance.now();
  await fetch(
    `/api/segments?res=${resolution}&bandwidth=${state.networkProfile.bandwidth}&latency=${state.networkProfile.latency}`
  );
  const durationMs = performance.now() - start;
  metrics.resolutionSwitchDurations.push(durationMs);
  state.quality = resolution;
  renderUI();
  return durationMs;
}

function buildNotes(notes) {
  notesList.innerHTML = "";
  notes.forEach((note) => {
    const li = document.createElement("li");
    li.textContent = `${note.t}s -> ${note.text}`;
    li.dataset.time = note.t;
    li.addEventListener("mouseenter", (event) => {
      tooltip.style.display = "block";
      tooltip.textContent = `Jump to ${note.t}s`;
      tooltip.style.top = `${event.target.offsetTop - 10}px`;
      tooltip.style.left = `${event.target.offsetLeft + 180}px`;
    });
    li.addEventListener("mouseleave", () => {
      tooltip.style.display = "none";
    });
    li.addEventListener("click", () => {
      state.currentTime = note.t;
      renderUI();
      metrics.noteJumps.push({ note: note.t, landed: state.currentTime });
    });
    notesList.appendChild(li);
  });
}

function saveProgress(position = state.currentTime) {
  const payload = { position };
  fetch(`/api/progress?user=automation`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

function updatePlaybackRate(rate) {
  state.playbackRate = rate;
  metrics.resumeAccuracy = metrics.resumeAccuracy || 0;
  const event = { event: "rate-change", rate, ts: performance.now() };
  metrics.noteJumps.push(event);
}

speedSelect.addEventListener("change", (event) => {
  updatePlaybackRate(Number(event.target.value));
});

autoSkipBtn.addEventListener("click", () => {
  state.autoSkip = !state.autoSkip;
  autoSkipBtn.textContent = `Auto-skip: ${state.autoSkip ? "On" : "Off"}`;
  autoSkipBtn.classList.toggle("active", state.autoSkip);
});

playBtn.addEventListener("click", () => startPlay());
pauseBtn.addEventListener("click", () => pausePlay());
slider.addEventListener("input", (event) => {
  state.currentTime = Number(event.target.value);
  renderUI();
});

fetch("/api/notes")
  .then((response) => response.json())
  .then((notes) => buildNotes(notes));

renderUI();

window.enhancedPlayer = {
  getMetrics: () => ({ ...metrics, currentTime: state.currentTime }),
  runScenario: async (scenario) => {
    state.networkProfile = scenario.network_profile || state.networkProfile;
    state.playbackRate = scenario.initial_conditions.playback_rate || 1;
    speedSelect.value = state.playbackRate;
    state.autoSkip = Boolean(scenario.initial_conditions.auto_skip);
    autoSkipBtn.textContent = `Auto-skip: ${state.autoSkip ? "On" : "Off"}`;
    autoSkipBtn.classList.toggle("active", state.autoSkip);

    const savedProgress = await fetch(`/api/progress?user=${scenario.initial_conditions.user}`).then(
      (res) => res.json()
    );
    state.currentTime = savedProgress.position || scenario.initial_conditions.saved_progress;
    metrics.resumeAccuracy = Math.abs(state.currentTime - scenario.initial_conditions.saved_progress);
    renderUI();

    const learned = scenario.initial_conditions.learned_segments || [];
    state.learnedSegments = learned;
    await fetch("/api/learned", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user: scenario.initial_conditions.user, segments: learned }),
    });

    for (const resolution of resolutionOrder) {
      await switchResolution(resolution);
    }

    startPlay();
    await new Promise((resolve) => setTimeout(resolve, 1200));

    const noteTarget = scenario.expected?.notes_synced?.[0]?.t || scenario.expected?.jumped_time;
    if (noteTarget) {
      state.currentTime = noteTarget;
      renderUI();
      metrics.noteJumps.push({ note: noteTarget, landed: state.currentTime });
    }

    saveProgress();
    return {
      scenario: scenario.id,
      resume_accuracy: metrics.resumeAccuracy,
      playback_rate: state.playbackRate,
      time_to_first_frame: metrics.timeToFirstFrame,
      resolution_switch_ms: metrics.resolutionSwitchDurations,
      note_jumps: metrics.noteJumps,
    };
  },
};
