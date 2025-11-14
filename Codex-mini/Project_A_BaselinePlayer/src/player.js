const duration = 300;
const state = {
  currentTime: 0,
  playbackRate: 1,
  playing: false,
  timeStart: null,
  lastRendered: null,
};

const metrics = {
  timeToFirstFrame: null,
  stalls: [],
  firstFrameLogged: false,
  history: [],
};

const playButton = document.getElementById("play-btn");
const pauseButton = document.getElementById("pause-btn");
const timeDisplay = document.getElementById("time-display");
const slider = document.getElementById("time-slider");
const notesList = document.getElementById("notes");

let timerId = null;

function tick() {
  state.currentTime = Math.min(duration, state.currentTime + state.playbackRate * 0.5);
  renderTime();
  if (state.currentTime >= duration) {
    clearInterval(timerId);
    state.playing = false;
  }
}

function renderTime() {
  timeDisplay.textContent = `${state.currentTime.toFixed(1)}s / ${duration}s`;
  slider.value = state.currentTime;
  state.lastRendered = performance.now();
}

function startPlay() {
  if (state.playing) return;
  state.playing = true;
  if (!metrics.firstFrameLogged) {
    metrics.timeToFirstFrame = performance.now();
    metrics.firstFrameLogged = true;
  }
  metrics.history.push({ event: "play", t: state.currentTime });
  timerId = setInterval(tick, 500);
}

function pausePlay() {
  if (!state.playing) return;
  state.playing = false;
  clearInterval(timerId);
  metrics.history.push({ event: "pause", t: state.currentTime });
}

playButton.addEventListener("click", () => startPlay());
pauseButton.addEventListener("click", () => pausePlay());
slider.addEventListener("input", (event) => {
  state.currentTime = Number(event.target.value);
  renderTime();
});

fetch("/api/notes")
  .then((response) => response.json())
  .then((notes) => {
    notes.forEach((note) => {
      const li = document.createElement("li");
      li.textContent = `${note.t}s - ${note.text}`;
      notesList.appendChild(li);
    });
  });

window.baselinePlayer = {
  getState: () => ({ ...state }),
  getMetrics: () => ({ ...metrics, currentTime: state.currentTime }),
  resume: () => {
    const stored = localStorage.getItem("baseline_last_time");
    if (stored) {
      state.currentTime = Number(stored);
      renderTime();
    }
  },
  storeProgress: () => {
    localStorage.setItem("baseline_last_time", state.currentTime);
  },
  runScenario: async (scenario) => {
    const start = performance.now();
    metrics.history.push({ event: "scenario", scenario: scenario.id, start });
    if (!state.playing) {
      startPlay();
    }
    if (scenario.network_profile && scenario.network_profile.latency) {
      const delay = scenario.network_profile.latency * 1000;
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
    renderTime();
    metrics.history.push({ event: "scenario_end", scenario: scenario.id, t: state.currentTime });
    return {
      scenario: scenario.id,
      resumeAccuracy: Math.abs(state.currentTime - (scenario.expected?.resume_time || 0)),
      timeToFirstFrame: metrics.timeToFirstFrame,
      playbackRate: state.playbackRate,
    };
  },
};
