// Enhanced player: resume, speed control, auto-skip, adaptive resolution, notes sync
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
let playing=false;
let currentTime=0;
let fps=1; // 1 fps sim
let timer=null;
let quality='360p';
let playbackRate=1.0;
let autoSkip=false;
let learnedSegments=[];
let notes=[];
let lastSavedTime=0;

function drawSVGText(text){
  const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='640' height='360'><rect width='100%' height='100%' fill='blue'/><text x='20' y='40' font-size='34' fill='white'>${text}</text></svg>`;
  const b64 = 'data:image/svg+xml;base64,'+btoa(svg);
  const img=new Image();
  img.onload=()=>{ctx.drawImage(img,0,0,canvas.width,canvas.height)};
  img.src=b64;
}

async function fetchFrame(t){
  const bandwidth = (window.networkProfile && window.networkProfile.bandwidth_kbps) ? window.networkProfile.bandwidth_kbps : 1000;
  const latency = (window.networkProfile && window.networkProfile.latency_ms) ? window.networkProfile.latency_ms : 50;
  const res = await fetch(`/stream/${quality}?t=${t}&bandwidth_kbps=${bandwidth}&latency_ms=${latency}`);
  const j = await res.json();
  drawSVGText(`t=${j.t} q=${quality}`);
}

async function play(){
  if (playing) return;
  playing = true;
  document.getElementById('status').innerText='Playing';
  let sampleCount=0, accumTTF=0;
  timer = setInterval(async () => {
    // auto-skip check
    if (autoSkip){
      for (const s of learnedSegments){
        if (currentTime>=s.start && currentTime<s.end){
          currentTime = s.end; // skip
        }
      }
    }
    const t0 = performance.now();
    await fetchFrame(currentTime);
    const ttf = performance.now() - t0;
    if (ttf>500){
      window.rebufferCount = (window.rebufferCount||0)+1;
    }
    sampleCount++;
    accumTTF += ttf;
    // adaptive resolution: if avg ttf > 700 ms, lower quality
    const avg = accumTTF / sampleCount;
    if (avg > 700 && quality!=='360p'){
      quality='360p';
    } else if (avg < 400 && quality!=='720p'){
      quality='720p';
    }
    currentTime += (1/fps) * playbackRate;
    if (currentTime - lastSavedTime > 5){
      // save progress
      navigator.sendBeacon('/progress', JSON.stringify({time: currentTime}));
      lastSavedTime=currentTime;
    }
  }, 1000/fps);
}
function pause(){
  clearInterval(timer);
  playing=false;
  document.getElementById('status').innerText='Paused';
  navigator.sendBeacon('/progress', JSON.stringify({time: currentTime}));
}

// speed
document.getElementById('rate').addEventListener('change', (e)=>{playbackRate=parseFloat(e.target.value);});
// auto-skip
document.getElementById('auto-skip').addEventListener('change', (e)=>{autoSkip=e.target.checked;});

// controls
document.getElementById('play').addEventListener('click', play);
document.getElementById('pause').addEventListener('click', pause);

// load learned segments and notes from server
async function loadMeta(){
  const r = await fetch('/meta');
  const j = await r.json();
  learnedSegments=j.learned || [];
  notes=j.notes || [];
  const notesDiv=document.getElementById('notes');
  for (const n of notes){
    const el=document.createElement('div');
    el.className='note';
    el.innerText=`${n.t} - ${n.text}`;
    el.addEventListener('mouseover', ()=>{currentTime=n.t; drawSVGText(`jumped to ${n.t}`);});
    el.addEventListener('click', ()=>{currentTime=n.t;});
    notesDiv.appendChild(el);
  }
}

// resume
async function resume(){
  const r = await fetch('/progress');
  const j = await r.json();
  if (j.time) currentTime=j.time;
}

window.addEventListener('load', async ()=>{await resume(); await loadMeta();});

window.player={play,pause,setRate:(r)=>{playbackRate=r;document.getElementById('rate').value=r;},getState:()=>({currentTime,playbackRate,learnedSegments,quality,rebufferCount:window.rebufferCount||0}),addLearned:(s)=>{learnedSegments.push(s);},setQuality:(q)=>{quality=q;}};

