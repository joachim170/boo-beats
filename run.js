/* Boo Run – bana 1 "Rua" (brasiliansk gatufotboll). 3D-runner byggd på Three.js (r128, global THREE).
   Styrs av bollens fil (0/1/2) och "hopp" (chapéu = lyft bollen). Allt ritas här; HUD ritas av index.html. */
(function(){
'use strict';
const LX=[-1.8,0,1.8];            // filernas x-läge
const ROAD_HALF=3, WALK=2.2;      // gata och trottoar
const SPAWN_Z=-115, KILL_Z=14;

let R=null,scene,cam,canvas,clock=0;
let ac=null,musicTimer=null,nextNote=0,step16=0;
const S={running:false,over:false,countdown:0,speed:0,dist:0,coins:0,canetas:0,chapeus:0,gols:0,lives:3,score:0,
  invuln:0,hitFlash:0,popups:[],t:0,jumpEnabled:true,lane:1};
let px=0,jumpT=-1,legPhase=0,spawnAcc=0,elapsed=0,lastGoalAt=0;
const JUMP_DUR=.85;

/* ---------- texturer (ritade i canvas, inga externa bilder) ---------- */
function ctex(w,h,draw,rx=1,ry=1){const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');draw(x,w,h);const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(rx,ry);t.anisotropy=4;return t}
function rnd(a,b){return a+Math.random()*(b-a)}
function pick(a){return a[Math.floor(Math.random()*a.length)]}
const PASTEL=['#f4a261','#2a9d8f','#e9c46a','#e76f51','#8ecae6','#ffb703','#fb8500','#90be6d','#f28482','#84a59d','#cdb4db','#ffd166','#06d6a0','#ef476f'];

function cobble(){return ctex(256,256,(x,w,h)=>{x.fillStyle='#6d6259';x.fillRect(0,0,w,h);
  for(let r=0;r<10;r++)for(let c=0;c<9;c++){const sx=c*30+(r%2?15:0)-8,sy=r*26;const g=rnd(95,150);x.fillStyle=`rgb(${g+8},${g},${g-10})`;
    x.beginPath();x.ellipse(sx+14,sy+12,13,11,rnd(-.3,.3),0,7);x.fill();x.fillStyle='rgba(255,255,255,.08)';x.beginPath();x.ellipse(sx+11,sy+9,6,4,0,0,7);x.fill()}},2.4,85)}
function calcadao(){ // Copacabanas vågmönster
  return ctex(256,256,(x,w,h)=>{x.fillStyle='#f3efe6';x.fillRect(0,0,w,h);x.fillStyle='#1d1d1f';
    for(let k=-1;k<5;k++){x.beginPath();for(let y=0;y<=h;y+=4){const xx=w/2+Math.sin((y/h)*Math.PI*2+k*Math.PI)*w*.28;x.lineTo(xx+(k%2?-30:30),y)}for(let y=h;y>=0;y-=4){const xx=w/2+Math.sin((y/h)*Math.PI*2+k*Math.PI)*w*.28;x.lineTo(xx+(k%2?-30:30)+22,y)}x.closePath();if(k===1||k===3)x.fill()}},1,70)}
function facade(color){return ctex(128,256,(x,w,h)=>{x.fillStyle=color;x.fillRect(0,0,w,h);
  x.fillStyle='rgba(0,0,0,.08)';for(let i=0;i<40;i++)x.fillRect(rnd(0,w),rnd(0,h),rnd(2,8),rnd(1,3));
  const win=pick(['#2b3a55','#3d5a80','#1b263b']);for(let fy=24;fy<h-60;fy+=58)for(let fx=16;fx<w-30;fx+=56){x.fillStyle='#fff8';x.fillRect(fx-3,fy-3,32,40);x.fillStyle=win;x.fillRect(fx,fy,26,34);x.fillStyle=pick(PASTEL);x.fillRect(fx-4,fy+34,34,4)}
  x.fillStyle='#5a3d2b';x.fillRect(w/2-14,h-52,28,52);
  if(Math.random()<.55){for(let i=0;i<4;i++){x.fillStyle=pick(PASTEL);x.globalAlpha=.85;x.beginPath();x.ellipse(rnd(10,w-10),rnd(h-80,h-20),rnd(10,26),rnd(6,14),rnd(0,3),0,7);x.fill()}x.globalAlpha=1;x.strokeStyle='#111';x.lineWidth=3;x.beginPath();x.moveTo(12,h-40);for(let i=0;i<6;i++)x.quadraticCurveTo(20+i*18,h-70+Math.random()*30,30+i*18,h-44);x.stroke()}
})}
function ballTex(){return ctex(256,128,(x,w,h)=>{x.fillStyle='#fafafa';x.fillRect(0,0,w,h);x.fillStyle='#151515';
  const pts=[[.1,.5],[.3,.2],[.3,.8],[.5,.5],[.7,.2],[.7,.8],[.9,.5],[.0,.1],[.5,.05],[1,.1],[.5,.95]];
  for(const[u,v]of pts){x.beginPath();for(let k=0;k<5;k++){const a=k/5*Math.PI*2-Math.PI/2;x.lineTo(u*w+Math.cos(a)*16,v*h+Math.sin(a)*14)}x.closePath();x.fill()}})}
function skyTex(){return ctex(8,256,(x,w,h)=>{const g=x.createLinearGradient(0,0,0,h);g.addColorStop(0,'#3a8fd9');g.addColorStop(.55,'#9fd3ff');g.addColorStop(1,'#ffe1b0');x.fillStyle=g;x.fillRect(0,0,w,h)})}
function hillsTex(){return ctex(1024,256,(x,w,h)=>{x.clearRect(0,0,w,h);
  const layer=(col,base,amp,seed)=>{x.fillStyle=col;x.beginPath();x.moveTo(0,h);for(let i=0;i<=w;i+=8){const y=base-amp*(Math.sin(i*.006+seed)*.5+Math.sin(i*.017+seed*2)*.3+Math.sin(i*.041)*.1);x.lineTo(i,y)}x.lineTo(w,h);x.closePath();x.fill()};
  layer('#7fa7b8',150,70,1);
  // sockertopp-liknande berg
  x.fillStyle='#5f8a7a';x.beginPath();x.moveTo(640,h);x.quadraticCurveTo(700,40,760,60);x.quadraticCurveTo(800,90,830,h);x.fill();
  layer('#4f7d5c',205,45,4);
  for(let i=0;i<220;i++){x.fillStyle=pick(PASTEL);x.globalAlpha=.75;x.fillRect(rnd(0,w),rnd(185,250),rnd(3,7),rnd(3,6))}x.globalAlpha=1;
},1,1)}

/* ---------- material och geometrier ---------- */
const M={},G={};
function mats(){
  M.road=new THREE.MeshLambertMaterial({map:cobble()});
  M.walk=new THREE.MeshLambertMaterial({map:calcadao()});
  M.curb=new THREE.MeshLambertMaterial({color:'#d8d2c4'});
  M.facades=PASTEL.map(c=>new THREE.MeshLambertMaterial({map:facade(c)}));
  M.roof=new THREE.MeshLambertMaterial({color:'#b5522f'});
  M.skin=new THREE.MeshLambertMaterial({color:'#b5774e'});
  M.hair=new THREE.MeshLambertMaterial({color:'#1b1410'});
  M.shirt=new THREE.MeshLambertMaterial({color:'#ffd21f'});
  M.trim=new THREE.MeshLambertMaterial({color:'#16a34a'});
  M.shorts=new THREE.MeshLambertMaterial({color:'#1e40af'});
  M.sock=new THREE.MeshLambertMaterial({color:'#f5f5f5'});
  M.shoe=new THREE.MeshLambertMaterial({color:'#111'});
  M.def=new THREE.MeshLambertMaterial({color:'#dc2626'});
  M.defShorts=new THREE.MeshLambertMaterial({color:'#111827'});
  M.wood=new THREE.MeshLambertMaterial({color:'#8b5a2b'});
  M.tire=new THREE.MeshLambertMaterial({color:'#222'});
  M.coin=new THREE.MeshLambertMaterial({color:'#ffc400',emissive:'#5a3a00'});M.coinEdge=new THREE.MeshLambertMaterial({color:'#b8860b'});
  M.white=new THREE.MeshLambertMaterial({color:'#ffffff'});
  M.net=new THREE.MeshBasicMaterial({color:'#ffffff',wireframe:true,transparent:true,opacity:.5});
  M.ball=new THREE.MeshLambertMaterial({map:ballTex()});
  M.shadow=new THREE.MeshBasicMaterial({color:'#000',transparent:true,opacity:.28,depthWrite:false});
  M.green=new THREE.MeshLambertMaterial({color:'#2f7d32'});
  M.trunk=new THREE.MeshLambertMaterial({color:'#7a5230'});
  G.box=new THREE.BoxGeometry(1,1,1);
  G.cyl=new THREE.CylinderGeometry(.5,.5,1,12);
  G.sph=new THREE.SphereGeometry(.5,16,12);
  G.disc=new THREE.CircleGeometry(.5,20);
  G.coin=new THREE.CylinderGeometry(.26,.26,.07,20);
  G.tri=new THREE.BufferGeometry();G.tri.setAttribute('position',new THREE.Float32BufferAttribute([-.18,0,0,.18,0,0,0,-.32,0],3));G.tri.computeVertexNormals();
}
function mesh(geo,mat,sx=1,sy=1,sz=1,x=0,y=0,z=0){const m=new THREE.Mesh(geo,mat);m.scale.set(sx,sy,sz);m.position.set(x,y,z);return m}
function shadowBlob(r){const m=mesh(G.disc,M.shadow,r*2,r*2,1,0,.02,0);m.rotation.x=-Math.PI/2;return m}

/* ---------- figurer ---------- */
function person(shirt,shorts,legsApart){
  const g=new THREE.Group(),k=legsApart?.38:.14;
  const legL=new THREE.Group(),legR=new THREE.Group();
  for(const[leg,sx]of[[legL,-k],[legR,k]]){leg.position.set(sx,.95,0);leg.add(mesh(G.cyl,M.skin,.17,.5,.17,0,-.25,0));leg.add(mesh(G.cyl,M.sock,.18,.32,.18,0,-.62,0));leg.add(mesh(G.box,M.shoe,.2,.12,.34,0,-.84,.06));if(legsApart)leg.rotation.z=sx>0?-.25:.25;g.add(leg)}
  g.add(mesh(G.box,shorts,.5,.3,.3,0,1.05,0));
  g.add(mesh(G.box,shirt,.56,.62,.32,0,1.48,0));
  const armL=new THREE.Group(),armR=new THREE.Group();
  for(const[arm,sx]of[[armL,-.36],[armR,.36]]){arm.position.set(sx,1.72,0);arm.add(mesh(G.cyl,shirt,.16,.22,.16,0,-.1,0));arm.add(mesh(G.cyl,M.skin,.13,.42,.13,0,-.42,0));g.add(arm)}
  g.add(mesh(G.sph,M.skin,.36,.4,.36,0,2.0,0));g.add(mesh(G.sph,M.hair,.38,.22,.38,0,2.14,-.02));
  g.userData={legL,legR,armL,armR};return g;
}

/* ---------- världen ---------- */
let road,walkL,walkR,player,ball,ballShadow,playerShadow;
const scenery=[],obstacles=[],flags=[],kites=[];
function buildWorld(){
  scene=new THREE.Scene();
  scene.background=skyTex();scene.fog=new THREE.Fog('#cfe7f7',35,125);
  cam=new THREE.PerspectiveCamera(62,1,.1,400);cam.position.set(0,3.4,6.6);cam.lookAt(0,1.1,-8);
  scene.add(new THREE.HemisphereLight('#fff7e0','#6b5a4a',.95));
  const sun=new THREE.DirectionalLight('#fff1d0',.75);sun.position.set(-6,12,4);scene.add(sun);
  // berg i bakgrunden (påverkas inte av dimman)
  const hills=new THREE.Mesh(new THREE.PlaneGeometry(420,105),new THREE.MeshBasicMaterial({map:hillsTex(),transparent:true,fog:false}));hills.position.set(0,32,-210);scene.add(hills);
  road=mesh(new THREE.PlaneGeometry(ROAD_HALF*2,260),M.road);road.rotation.x=-Math.PI/2;road.position.z=-110;scene.add(road);
  for(const s of[-1,1]){const w=mesh(new THREE.PlaneGeometry(WALK,260),M.walk);w.rotation.x=-Math.PI/2;w.position.set(s*(ROAD_HALF+WALK/2),.12,-110);scene.add(w);if(s<0)walkL=w;else walkR=w;
    const curb=mesh(G.box,M.curb,.18,.14,260,s*(ROAD_HALF+.09),.07,-110);scene.add(curb)}
  // hus längs båda sidor
  for(const s of[-1,1]){let z=KILL_Z;while(z>SPAWN_Z-20){const len=rnd(5,9),hgt=rnd(4.5,11),dep=rnd(4,6);
    const h=new THREE.Group();const b=mesh(G.box,pick(M.facades),dep,hgt,len,0,hgt/2,0);h.add(b);h.add(mesh(G.box,M.roof,dep+.3,.35,len+.3,0,hgt+.17,0));
    if(Math.random()<.4){const aw=mesh(G.box,new THREE.MeshLambertMaterial({color:pick(PASTEL)}),.9,.12,len*.7,-s*(dep/2+.4),2.6,0);aw.rotation.z=s*.35;h.add(aw)}
    h.position.set(s*(ROAD_HALF+WALK+dep/2),0,z-len/2);h.userData={len:len+rnd(.2,1.5)};scene.add(h);scenery.push(h);z-=h.userData.len}
  }
  // palmer
  for(let i=0;i<8;i++){const p=new THREE.Group(),hh=rnd(4,6);p.add(mesh(G.cyl,M.trunk,.28,hh,.28,0,hh/2,0));for(let k=0;k<6;k++){const l=mesh(G.box,M.green,.2,.06,2.4,0,hh,0);l.rotation.y=k/6*Math.PI*2;l.rotation.x=.5;l.translateZ(1);p.add(l)}
    p.position.set((i%2?1:-1)*(ROAD_HALF+.8),0,-i*16-6);p.userData={len:16,palm:true};scene.add(p);scenery.push(p)}
  // bandeirinhas (festa junina-flaggor över gatan)
  for(let i=0;i<8;i++){const f=new THREE.Group();const span=(ROAD_HALF+WALK)*2,n=22;
    for(let k=0;k<n;k++){const u=k/(n-1),x=-span/2+u*span,y=5.6-Math.sin(u*Math.PI)*.9;const t=new THREE.Mesh(G.tri,new THREE.MeshLambertMaterial({color:pick(PASTEL),side:THREE.DoubleSide}));t.position.set(x,y,0);f.add(t)}
    f.position.z=-i*15-4;scene.add(f);flags.push(f)}
  // drakar (pipas) på himlen
  for(let i=0;i<4;i++){const k=new THREE.Mesh(new THREE.PlaneGeometry(1.1,1.1),new THREE.MeshBasicMaterial({color:pick(PASTEL),side:THREE.DoubleSide,fog:false}));k.rotation.z=Math.PI/4;k.position.set(rnd(-25,25),rnd(14,24),rnd(-90,-50));k.userData={ph:rnd(0,6)};scene.add(k);kites.push(k)}
  // spelare + boll
  player=person(M.shirt,M.shorts,false);player.add(mesh(G.box,M.trim,.58,.06,.34,0,1.77,0));scene.add(player);
  playerShadow=shadowBlob(.45);scene.add(playerShadow);
  ball=mesh(new THREE.SphereGeometry(.27,20,14),M.ball);scene.add(ball);ballShadow=shadowBlob(.26);scene.add(ballShadow);
}

/* ---------- hinder ---------- */
function makeObstacle(type,laneI,z){
  const g=new THREE.Group();let h=2,d=1.2;
  if(type==='cart'){ // försäljarvagn med parasoll
    g.add(mesh(G.box,M.wood,1.45,.9,1.1,0,.85,0));g.add(mesh(G.box,new THREE.MeshLambertMaterial({color:pick(PASTEL)}),1.5,.12,1.15,0,1.36,0));
    for(const sx of[-.55,.55]){const w=mesh(G.cyl,M.tire,.38,.12,.38,sx,.22,0);w.rotation.z=Math.PI/2;g.add(w)}
    g.add(mesh(G.cyl,M.white,.05,1.3,.05,0,2.0,0));const um=new THREE.Mesh(new THREE.ConeGeometry(1.1,.5,10),new THREE.MeshLambertMaterial({color:pick(PASTEL)}));um.position.y=2.75;g.add(um);
    h=3;d=1.3;
  }else if(type==='tackle'){ // försvarare som glidtacklar (låg – går att hoppa över)
    const p=person(M.def,M.defShorts,false);p.rotation.z=Math.PI/2.3;p.position.set(-.6,.35,0);p.rotation.y=Math.PI;g.add(p);h=.6;d=1.4;
  }else if(type==='caneta'){ // bredbent försvarare – kör rakt igenom benen
    const p=person(M.def,M.defShorts,true);p.rotation.y=Math.PI;g.add(p);h=0;d=.8;
  }else if(type==='low'){ // däck/lådor – hoppa (chapéu) eller byt fil
    for(let k=0;k<3;k++)g.add(mesh(G.cyl,M.tire,.95,.26,.95,0,.13+k*.26,0));h=.78;d=1;
  }else if(type==='wall'){ // låg mur över alla filer – måste hoppas
    g.add(mesh(G.box,new THREE.MeshLambertMaterial({color:'#e9c46a'}),ROAD_HALF*2,.7,.5,0,.35,0));for(let k=0;k<6;k++){g.add(mesh(G.box,new THREE.MeshLambertMaterial({color:pick(PASTEL)}),.6,.4,.52,-2.5+k,.42,0))}h=.7;d=.6;
  }else if(type==='coin'){g.add(mesh(G.coin,M.coin,1,1,1,0,.9,0));g.children[0].rotation.x=Math.PI/2;h=-1;d=.8;
  }else if(type==='goal'){ // golzinho – liten målbur i mittfilen
    for(const sx of[-.9,.9])g.add(mesh(G.cyl,M.white,.1,1.3,.1,sx,.65,0));const bar=mesh(G.cyl,M.white,.1,1.9,.1,0,1.3,0);bar.rotation.z=Math.PI/2;g.add(bar);
    g.add(mesh(G.box,M.net,1.8,1.3,.8,0,.65,-.45));h=-2;d=.8;
  }
  g.position.set(type==='wall'?0:LX[laneI],0,z);scene.add(g);
  const o={type,lane:laneI,z,h,d,g,done:false};obstacles.push(o);return o;
}
function spawnPattern(){
  const z=SPAWN_Z,lanes=[0,1,2],free=pick(lanes);const r=Math.random(),late=elapsed>18;
  const coinLine=(l,n=5,arc=false)=>{for(let k=0;k<n;k++){const o=makeObstacle('coin',l,z-k*1.6);if(arc){o.g.children[0].position.y=.9+Math.sin(k/(n-1)*Math.PI)*1.6}}};
  if(late&&S.jumpEnabled&&r<.10){makeObstacle('wall',1,z);coinLine(pick(lanes),5,true);flash('CHAPÉU!',z);return}
  if(r<.30){makeObstacle('cart',pick(lanes.filter(l=>l!==free)),z);coinLine(free)}
  else if(r<.50){for(const l of lanes)if(l!==free)makeObstacle('cart',l,z);coinLine(free,4)}
  else if(r<.66){const c=pick(lanes);makeObstacle('caneta',c,z);for(const l of lanes)if(l!==c&&Math.random()<(late?.9:.5))makeObstacle('cart',l,z)}
  else if(r<.80){makeObstacle(S.jumpEnabled?pick(['tackle','low']):'tackle',pick(lanes),z);coinLine(free,4)}
  else{const l=pick(lanes);coinLine(l,6)}
}
function flash(txt,z){} // plats för framtida varningsskylt

/* ---------- musik: samba/batucada som följer tempot ---------- */
function noise(t,dur,vol,hp){const len=Math.max(1,Math.floor(ac.sampleRate*dur)),b=ac.createBuffer(1,len,ac.sampleRate),c=b.getChannelData(0);for(let i=0;i<len;i++)c[i]=(Math.random()*2-1)*(1-i/len);const s=ac.createBufferSource(),f=ac.createBiquadFilter(),g=ac.createGain();f.type='highpass';f.frequency.value=hp;g.gain.value=vol;s.buffer=b;s.connect(f).connect(g).connect(ac.destination);s.start(t)}
function tone(t,f0,f1,dur,vol,type='sine'){const o=ac.createOscillator(),g=ac.createGain();o.type=type;o.frequency.setValueAtTime(f0,t);o.frequency.exponentialRampToValueAtTime(f1,t+dur);g.gain.setValueAtTime(vol,t);g.gain.exponentialRampToValueAtTime(.001,t+dur);o.connect(g).connect(ac.destination);o.start(t);o.stop(t+dur+.02)}
const TAMB=[1,0,1,1,0,1,0,1,1,0,1,1,0,1,0,1],AGO=[2,0,1,0,2,0,0,1,0,2,0,1,2,0,1,0];
function bpm(){return Math.min(138,98+S.speed*1.6)}
function schedule(){
  if(!ac||ac.state!=='running'||!S.running||S.countdown>0)return;
  const sixteenth=60/bpm()/4;
  while(nextNote<ac.currentTime+.12){const t=Math.max(nextNote,ac.currentTime),k=step16%16;
    if(k===0)tone(t,90,48,.22,.55);                     // surdo (dämpad)
    if(k===8)tone(t,75,40,.4,.95);                      // surdo (öppen, betoning på 2)
    if(TAMB[k])noise(t,.03,k%4===0?.22:.13,6000);       // tamborim
    noise(t,.02,k%2?.05:.09,8500);                       // chocalho
    if(AGO[k])tone(t,AGO[k]===2?960:720,AGO[k]===2?940:700,.09,.12,'triangle'); // agogô
    nextNote+=sixteenth;step16++}
}
function sfx(kind){if(!ac)return;const t=ac.currentTime;
  if(kind==='coin'){tone(t,1320,1760,.08,.12,'square')}
  else if(kind==='hit'){tone(t,180,60,.3,.35,'sawtooth');noise(t,.15,.3,400)}
  else if(kind==='caneta'){tone(t,660,990,.08,.18,'triangle');tone(t+.08,990,1320,.12,.18,'triangle')}
  else if(kind==='jump'){tone(t,300,700,.18,.12,'sine')}
  else if(kind==='goal'){for(let i=0;i<4;i++)tone(t+i*.09,520+i*130,560+i*130,.12,.18,'square')}}

/* ---------- spelloop ---------- */
function pop(txt,col,big){S.popups.push({txt,col,t:S.t,big:!!big})}
function reset(){
  for(const o of obstacles)scene.remove(o.g);obstacles.length=0;
  Object.assign(S,{running:false,over:false,countdown:3,speed:9,dist:0,coins:0,canetas:0,chapeus:0,gols:0,lives:3,score:0,invuln:0,hitFlash:0,popups:[],t:0});
  px=LX[1];jumpT=-1;spawnAcc=0;elapsed=0;lastGoalAt=0;
}
function update(dt,laneIn,jumpIn){
  S.t+=dt;clock+=dt;
  for(const k of kites){k.userData.ph+=dt;k.position.y+=Math.sin(k.userData.ph*1.3)*dt*.6;k.rotation.z=Math.PI/4+Math.sin(k.userData.ph)*.25}
  if(!S.running||S.over){idlePose(dt);return}
  if(S.countdown>0){S.countdown-=dt;idlePose(dt);if(S.countdown<=0&&ac){nextNote=ac.currentTime+.05;step16=0}return}
  elapsed+=dt;S.speed=Math.min(22,9+elapsed*.11);const v=S.speed*(S.invuln>1?.6:1),dz=v*dt;S.dist+=dz;
  // spelaren
  S.lane=laneIn;const tx=LX[laneIn];px+=(tx-px)*Math.min(1,dt*11);
  if(jumpIn&&jumpT<0&&S.jumpEnabled){jumpT=0;sfx('jump')}
  let jh=0;if(jumpT>=0){jumpT+=dt;jh=Math.sin(Math.min(1,jumpT/JUMP_DUR)*Math.PI)*1.7;if(jumpT>=JUMP_DUR)jumpT=-1}
  legPhase+=dt*v*.9;
  const ud=player.userData,sw=Math.sin(legPhase);
  ud.legL.rotation.x=sw*.9;ud.legR.rotation.x=-sw*.9;ud.armL.rotation.x=-sw*.7;ud.armR.rotation.x=sw*.7;
  player.position.set(px,jh+Math.abs(Math.cos(legPhase))*.08,0);player.rotation.z=(tx-px)*-.12;
  const blink=S.invuln>0&&Math.floor(S.t*12)%2===0;player.visible=!blink;
  playerShadow.position.set(px,.02,0);playerShadow.scale.setScalar(.9-jh*.2);
  // bollen: framför fötterna, rullar; lyfts i chapéu
  const bh=jumpT>=0?Math.sin(Math.min(1,jumpT/JUMP_DUR)*Math.PI)*2.3:0;
  ball.position.set(px+.42,.27+bh+Math.abs(Math.sin(legPhase))*.05,-1.6);ball.rotation.x-=dz/.27;ballShadow.position.set(px+.42,.02,-1.6);ballShadow.scale.setScalar(.55-bh*.12);
  // gata och trottoar rullar
  M.road.map.offset.y+=dz/260*85;M.walk.map.offset.y+=dz/260*70;
  // kulisser
  for(const h of scenery){h.position.z+=dz;if(h.position.z-((h.userData.len||8)/2)>KILL_Z){let minZ=0;for(const o of scenery)if(o.position.x*h.position.x>0&&!!o.userData.palm===!!h.userData.palm)minZ=Math.min(minZ,o.position.z-(o.userData.len||8)/2);h.position.z=minZ-(h.userData.len||8)/2}}
  for(const f of flags){f.position.z+=dz;if(f.position.z>KILL_Z)f.position.z-=15*flags.length}
  // nya hinder
  spawnAcc+=dz;const gap=Math.max(11,19-S.speed*.35);if(spawnAcc>=gap){spawnAcc=0;spawnPattern()}
  if(S.dist-lastGoalAt>420){lastGoalAt=S.dist;makeObstacle('goal',1,SPAWN_Z-6)}
  // krockar och bonusar
  const myLane=Math.round(px/1.8)+1;
  for(let i=obstacles.length-1;i>=0;i--){const o=obstacles[i];o.z+=dz;o.g.position.z=o.z;
    if(o.type==='coin')o.g.rotation.y+=dt*5;
    if(!o.done&&Math.abs(o.z)<o.d/2+.35){
      const same=o.type==='wall'||myLane===o.lane;
      if(same){
        if(o.type==='coin'){const cy=o.g.children[0].position.y;if(Math.abs(cy-(.9+jh))<1.3){o.done=true;o.g.visible=false;S.coins++;S.score+=10;sfx('coin')}}
        else if(o.type==='goal'){o.done=true;S.gols++;S.score+=150;pop('GOOOL!','#4ade80',true);sfx('goal')}
        else if(o.type==='caneta'){if(jh<.3&&Math.abs(px-LX[o.lane])<.5){o.done=true;S.canetas++;S.score+=60;pop('CANETA!','#ffd23f',true);sfx('caneta')}}
        else if(o.h>0){if(jh>o.h-.05){if(!o.done){o.done=true;if(o.type!=='coin'){S.chapeus++;S.score+=40;pop('CHAPÉU!','#38bdf8',true);sfx('caneta')}}}
          else if(S.invuln<=0){o.done=true;S.lives--;S.invuln=1.6;S.hitFlash=1;pop(S.lives>0?'AJ!':'SLUT!','#f87171',true);sfx('hit');if(S.lives<=0){S.over=true;S.running=false}}}
      }
    }
    if(o.z>KILL_Z){scene.remove(o.g);obstacles.splice(i,1)}
  }
  S.invuln=Math.max(0,S.invuln-dt);S.hitFlash=Math.max(0,S.hitFlash-dt*2);
  S.score=Math.round(S.dist)+S.coins*10+S.canetas*60+S.chapeus*40+S.gols*150;
  // kameran följer lite i sidled
  cam.position.x+=(px*.45-cam.position.x)*Math.min(1,dt*4);cam.lookAt(cam.position.x*.5,.6,-9);
}
function idlePose(dt){legPhase+=dt*2;const ud=player.userData;ud.legL.rotation.x=ud.legR.rotation.x=0;ud.armL.rotation.x=Math.sin(legPhase)*.1;ud.armR.rotation.x=-Math.sin(legPhase)*.1;
  player.position.set(px,0,0);player.visible=true;ball.position.set(px+.42,.27,-1.6);ballShadow.position.set(px+.42,.02,-1.6);playerShadow.position.set(px,.02,0)}

function resize(){if(!R)return;const w=innerWidth,h=innerHeight;R.setSize(w,h,false);cam.aspect=w/h;
  // stående mobil: ta ett steg bakåt så att alla tre filer syns
  const portrait=h>w;cam.fov=portrait?72:58;cam.position.set(cam.position.x,portrait?5.2:4.0,portrait?8.6:6.8);cam.lookAt(cam.position.x*.5,.6,-9);cam.updateProjectionMatrix()}

window.BooRun={
  state:S,
  init(cv){if(R)return;canvas=cv;R=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance'});R.setPixelRatio(Math.min(2,devicePixelRatio||1));mats();buildWorld();reset();resize();addEventListener('resize',resize);idlePose(0);R.render(scene,cam)},
  start(audioCtx,opts){ac=audioCtx;reset();S.jumpEnabled=!opts||opts.jump!==false;S.running=true;clearInterval(musicTimer);musicTimer=setInterval(schedule,25)},
  stop(){S.running=false;clearInterval(musicTimer)},
  update(dt,lane,jump){update(Math.min(.05,dt),lane,jump)},
  render(){if(R)R.render(scene,cam)},
  show(on){if(canvas)canvas.style.display=on?'block':'none'},
  peek(){return obstacles.filter(o=>!o.done&&o.z<1&&o.z>-40).map(o=>({type:o.type,lane:o.lane,z:o.z,h:o.h}))}
};
})();
