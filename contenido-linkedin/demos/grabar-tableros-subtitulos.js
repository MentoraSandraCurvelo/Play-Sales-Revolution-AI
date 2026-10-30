const {chromium}=require('playwright');
(async()=>{
 const b=await chromium.launch();
 const ctx=await b.newContext({viewport:{width:1080,height:1350},recordVideo:{dir:'vid',size:{width:1080,height:1350}},colorScheme:'light'});
 const p=await ctx.newPage();
 await p.goto('file://'+process.cwd()+'/demo.html'); await p.waitForTimeout(800);
 await p.evaluate(()=>{
  const l=document.createElement('link');l.rel='stylesheet';l.href='https://fonts.googleapis.com/css2?family=Outfit:wght@600;800&display=swap';document.head.appendChild(l);
  const s=document.createElement('style');s.textContent=`#cap{pointer-events:none;position:fixed;left:40px;right:40px;bottom:48px;z-index:99;background:rgba(8,8,8,.92);color:#fff;font:600 38px/1.3 Outfit,sans-serif;padding:26px 32px;border-left:10px solid #e00000;border-radius:6px;transition:opacity .3s}
  #cap b{color:#ff5a5a;font-weight:800}
  #card{pointer-events:none;position:fixed;inset:0;z-index:100;background:#080808;color:#fff;display:flex;flex-direction:column;justify-content:center;padding:90px;gap:28px;font-family:Outfit,sans-serif;transition:opacity .6s}
  #card .e{color:#e00000;font-weight:600;font-size:30px;letter-spacing:.08em}#card .h{font-weight:800;font-size:76px;line-height:1.08}#card .s{color:#bbb;font-size:34px;line-height:1.35}`;
  document.head.appendChild(s);
  const c=document.createElement('div');c.id='cap';c.style.opacity=0;document.body.appendChild(c);
  const k=document.createElement('div');k.id='card';document.body.appendChild(k);
 });
 const w=t=>p.waitForTimeout(t);
 const cap=async h=>{await p.evaluate(h=>{const c=document.getElementById('cap');c.innerHTML=h;c.style.opacity=h?1:0},h)};
 const card=async h=>{await p.evaluate(h=>{const k=document.getElementById('card');if(h){k.innerHTML=h;k.style.opacity=1}else k.style.opacity=0},h)};
 await w(1200);
 await card('<div class="e">IAM™ INTELLIGENCE · SECTOR PÚBLICO</div><div class="h">Así funciona la IA en una alcaldía.</div><div class="s">3 tableros. La IA hace el trabajo pesado. El servidor público decide y firma.</div>'); await w(4500);
 await card(''); await p.click('#t-plan'); await w(700);
 await cap('<b>1. Plan de Desarrollo.</b> El ciudadano ve cómo avanza cada eje frente a lo esperado.'); await w(4800);
 await cap('La IA señala las metas que van atrasadas y quién es el responsable.'); await p.mouse.wheel(0,400); await w(4200);
 await p.mouse.wheel(0,-400);
 await cap('Y redacta el informe en <b>lenguaje claro</b>, citando la fuente de cada cifra.'); await p.click('#pl-cite'); await w(4200);
 await cap('Planeación lo revisa y lo aprueba. <b>Nada se publica sin un humano.</b>'); await p.click('#pl-ok'); await w(4000);
 await p.click('#t-pqrsd'); await w(500);
 await cap('<b>2. PQRSD.</b> La IA clasifica cada solicitud y calcula el plazo de la Ley 1755.'); await w(4600);
 await p.click('#pq-table tbody tr:nth-child(2)');
 await cap('Ordena la bandeja por lo que vence primero y propone el borrador de respuesta.'); await w(4600);
 await p.click('#pq-table tbody tr:nth-child(5)'); await w(1500);
 await p.click('#pq-ok'); await cap('El servidor revisa, ajusta y <b>firma</b>. La IA no decide sobre derechos.'); await w(4200);
 await p.click('#t-secop'); await w(500);
 await cap('<b>3. Radar SECOP II.</b> La IA lee estudios previos y pliegos de cada proceso.'); await w(4600);
 await p.click('#sc-table tbody tr:nth-child(5)');
 await cap('Marca alertas: requisitos desproporcionados, precios fuera de rango, riesgos sin dueño.'); await w(5000);
 await p.click('#sc-ok'); await cap('El abogado confirma o descarta cada hallazgo. <b>Transparencia con supervisión humana.</b>'); await w(4800);
 await cap('');
 await card('<div class="e">EJEMPLO FICTICIO</div><div class="h">Lo que no se mide no puede ser mejorado.</div><div class="s">Todas las cifras son de ejemplo y no corresponden a ninguna entidad real.<br><br>Sandra Curvelo · Founder & CSO IAM™</div>'); await w(5000);
 await ctx.close(); await b.close();
})();
