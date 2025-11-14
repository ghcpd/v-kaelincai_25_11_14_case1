// Baseline player: simple frame fetch, no resume, no speed control or skip.
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
let playing=false;
let currentTime=0;
let fps=1; // 1 frame per second to keep simple
let timer=null;
let quality='360p';

async function fetchFrame(t) {
  // fetch a JSON frame from server
  const bandwidth = (window.networkProfile && window.networkProfile.bandwidth_kbps) ? window.networkProfile.bandwidth_kbps : 1000;
  const latency = (window.networkProfile && window.networkProfile.latency_ms) ? window.networkProfile.latency_ms : 50;
  const res = await fetch(`/stream/${quality}?t=${t}&bandwidth_kbps=${bandwidth}&latency_ms=${latency}`);
  const j = await res.json();
  const img = new Image();
  img.onload = () => {
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
  };
  img.src = j.data;
}

async function play() {
  if (playing) return;
  playing = true;
  document.getElementById('status').innerText='Playing';
  timer = setInterval(async () => {
    await fetchFrame(currentTime);
    currentTime += 1/fps;
  }, 1000/fps);
}
function pause(){
  clearInterval(timer);
  playing=false;
  document.getElementById('status').innerText='Paused';
}

document.getElementById('play').addEventListener('click', play);
document.getElementById('pause').addEventListener('click', pause);

// Dummy notes display (static). Hover does nothing in baseline.
const notesDiv=document.getElementById('notes');
notesDiv.innerHTML='<h3>Notes</h3><ul><li>100.5 - Important</li><li>120.5 - Key point</li></ul>';

// Expose for tests
window.player={play,pause,getState:()=>({currentTime,playing}),setQuality:(q)=>{quality=q;},reset:()=>{currentTime=0;}};
