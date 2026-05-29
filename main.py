<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Duct Viewer</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;}
html,body{height:100%;display:flex;flex-direction:column;overflow:hidden;font-family:system-ui,sans-serif;background:#0f172a;color:#f1f5f9;-webkit-user-select:none;user-select:none;}
#hdr{height:50px;min-height:50px;background:#1e293b;display:flex;align-items:center;gap:10px;padding:0 14px;border-bottom:1px solid #334155;flex-shrink:0;}
.t{font-size:14px;font-weight:600;}
.pill{border:1px solid #334155;border-radius:20px;padding:3px 10px;font-size:11px;color:#64748b;margin-left:auto;white-space:nowrap;}
#sr{height:56px;min-height:56px;background:#1e293b;display:flex;align-items:center;gap:8px;padding:0 14px;border-bottom:1px solid #334155;flex-shrink:0;}
#si{flex:1;height:40px;padding:0 14px;border-radius:8px;border:1.5px solid #334155;background:#0f172a;color:#f1f5f9;font-size:16px;font-family:'Courier New',monospace;outline:none;text-transform:uppercase;}
#si::placeholder{text-transform:none;color:#475569;font-family:system-ui;font-size:14px;}
#si:focus{border-color:#1D9E75;}
#fb{height:40px;padding:0 20px;border-radius:8px;border:none;background:#1D9E75;color:#fff;font-size:14px;font-weight:700;cursor:pointer;flex-shrink:0;touch-action:manipulation;}
#strow{height:30px;min-height:30px;display:flex;align-items:center;padding:0 14px;font-size:12px;color:#64748b;flex-shrink:0;}
#dwgbar{background:#0f172a;display:flex;align-items:center;gap:6px;padding:6px 12px;border-bottom:1px solid #1a2332;overflow-x:auto;flex-shrink:0;}
.dtab{padding:5px 12px;border-radius:20px;border:1px solid #334155;background:transparent;color:#64748b;font-size:11px;cursor:pointer;white-space:nowrap;flex-shrink:0;touch-action:manipulation;}
.dtab.active{background:#1e293b;color:#f1f5f9;border-color:#475569;}
#dupBox{display:none;background:#1e293b;border:1px solid #334155;border-radius:10px;padding:12px 14px;margin:0 14px;flex-shrink:0;}
#dupBox.open{display:block;}
#dupBox p{font-size:12px;color:#94a3b8;margin-bottom:8px;}
.dup-btns{display:flex;flex-wrap:wrap;gap:6px;}
.dup-btn{padding:6px 14px;border-radius:6px;border:1px solid #334155;background:#0f172a;color:#f1f5f9;font-size:13px;cursor:pointer;touch-action:manipulation;}
.dup-btn:active{background:#1D9E75;border-color:#1D9E75;}
#vp{flex:1;overflow:hidden;position:relative;background:#1a2332;touch-action:none;cursor:grab;}
#iw{position:absolute;transform-origin:0 0;will-change:transform;}
#bi{display:block;max-width:none;}
#ring{position:absolute;border:3px solid #facc15;border-radius:50%;pointer-events:none;display:none;box-shadow:0 0 16px rgba(250,204,21,0.6);}
#ring.on{display:block;animation:pulse 1.1s ease-in-out infinite;}
@keyframes pulse{0%,100%{transform:translate(-50%,-50%) scale(1);opacity:1;}55%{transform:translate(-50%,-50%) scale(1.2);opacity:0.65;}}
#dl{position:absolute;background:#facc15;color:#0f172a;font-weight:800;font-family:'Courier New',monospace;font-size:13px;padding:4px 12px;border-radius:5px;display:none;pointer-events:none;white-space:nowrap;transform:translate(-50%,-160%);}
#dl.on{display:block;}
#zc{position:absolute;bottom:16px;right:16px;display:flex;flex-direction:column;gap:6px;}
.zb{width:46px;height:46px;border-radius:9px;border:1px solid #2d3f55;background:#1e293b;color:#f1f5f9;font-size:24px;cursor:pointer;display:flex;align-items:center;justify-content:center;touch-action:manipulation;}
#ld{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;background:#1a2332;z-index:10;}
#ld p{font-size:13px;color:#64748b;}
.spin{width:32px;height:32px;border:3px solid rgba(255,255,255,0.1);border-top-color:#1D9E75;border-radius:50%;animation:spin 0.8s linear infinite;}
@keyframes spin{to{transform:rotate(360deg);}}
#empty{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;background:#1a2332;}
#empty p{font-size:14px;color:#64748b;text-align:center;max-width:240px;line-height:1.6;}
.ok{color:#22c55e;font-weight:500;}.err{color:#ef4444;}
.found-badge{display:inline-flex;align-items:center;background:#1e293b;border:1px solid #334155;border-radius:20px;padding:2px 9px;font-size:11px;color:#94a3b8;margin-left:8px;}
</style>
</head>
<body>
<div id="hdr">
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1D9E75" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
  <span class="t">Duct Viewer</span>
  <span class="pill" id="pill">Loading...</span>
</div>
<div id="sr">
  <input type="text" id="si" placeholder="Enter duct ID, e.g. 02-0044" autocomplete="off" autocorrect="off" spellcheck="false"/>
  <button id="fb" onclick="find()">Find</button>
</div>
<div id="strow"><span id="st">Loading drawings...</span></div>
<div id="dwgbar"></div>
<div id="dupBox"><p id="dupMsg"></p><div class="dup-btns" id="dupBtns"></div></div>
<div id="vp">
  <div id="ld"><div class="spin"></div><p id="ldTxt">Loading...</p></div>
  <div id="iw"><img id="bi" alt="Drawing"/><div id="ring"></div><div id="dl"></div></div>
  <div id="zc">
    <button class="zb" onclick="z(1.25)">+</button>
    <button class="zb" onclick="z(0.8)">&#x2212;</button>
    <button class="zb" onclick="fit()" style="font-size:12px;font-weight:600;">fit</button>
  </div>
  <div id="empty" style="display:none;">
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#334155" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><polyline points="13 2 13 9 20 9"/></svg>
    <p>No drawings available yet.<br>Contact your administrator.</p>
  </div>
</div>

<script>
let DRAWINGS = [], M = {}, curDi = 0;
let sc=1, px=0, py=0, drag=false, ds={}, pd=0, fitted=false;
const img=document.getElementById('bi'), wrap=document.getElementById('iw'), vp=document.getElementById('vp');
const ring=document.getElementById('ring'), dl=document.getElementById('dl'), st=document.getElementById('st');
const dupBox=document.getElementById('dupBox');

// Load data from API
fetch('/static/drawings.json')
  .then(r => r.json())
  .then(rawDrawings => {
    // Build global marker lookup from drawings array
    const allMarkers = {};
    rawDrawings.forEach((d, di) => {
      Object.entries(d.markers).forEach(([id, pos]) => {
        if (!allMarkers[id]) allMarkers[id] = [];
        allMarkers[id].push({x: pos.x, y: pos.y, di});
      });
    });
    DRAWINGS = rawDrawings;
    M = allMarkers;
    if (DRAWINGS.length === 0) {
      document.getElementById('ld').style.display = 'none';
      document.getElementById('empty').style.display = 'flex';
      st.textContent = 'No drawings available';
      document.getElementById('pill').textContent = '0 drawings';
      return;
    }
    const total = DRAWINGS.reduce((s,d) => s+d.count, 0);
    document.getElementById('pill').textContent = total + ' ducts · ' + DRAWINGS.length + ' drawings';
    st.textContent = 'Search across all ' + DRAWINGS.length + ' drawings — ' + total + ' ducts total';
    buildTabs();
    switchDrawing(0);
  })
  .catch(() => {
    st.innerHTML = '<span class="err">Failed to load drawings</span>';
    document.getElementById('ld').style.display = 'none';
  });

function buildTabs() {
  const bar = document.getElementById('dwgbar');
  bar.innerHTML = '';
  DRAWINGS.forEach((d, i) => {
    const btn = document.createElement('button');
    btn.className = 'dtab' + (i===curDi ? ' active' : '');
    btn.textContent = d.name + ' (' + d.count + ')';
    btn.onclick = () => switchDrawing(i);
    bar.appendChild(btn);
  });
  if (DRAWINGS.length <= 1) bar.style.display = 'none';
}

function switchDrawing(di) {
  curDi = di;
  ring.classList.remove('on'); dl.classList.remove('on'); dupBox.classList.remove('open');
  fitted = false;
  document.getElementById('ld').style.display = 'flex';
  document.getElementById('ldTxt').textContent = 'Loading ' + DRAWINGS[di].name + '...';
  buildTabs();
  img.onload = () => requestAnimationFrame(fit);
  img.src = DRAWINGS[di].img;
}

function fit() {
  const w=vp.offsetWidth, h=vp.offsetHeight;
  if (!w||!h||!img.naturalWidth) { requestAnimationFrame(fit); return; }
  sc = Math.min(w/img.naturalWidth, h/img.naturalHeight) * 0.97;
  px = (w - img.naturalWidth*sc) / 2;
  py = (h - img.naturalHeight*sc) / 2;
  ap(); document.getElementById('ld').style.display = 'none'; fitted = true;
}
function ap(s) { wrap.style.transition=s?'transform 0.4s ease':'none'; wrap.style.transform='translate('+px+'px,'+py+'px) scale('+sc+')'; wrap.style.transformOrigin='0 0'; }
function z(f) { const w=vp.offsetWidth,h=vp.offsetHeight,cx=w/2,cy=h/2,p=sc; sc=Math.max(0.1,Math.min(20,sc*f)); px=cx-(cx-px)*(sc/p); py=cy-(cy-py)*(sc/p); ap(); }

vp.addEventListener('mousedown', e=>{ drag=true; ds={x:e.clientX,y:e.clientY,px,py}; vp.style.cursor='grabbing'; });
document.addEventListener('mousemove', e=>{ if(!drag)return; px=ds.px+e.clientX-ds.x; py=ds.py+e.clientY-ds.y; ap(); });
document.addEventListener('mouseup', ()=>{ drag=false; vp.style.cursor='grab'; });
vp.addEventListener('wheel', e=>{ e.preventDefault(); const r=vp.getBoundingClientRect(),mx=e.clientX-r.left,my=e.clientY-r.top,f=e.deltaY<0?1.1:0.91,p=sc; sc=Math.max(0.1,Math.min(20,sc*f)); px=mx-(mx-px)*(sc/p); py=my-(my-py)*(sc/p); ap(); }, {passive:false});
let touches=[];
vp.addEventListener('touchstart', e=>{ touches=Array.from(e.touches); if(e.touches.length===1){drag=true;ds={x:e.touches[0].clientX,y:e.touches[0].clientY,px,py};}else if(e.touches.length===2){pd=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);drag=false;} });
vp.addEventListener('touchmove', e=>{ e.preventDefault(); const t=Array.from(e.touches); if(t.length===1&&drag){px=ds.px+t[0].clientX-ds.x;py=ds.py+t[0].clientY-ds.y;ap();}else if(t.length===2){const d=Math.hypot(t[0].clientX-t[1].clientX,t[0].clientY-t[1].clientY),f=d/pd,r=vp.getBoundingClientRect(),cx=(t[0].clientX+t[1].clientX)/2-r.left,cy=(t[0].clientY+t[1].clientY)/2-r.top,p=sc;sc=Math.max(0.1,Math.min(20,sc*f));px=cx-(cx-px)*(sc/p);py=cy-(cy-py)*(sc/p);ap();pd=d;} }, {passive:false});
vp.addEventListener('touchend', ()=>{ drag=false; });
window.addEventListener('resize', ()=>{ if(fitted) fit(); });
document.getElementById('si').addEventListener('keydown', e=>{ if(e.key==='Enter') find(); });

function highlight(mk, q, name) {
  const ix=mk.x*img.naturalWidth, iy=mk.y*img.naturalHeight, sz=80;
  ring.style.width=sz+'px'; ring.style.height=sz+'px';
  ring.style.left=ix+'px'; ring.style.top=iy+'px';
  dl.style.left=ix+'px'; dl.style.top=iy+'px'; dl.textContent=q;
  ring.classList.add('on'); dl.classList.add('on');
  sc=Math.min(6,Math.max(3,sc)); px=vp.offsetWidth/2-ix*sc; py=vp.offsetHeight/2-iy*sc; ap(true);
  st.innerHTML='<span class="ok">&#10003; '+q+'</span><span class="found-badge">'+name+'</span>';
}

function find() {
  const q = document.getElementById('si').value.trim().toUpperCase().replace(/\s+/g,'');
  if (!q) return;
  dupBox.classList.remove('open');
  const hits = (M[q]||[]);
  if (hits.length===0) { st.innerHTML='<span class="err">&#10060; "'+q+'" not found</span>'; ring.classList.remove('on'); dl.classList.remove('on'); return; }
  if (hits.length===1) {
    const mk=hits[0];
    const go=()=>highlight(mk,q,DRAWINGS[mk.di].name);
    if(mk.di!==curDi){switchDrawing(mk.di);setTimeout(go,500);}else go();
    return;
  }
  st.innerHTML='<span style="color:#f59e0b;">Found in '+hits.length+' drawings — choose:</span>';
  document.getElementById('dupMsg').textContent='"'+q+'" found in:';
  const btns=document.getElementById('dupBtns'); btns.innerHTML='';
  hits.forEach(mk=>{
    const btn=document.createElement('button');
    btn.className='dup-btn'; btn.textContent=DRAWINGS[mk.di].name;
    btn.onclick=()=>{ dupBox.classList.remove('open'); const go=()=>highlight(mk,q,DRAWINGS[mk.di].name); if(mk.di!==curDi){switchDrawing(mk.di);setTimeout(go,500);}else go(); };
    btns.appendChild(btn);
  });
  dupBox.classList.add('open');
}
</script>
</body>
</html>
