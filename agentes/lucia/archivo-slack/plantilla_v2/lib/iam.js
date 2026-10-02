(function(){
const esc = s => String(s==null?'':s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const plano = s => String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
const MESES = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'];
const DIAS = ['domingo','lunes','martes','miércoles','jueves','viernes','sábado'];
function fechaLarga(iso){ const [y,m,d] = iso.split('-').map(Number);
  return DIAS[new Date(Date.UTC(y,m-1,d)).getUTCDay()] + ' ' + d + ' de ' + MESES[m-1]; }
const fechaCorta = iso => { if(!iso) return ''; const [,m,d] = iso.split('-').map(Number); return d + ' ' + MESES[m-1].slice(0,3); };
const miles = n => Math.round(n).toLocaleString('es-CO');
const horas = m => m >= 60 ? (Math.floor(m/60)+' h'+(m%60 ? ' '+(m%60)+' min' : '')) : m+' min';
const EMOJI = {o:'⭕',red_circle:'🔴',muscle:'💪',point_right:'👉',calendar:'📅',date:'📅',memo:'📝',movie_camera:'🎥',raised_hands:'🙌',wave:'👋',file_folder:'📁',warning:'⚠️',alarm_clock:'⏰',clock1:'🕐',clock2:'🕑',clock3:'🕒',clock4:'🕓',clock5:'🕔',clock8:'🕗',tada:'🎉',bulb:'💡',heart:'❤️',eyes:'👀',bar_chart:'📊',chart_with_upwards_trend:'📈',white_check_mark:'✅',heavy_check_mark:'✔️',x:'❌',pushpin:'📌',rocket:'🚀',fire:'🔥',clap:'👏',pray:'🙏',handshake:'🤝',books:'📚',mag:'🔍',bell:'🔔',lock:'🔒',key:'🔑',sparkles:'✨',star:'⭐',trophy:'🏆',dart:'🎯',hourglass:'⏳','+1':'👍','-1':'👎',page_facing_up:'📄',open_file_folder:'📂',inbox_tray:'📥',outbox_tray:'📤',computer:'💻',iphone:'📱',email:'📧',envelope:'✉️',link:'🔗',gear:'⚙️',large_blue_circle:'🔵',green_circle:'🟢',yellow_circle:'🟡',orange_circle:'🟠',arrow_right:'➡️',ok_hand:'👌',smile:'😊',blush:'😊',thinking_face:'🤔','100':'💯'};
const emo = n => EMOJI[n] || null;
const A_ST = 'color:var(--redt);text-decoration:none;border-bottom:1px solid var(--redline)';
const MEN = 'color:var(--redt);background:var(--redsoft);padding:0 4px;border-radius:5px;font-weight:550';
function marcar(t){
  if (!t) return '';
  const cofre = []; const dep = h => '\u0000'+(cofre.push(h)-1)+'\u0000';
  const u2 = u => u.replace(/&/g,'&amp;').replace(/"/g,'%22');
  const lnk = (u,e) => dep('<a style="'+A_ST+'" href="'+u2(u)+'" target="_blank" rel="noopener">'+esc(e)+'</a>');
  const corto = u => u.replace(/^https?:\/\//,'').replace(/^(.{48}).{4,}$/,'$1…');
  let s = String(t);
  s = s.replace(/```([\s\S]*?)```/g, (_,c) => dep('<pre style="font:12.5px/1.5 Geist Mono,monospace;background:var(--card2);border:1px solid var(--line);padding:10px 12px;border-radius:10px;white-space:pre-wrap;margin:6px 0">'+esc(c.trim())+'</pre>'));
  s = s.replace(/`([^`\n]+)`/g, (_,c) => dep('<code style="font:12.5px Geist Mono,monospace;background:var(--card2);padding:1px 5px;border-radius:5px">'+esc(c)+'</code>'));
  s = s.replace(/<(https?:\/\/[^>|\s]+)\|([^>]*)>/g, (_,u,e) => lnk(u, e.trim() || corto(u)));
  s = s.replace(/<(https?:\/\/[^>|\s]+)>/g, (_,u) => lnk(u, corto(u)));
  s = s.replace(/<mailto:([^>|\s]+)(?:\|[^>]*)?>/g, (_,m) => dep('<a style="'+A_ST+'" href="mailto:'+esc(m)+'">'+esc(m)+'</a>'));
  s = s.replace(/<@[A-Z0-9]+\|([^>]+)>/g, (_,n) => dep('<span style="'+MEN+'">@'+esc(n)+'</span>'));
  s = s.replace(/<@([A-Z0-9]+)>/g, (_,n) => dep('<span style="'+MEN+'">@'+esc(n)+'</span>'));
  s = s.replace(/<#[A-Z0-9]+\|([^>]+)>/g, (_,n) => dep('<span style="'+MEN+'">#'+esc(n)+'</span>'));
  s = s.replace(/<!([a-z]+)(?:\|[^>]*)?>/g, (_,n) => dep('<span style="'+MEN+'">@'+esc(n)+'</span>'));
  s = s.replace(/(^|[\s(])(https?:\/\/[^\s<>]+)/g, (m,a,u) => a + lnk(u, corto(u)));
  s = esc(s);
  s = s.replace(/:([a-z0-9_+\-]+):/g, (m,n) => emo(n) || m);
  s = s.replace(/(^|[\s(])\*([^*\n]+)\*/g, '$1<strong style="font-weight:620">$2</strong>');
  s = s.replace(/(^|[\s(])_([^_\n]+)_/g, '$1<em>$2</em>');
  s = s.replace(/(^|[\s(])~([^~\n]+)~/g, '$1<del>$2</del>');
  let out = '', buf = [];
  const cerrar = () => { if (buf.length){ out += '<p style="margin:0 0 6px">'+buf.join('<br>')+'</p>'; buf = []; } };
  for (const ln of s.split('\n')){
    const l = ln.trim();
    if (!l){ cerrar(); continue; }
    if (l.startsWith('&gt;')){ cerrar(); out += '<blockquote style="margin:4px 0 8px;padding:2px 0 2px 12px;border-left:2px solid var(--red);color:var(--ink2)">'+l.slice(4).trim()+'</blockquote>'; continue; }
    if (/^[•·\-–]\s/.test(l)){ buf.push('<span style="display:block;padding-left:14px;text-indent:-12px">• '+l.replace(/^[•·\-–]\s*/,'')+'</span>'); continue; }
    buf.push(l);
  }
  cerrar();
  return out.replace(/\u0000(\d+)\u0000/g, (_,i) => cofre[+i]);
}
function md(t){
  if (!t) return '';
  const cofre = []; const dep = h => '\u0000'+(cofre.push(h)-1)+'\u0000';
  let s = String(t).replace(/`([^`\n]+)`/g, (_,c) => dep('<code style="font:12.5px Geist Mono,monospace;background:var(--card2);padding:1px 5px;border-radius:5px">'+esc(c)+'</code>'));
  s = esc(s);
  s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, (_,e,u) => dep('<a style="'+A_ST+'" href="'+u.replace(/&amp;/g,'&').replace(/&/g,'&amp;')+'" target="_blank" rel="noopener">'+e+'</a>'));
  s = s.replace(/(https?:\/\/[^\s<]+)/g, u => dep('<a style="'+A_ST+'" href="'+u+'" target="_blank" rel="noopener">'+u.replace(/^https?:\/\//,'').slice(0,60)+'</a>'));
  s = s.replace(/\*\*([^*]+)\*\*/g, '<strong style="font-weight:620">$1</strong>');
  s = s.replace(/(^|[\s(])\*([^*\n]+)\*/g, '$1<em>$2</em>');
  s = s.replace(/(^|[\s(])_([^_\n]+)_/g, '$1<em>$2</em>');
  s = s.replace(/:([a-z0-9_+\-]+):/g, (m,n) => emo(n) || m);
  return s.replace(/\n/g,'<br>').replace(/\u0000(\d+)\u0000/g, (_,i) => cofre[+i]);
}
function textoDe(x){
  if (x == null) return '';
  if (typeof x === 'string') return x;
  if (Array.isArray(x)) return x.map(textoDe).join(' · ');
  const t = x.titulo || x.texto || x.tarea || x.nombre || '';
  const d = x.descripcion || x.detalle || x.objetivo || '';
  return t && d ? '**'+t+'** — '+d : (t || d || '');
}
function limpio(t){
  return String(t||'').replace(/<(https?:\/\/[^|>\s]+)\|([^>]*)>/g,'$2').replace(/<(https?:\/\/[^|>\s]+)>/g,'$1')
    .replace(/<@[A-Z0-9]+\|([^>]+)>/g,'@$1').replace(/<#[A-Z0-9]+\|([^>]+)>/g,'#$1')
    .replace(/:([a-z0-9_+\-]+):/g,' ').replace(/[*_~`]/g,'').replace(/\s+/g,' ').trim();
}
const PALETA = ['#C00000','#8E0000','#E5383B','#2B2B30','#45454B','#5C0A0A','#1A1A1D','#A4161A','#6B6B72'];
function iniciales(n){
  const p = String(n||'?').trim().split(/\s+/).filter(x=>/[a-zA-ZÀ-ÿ]/.test(x[0]||''));
  if (!p.length) return '?';
  return ((p[0][0]||'')+(p.length>1?(p[p.length-1][0]||''):'')).toUpperCase();
}
function colorDe(n){ let h = 0; const s = String(n||''); for (let i=0;i<s.length;i++) h = (h*31+s.charCodeAt(i))>>>0; return PALETA[h%PALETA.length]; }
function tipoArch(t){ t=t||''; return /pdf/.test(t)?'PDF' : /csv/.test(t)?'CSV' : /sheet|excel/.test(t)?'XLS' : /video|mp4/.test(t)?'VID' : /image|png|jpe?g/.test(t)?'IMG' : /word|doc/.test(t)?'DOC' : /present|ppt/.test(t)?'PPT' : 'ARC'; }
function recorte(t, q){
  const p = limpio(t), i = plano(p).indexOf(plano(q));
  if (i < 0) return esc(p.slice(0,86)) + (p.length>86?'…':'');
  const ini = Math.max(0, i-26), rec = p.slice(ini, i+q.length+62);
  const j = plano(rec).indexOf(plano(q));
  return (ini?'…':'') + esc(rec.slice(0,j)) + '<mark style="background:var(--red);color:#fff;border-radius:3px;padding:0 2px">' + esc(rec.slice(j,j+q.length)) + '</mark>' + esc(rec.slice(j+q.length)) + '…';
}
function makeCountUp(React){
  return function CountUp(p){
    const [v,setV] = React.useState(0);
    React.useEffect(()=>{ let r, s=performance.now(), d=p.dur||1600;
      const f=t=>{ const k=Math.min(1,(t-s)/d); setV(p.to*(1-Math.pow(1-k,4))); if(k<1) r=requestAnimationFrame(f); };
      r=requestAnimationFrame(f); const fb=setTimeout(()=>setV(p.to), d+150); return ()=>{cancelAnimationFrame(r); clearTimeout(fb);}; },[p.to]);
    return React.createElement('span',{style:{fontVariantNumeric:'tabular-nums'}}, miles(v)+(p.suf||''));
  };
}

/* Escena 3D: el anillo IAM™ hecho de partículas, con las áreas orbitando como satélites */
function hero3D(canvas, nodos, cb){
  const T = window.THREE; if (!T) return null;
  /* Si el equipo no tiene WebGL —equipo corporativo bloqueado, escritorio
     remoto, máquina vieja— crear el renderer lanza, y esa excepción tumbaba
     la página entera, no solo el hero. Devolver null deja el archivo
     navegable sin la escena. */
  let R; try { R = new T.WebGLRenderer({canvas, antialias:true, alpha:true}); }
  catch (e) { console.warn('[iam] sin WebGL: el archivo sigue, el hero no se dibuja'); return null; }
  R.setPixelRatio(Math.min(devicePixelRatio||1, 2));
  const S = new T.Scene(), C = new T.PerspectiveCamera(42, 1, .1, 100); C.position.set(0, 0, 10.5);
  const G = new T.Group(); S.add(G); G.rotation.x = .95; G.rotation.y = -.25;
  const N = 5200, pos = new Float32Array(N*3), base = new Float32Array(N*3), col = new Float32Array(N*3), fase = new Float32Array(N);
  const rojo = new T.Color('#E01818'), blanco = new T.Color('#FFFFFF'), oscuro = new T.Color('#7A0000');
  for (let i=0;i<N;i++){
    const u = Math.random()*Math.PI*2, v = Math.random()*Math.PI*2, R0 = 2.6, r = .32*Math.sqrt(Math.random());
    const x = (R0 + r*Math.cos(v))*Math.cos(u), y = (R0 + r*Math.cos(v))*Math.sin(u), z = r*Math.sin(v);
    base.set([x,y,z], i*3); pos.set([x,y,z], i*3); fase[i] = u;
    const c = Math.random()<.12 ? blanco : (Math.random()<.5 ? rojo : oscuro); col.set([c.r,c.g,c.b], i*3);
  }
  const geo = new T.BufferGeometry(); geo.setAttribute('position', new T.BufferAttribute(pos,3)); geo.setAttribute('color', new T.BufferAttribute(col,3));
  const pm = new T.PointsMaterial({size:.034, vertexColors:true, transparent:true, opacity:.95, depthWrite:false, blending:T.AdditiveBlending, sizeAttenuation:true});
  G.add(new T.Points(geo, pm));
  // polvo de fondo
  const M = 900, dp = new Float32Array(M*3);
  for (let i=0;i<M;i++){ dp.set([(Math.random()-.5)*22,(Math.random()-.5)*12,(Math.random()-.5)*10-3], i*3); }
  const dg = new T.BufferGeometry(); dg.setAttribute('position', new T.BufferAttribute(dp,3));
  const dmat = new T.PointsMaterial({size:.02, color:0xffffff, transparent:true, opacity:.35, depthWrite:false});
  const polvo = new T.Points(dg, dmat); S.add(polvo);
  // núcleo
  const nucleo = new T.Mesh(new T.IcosahedronGeometry(.9, 1), new T.MeshBasicMaterial({color:0xC00000, wireframe:true, transparent:true, opacity:.28}));
  G.add(nucleo);
  // satélites
  const max = Math.max(...nodos.map(n=>n.n), 1), sats = [], lp = [];
  const satG = new T.Group(); G.add(satG);
  nodos.forEach((n,i) => {
    const r = .07 + .16*Math.sqrt(n.n/max);
    const m = new T.Mesh(new T.SphereGeometry(r, 20, 20), new T.MeshBasicMaterial({color: i%3===0 ? 0xffffff : 0xFF2A2A, transparent:true, opacity:.95}));
    const halo = new T.Mesh(new T.SphereGeometry(r*2.4, 16, 16), new T.MeshBasicMaterial({color:0xC00000, transparent:true, opacity:.13, depthWrite:false, blending:T.AdditiveBlending}));
    m.add(halo);
    const o = { m, halo, rad: 3.35 + (i%4)*.42, ang: i/nodos.length*Math.PI*2, vel: .05 + (i%5)*.012, tilt: ((i%6)-2.5)*.16, data:n };
    m.userData = o; satG.add(m); sats.push(o);
  });
  const lg = new T.BufferGeometry(); const lpos = new Float32Array(nodos.length*6); lg.setAttribute('position', new T.BufferAttribute(lpos,3));
  const lmat = new T.LineBasicMaterial({color:0xC00000, transparent:true, opacity:.22});
  G.add(new T.LineSegments(lg, lmat));
  const ray = new T.Raycaster(), ptr = new T.Vector2(-9,-9);
  let tx = 0, ty = 0, hover = null, raf, t0 = performance.now(), vivo = true;
  const tam = () => { const w = canvas.clientWidth, h = canvas.clientHeight; if (!w||!h) return; R.setSize(w, h, false); C.aspect = w/h; C.position.z = w < 640 ? 13.5 : 10.5; C.updateProjectionMatrix(); };
  const ro = new ResizeObserver(tam); ro.observe(canvas); tam();
  const mover = e => { const r = canvas.getBoundingClientRect(); ptr.x = ((e.clientX-r.left)/r.width)*2-1; ptr.y = -((e.clientY-r.top)/r.height)*2+1; tx = ptr.x*.35; ty = ptr.y*.22; };
  const salir = () => { ptr.set(-9,-9); tx = ty = 0; };
  const clic = () => { if (hover && cb.pick) cb.pick(hover.data); };
  canvas.addEventListener('pointermove', mover); canvas.addEventListener('pointerleave', salir); canvas.addEventListener('click', clic);
  const v3 = new T.Vector3();
  function paso(t){
    if (!vivo) return;
    const s = (t - t0)/1000;
    const p = geo.attributes.position.array;
    for (let i=0;i<N;i++){ const k = i*3, w = Math.sin(fase[i]*3 + s*1.4)*.09 + Math.sin(fase[i]*7 - s*.9)*.04;
      p[k] = base[k]*(1+w*.12); p[k+1] = base[k+1]*(1+w*.12); p[k+2] = base[k+2] + w; }
    geo.attributes.position.needsUpdate = true;
    G.rotation.z = s*.07;
    G.rotation.x += ((.95 + ty) - G.rotation.x)*.05; G.rotation.y += ((-.25 + tx) - G.rotation.y)*.05;
    nucleo.rotation.x = s*.3; nucleo.rotation.y = s*.22; nucleo.scale.setScalar(1 + Math.sin(s*1.6)*.05);
    polvo.rotation.y = s*.01;
    sats.forEach((o,i) => { const a = o.ang + s*o.vel;
      o.m.position.set(Math.cos(a)*o.rad, Math.sin(a)*o.rad, Math.sin(a*2 + i)*.35 + o.tilt*Math.cos(a));
      const j = (i+1)%sats.length, b = sats[j];
      lpos.set([o.m.position.x,o.m.position.y,o.m.position.z, 0,0,0], i*6);
      const on = hover === o; o.m.scale.setScalar(on ? 1.7 : 1); o.halo.material.opacity = on ? .4 : .13; });
    lg.attributes.position.needsUpdate = true;
    ray.setFromCamera(ptr, C);
    const hit = ray.intersectObjects(sats.map(o=>o.m), false)[0];
    const nuevo = hit ? hit.object.userData : null;
    if (nuevo !== hover){ hover = nuevo; canvas.style.cursor = hover ? 'pointer' : 'default'; }
    if (cb.hover){
      if (hover){ hover.m.getWorldPosition(v3); v3.project(C); const r = canvas.getBoundingClientRect();
        cb.hover(hover.data, r.left + (v3.x+1)/2*r.width, r.top + (1-v3.y)/2*r.height); }
      else cb.hover(null);
    }
    R.render(S, C); raf = requestAnimationFrame(paso);
  }
  raf = requestAnimationFrame(paso);
  return {
    tema(claro){ pm.blending = claro ? T.NormalBlending : T.AdditiveBlending; pm.needsUpdate = true; dmat.color.set(claro ? 0x000000 : 0xffffff); dmat.opacity = claro ? .18 : .35; lmat.opacity = claro ? .35 : .22; nucleo.material.opacity = claro ? .45 : .28;
      sats.forEach((o,i)=>{ o.m.material.color.set(i%3===0 ? (claro?0x111111:0xffffff) : 0xE01818); o.halo.material.blending = claro ? T.NormalBlending : T.AdditiveBlending; o.halo.material.needsUpdate = true; }); },
    destruir(){ vivo = false; cancelAnimationFrame(raf); ro.disconnect(); canvas.removeEventListener('pointermove', mover); canvas.removeEventListener('pointerleave', salir); canvas.removeEventListener('click', clic); R.dispose(); }
  };
}
/* La plantilla marcaba su texto con formato con `dangerouslySetInnerHTML`, y el
   runtime no lo implementa —no aparece ni una vez en support.js—: el texto no se
   pintaba nunca, ni en los mensajes ni en las actas ni en las tareas. Y como
   React sí conoce ese nombre, tampoco servía pasarle la cadena: acababa escrita
   como texto plano, con las etiquetas a la vista.
   Por eso ahora viaja en `data-html`, que no le dice nada a nadie, y esto lo
   convierte en contenido real en cuanto aparece. El atributo se quita al
   aplicarlo, que es lo que evita que el observador se dispare a sí mismo. */
function promoverHTML(raiz){
  for (const el of (raiz || document).querySelectorAll('[data-html]')){
    const h = el.getAttribute('data-html');
    el.removeAttribute('data-html');
    if (h) el.innerHTML = h;
  }
}
if (typeof document !== 'undefined'){
  const arranca = () => {
    promoverHTML();
    new MutationObserver(() => promoverHTML()).observe(
      document.body, { childList:true, subtree:true, attributes:true,
                       attributeFilter:['data-html'] });
  };
  if (document.body) arranca();
  else document.addEventListener('DOMContentLoaded', arranca);
}

window.IAM = { esc, plano, fechaLarga, fechaCorta, miles, horas, marcar, md, textoDe, limpio, iniciales, colorDe, tipoArch, recorte, makeCountUp, hero3D, promoverHTML, MESES };
})();
