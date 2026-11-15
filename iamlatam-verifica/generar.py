import os, json, hashlib, urllib.parse, html

BASE = '/tmp/claude-0/-home-user-Play-Sales-Revolution-AI/d084f257-a979-56f3-8b50-8654282783e6/scratchpad/sitio'
OUT = BASE + '/nuevo/verifica'
SITE = 'https://iamlatam.co'
EXP = '28 de septiembre de 2026'

# código, nombre, cargo, linkedin, seguidores inicio, seguidores hoy (corte 14 nov 2026)
P = [
 ('001', 'Frank Montero', 'Director Administrativo', 'frank-cajasdecompensacion-valledupar-ceo', 98, 740),
 ('002', 'Rosa Elvira Ustáriz', 'Subdirectora Operativa y Comercial', 'ocha-ustariz-87067285', 111, 406),
 ('003', 'Julio Acosta Felizzola', 'Subdirector Administrativo y Financiero', 'julio-acosta-felizola-comfacesar-subdirector-financiero-administrativo', 0, 121),
 ('004', 'Víctor Manuel Rueda', 'Jefe de la Oficina Jurídica y Asuntos Legales', 'vmrabogado', 857, 936),
 ('005', 'José Jaime Maya', 'Gerente de Empleo y Productividad', 'josé-jaime-maya-empleo-cajadecompesacion-productividad', 18, 304),
 ('006', 'José Luciano Contreras', 'Gerente de Subsidio y Aportes', 'jose-luciano-contreras-comfacesar-seguridasocial-subsidiofamiliar', 3, 83),
 ('007', 'Lacides Daza', 'Gerente de Talento Humano', 'lacides-daza-gestionhumana-comfacesar-seleccion', 0, 201),
 ('009', 'José Jaime Rodríguez', 'Gerente de Educación y Cultura', 'jose-jaime-rodriguez-educacion-comfacesar-cultura', 0, 684),
 ('010', 'María Elvira Marulanda', 'Responsable de Comunicaciones', 'maría-elvira-marulanda-comunicaciones-comfacesar-marketing', 46, 248),
 ('011', 'Alemar Granadillo', 'Profesional Senior del Despacho de Dirección', 'alemar-granadillo-vidal-comfacesar-alianzasempresariales-proyectos', 457, 1084),
 ('012', 'Claudia Núñez', 'Jefe de la División de Vivienda', 'claudia-nuñez-vivienda-comfacesar-habitat-comunidad', 0, 303),
]

SELLO = open(OUT + '/assets/sello.svg.txt', encoding='utf-8').read().replace('class="sello sello--sup" ', 'class="sello" ')

CSS = r'''
:root{--papel:#fbf8f2;--papel2:#f3ece0;--tinta:#14110d;--tinta7:#3b332a;--mute:#6b5f51;
--oro3:#e8cf94;--oro5:#c19a3f;--oro6:#a97c22;--oro7:#8a6115;--rojo:#c00000;--ok:#1d7444;--okbg:#e6f3ea}
*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-text-size-adjust:100%}
body{min-height:100vh;background:#0f0d0a;color:var(--tinta);font-family:"EB Garamond",Georgia,serif;
 -webkit-font-smoothing:antialiased;padding:0 16px 48px}
a{color:inherit}
.top{max-width:960px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;padding:20px 0}
.marca{display:flex;align-items:center;gap:10px;color:#f3ece0;text-decoration:none;font-family:Cinzel,serif;font-weight:700;font-size:22px;letter-spacing:.04em}
.marca b{background:linear-gradient(170deg,#e8cf94,#c19a3f 40%,#8a6115 75%,#d9b45f);-webkit-background-clip:text;background-clip:text;color:transparent}
.marca small{font-family:"EB Garamond",serif;font-weight:400;font-size:14px;letter-spacing:.12em;color:#a99c86;text-transform:uppercase}
.seg{font-family:Montserrat,Arial,sans-serif;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:#a99c86;display:flex;align-items:center;gap:8px}
.seg svg{width:14px;height:14px}
.hoja{max-width:960px;margin:0 auto;background:radial-gradient(120% 90% at 50% 0%,#fefcf7 0%,var(--papel) 45%,var(--papel2) 100%);
 border-radius:4px;position:relative;overflow:hidden;box-shadow:0 30px 80px rgba(0,0,0,.55)}
.hoja::before{content:"";position:absolute;inset:10px;border:2px solid var(--oro6);pointer-events:none}
.hoja::after{content:"";position:absolute;inset:16px;border:1px solid var(--oro5);opacity:.6;pointer-events:none}
.trama{position:absolute;inset:0;opacity:.5;pointer-events:none;background-image:repeating-linear-gradient(34deg,rgba(193,154,63,.07) 0 1px,transparent 1px 9px)}
.in{position:relative;padding:44px 48px 40px}
/* estado */
.estado{display:flex;align-items:center;gap:16px;padding:16px 20px;border-radius:3px;background:var(--okbg);border:1px solid #9cc9a9;color:#123f27}
.estado .ic{flex:none;width:44px;height:44px;border-radius:50%;background:var(--ok);display:grid;place-items:center}
.estado .ic svg{width:24px;height:24px}
.estado b{display:block;font-family:Montserrat,Arial,sans-serif;font-size:15px;letter-spacing:.12em;text-transform:uppercase}
.estado span{font-size:17px}
.check path{stroke-dasharray:30;stroke-dashoffset:30}
.listo .check path{animation:trazo .5s .15s ease-out forwards}
@keyframes trazo{to{stroke-dashoffset:0}}
/* verificando */
.velo{position:fixed;inset:0;z-index:20;background:#0f0d0a;display:grid;place-items:center;transition:opacity .5s,visibility .5s}
.listo .velo{opacity:0;visibility:hidden}
.velo .c{display:flex;flex-direction:column;align-items:center;gap:18px;color:#e8cf94;font-family:Montserrat,Arial,sans-serif;font-size:13px;letter-spacing:.18em;text-transform:uppercase}
.velo .anillo{width:84px;height:84px;border-radius:50%;border:2px solid rgba(232,207,148,.2);border-top-color:#e8cf94;animation:gira 1s linear infinite}
.velo code{font-family:ui-monospace,Menlo,monospace;letter-spacing:.06em;font-size:14px;color:#a99c86;text-transform:none}
@keyframes gira{to{transform:rotate(360deg)}}
/* cuerpo */
.cab{display:grid;grid-template-columns:150px 1fr;gap:28px;align-items:center;margin-top:30px}
.sello{width:150px;height:150px;filter:drop-shadow(0 6px 12px rgba(72,50,12,.35));transform:scale(1.6) rotate(-25deg);opacity:0}
.listo .sello{animation:sella .7s .35s cubic-bezier(.2,1.5,.4,1) forwards}
@keyframes sella{to{transform:none;opacity:1}}
.s-orla{font-family:Cinzel,serif;font-size:12.4px;font-weight:700;letter-spacing:2.5px;fill:#6b4910;text-anchor:middle}
.s-marca{font-family:Cinzel,serif;font-size:38px;font-weight:700;letter-spacing:1.5px;fill:#5c3d0b;text-anchor:middle}
.s-pie{font-family:Cinzel,serif;font-size:9.6px;font-weight:600;letter-spacing:3.2px;fill:#6b4910;text-anchor:middle}
.ced{font-family:"Cormorant Garamond",serif;font-size:22px;letter-spacing:.06em;color:var(--tinta7)}
.ced i{font-weight:600}
h1{font-family:"Cormorant Garamond",serif;font-weight:700;font-size:54px;line-height:1;letter-spacing:.02em;text-transform:uppercase;margin:6px 0 8px}
.cargo{font-size:20px;color:var(--tinta7)}
.prog{margin-top:26px;font-size:21px;line-height:1.5;color:var(--tinta7);text-align:center;max-width:760px;margin-left:auto;margin-right:auto}
.prog em{font-style:italic}
.coh{display:flex;align-items:center;justify-content:center;gap:12px;margin-top:10px;font-family:"Cormorant Garamond",serif;font-style:italic;font-size:20px;color:var(--oro7)}
.coh::before,.coh::after{content:"";width:56px;height:1px;background:var(--oro6)}
/* datos */
.datos{display:grid;grid-template-columns:repeat(3,1fr);margin-top:30px;border-top:1px solid #e1d3b5;border-bottom:1px solid #e1d3b5}
.datos div{padding:16px 14px;border-right:1px solid #e1d3b5}
.datos div:last-child{border-right:0}
.datos dt{font-family:Montserrat,Arial,sans-serif;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--mute)}
.datos dd{font-size:19px;margin-top:4px;color:var(--tinta)}
.datos code{font-family:ui-monospace,Menlo,monospace;font-size:15px}
/* logros */
.logros{margin-top:30px}
.logros h2,.comp h2{font-family:Montserrat,Arial,sans-serif;font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--oro7);margin-bottom:12px}
.kpi{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.kpi div{background:#fffdf8;border:1px solid #e8dcc2;border-top:3px solid var(--oro5);padding:14px 16px}
.kpi b{display:block;font-family:"Cormorant Garamond",serif;font-size:40px;line-height:1;color:var(--oro7);font-variant-numeric:lining-nums tabular-nums}
.kpi span{font-size:16px;color:var(--tinta7)}
.comp{margin-top:28px}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chips span{font-size:16px;padding:6px 12px;border:1px solid #d9c49a;border-radius:20px;background:#fffdf8}
/* firma */
.firma{display:grid;grid-template-columns:1fr auto 1fr;gap:24px;align-items:end;margin-top:34px}
.firma .f{text-align:center}
.firma .f img{height:58px;display:block;margin:0 auto}
.firma .f .r{height:1px;background:var(--tinta);opacity:.8;margin:2px auto 6px;width:200px}
.firma .f b{display:block;font-size:17px}
.firma .f span{font-size:15px;color:var(--tinta7)}
.firma .logo img{height:62px;display:block}
/* acciones */
.acc{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin-top:34px}
.btn{display:inline-flex;align-items:center;gap:10px;font-family:Montserrat,Arial,sans-serif;font-weight:700;font-size:14px;letter-spacing:.04em;
 padding:13px 20px;border-radius:3px;text-decoration:none;border:1px solid var(--tinta);color:var(--tinta);background:#fffdf8;cursor:pointer}
.btn.li{background:#0a66c2;border-color:#0a66c2;color:#fff}
.btn.au{background:var(--tinta);color:#f3ece0}
.btn svg{width:18px;height:18px}
.btn:focus-visible{outline:3px solid var(--oro5);outline-offset:2px}
.huella{margin-top:30px;padding-top:16px;border-top:1px dashed #d9c49a;font-size:14px;color:var(--mute);display:flex;flex-wrap:wrap;gap:6px 18px;justify-content:space-between}
.huella code{font-family:ui-monospace,Menlo,monospace;font-size:12px;word-break:break-all;color:var(--tinta7)}
.pie{max-width:960px;margin:22px auto 0;color:#a99c86;font-size:14px;line-height:1.6;text-align:center}
.pie a{color:#e8cf94}
.cft{position:fixed;top:-20px;width:9px;height:14px;z-index:30;pointer-events:none;animation:cae var(--t) linear forwards}
@keyframes cae{to{transform:translate(var(--x),110vh) rotate(var(--r))}}
@media (max-width:720px){.in{padding:30px 22px 28px}.cab{grid-template-columns:1fr;justify-items:center;text-align:center}
 h1{font-size:38px}.datos,.kpi{grid-template-columns:1fr}.datos div{border-right:0;border-bottom:1px solid #e1d3b5}
 .firma{grid-template-columns:1fr}.firma .logo{justify-self:center}.prog{font-size:19px}}
@media (prefers-reduced-motion:reduce){.velo .anillo,.cft{animation:none}.sello{opacity:1;transform:none}.listo .sello{animation:none}.check path{stroke-dashoffset:0}}
@media print{body{background:#fff;padding:0}.velo,.acc,.top .seg,.pie{display:none}.hoja{box-shadow:none}}
'''

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Cormorant+Garamond:ital,wght@0,600;0,700;1,600&family=EB+Garamond:wght@400;600&family=Montserrat:wght@600;700&display=swap">'

LOCK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>'
CHECK = '<svg class="check" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
LI = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.13 1.45-2.13 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"/></svg>'

def fmt(n): return f'{n:,}'

def pagina(p):
    num, nombre, cargo, li, ini, hoy = p
    code = f'IAM-AMB-CFC-G1-{num}'
    url = f'{SITE}/verifica/{code}'
    huella = hashlib.sha256(f'{code}|{nombre}|IAM Ambassadors|Comfacesar|G1|2026-09-28'.encode()).hexdigest()
    li_url = 'https://www.linkedin.com/in/' + urllib.parse.quote(li, safe='-')
    add = 'https://www.linkedin.com/profile/add?' + urllib.parse.urlencode({
        'startTask': 'CERTIFICATION_NAME', 'name': 'IAM™ Ambassadors · Embajador de marca en LinkedIn con IA',
        'organizationName': 'IAM™ Influence', 'issueYear': '2026', 'issueMonth': '9', 'certUrl': url, 'certId': code})
    share = 'https://www.linkedin.com/sharing/share-offsite/?' + urllib.parse.urlencode({'url': url})
    nuevas = hoy - ini
    red = f'<div><b>{fmt(ini)} → {fmt(hoy)}</b><span>seguidores en LinkedIn</span></div>'
    if ini > 0:
        crec = f'<div><b>+{fmt(nuevas)}</b><span>conexiones nuevas durante el programa</span></div>'
    else:
        crec = f'<div><b>+{fmt(nuevas)}</b><span>conexiones construidas desde cero</span></div>'
    e = html.escape
    rol = 'embajadora' if num in ('002','010','012') else 'embajador'
    titulo = f'Certificado verificado · {nombre} · IAM™ Ambassadors'
    desc = f'{nombre} es {rol} certificad' + ('a' if rol.endswith('a') else 'o') + f' de Comfacesar en LinkedIn. Programa IAM™ Ambassadors, primera generación. Código {code}.'
    _x = f' de Comfacesar en LinkedIn. Programa IAM™ Ambassadors, primera generación. Código {code}.'
    return f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="noindex">
<meta property="og:type" content="website"><meta property="og:url" content="{url}">
<meta property="og:title" content="{e(titulo)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{SITE}/verifica/og/{code}.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{url}">
{FONTS}
<style>{CSS}</style></head>
<body>
<div class="velo" aria-hidden="true"><div class="c"><div class="anillo"></div>Verificando certificado<code>{code}</code></div></div>
<header class="top"><a class="marca" href="/" aria-label="IAM™, ir al inicio"><b>IAM™</b><small>Registro de certificados</small></a>
<span class="seg">{LOCK}Verificación oficial</span></header>
<main class="hoja"><div class="trama"></div><div class="in">
 <div class="estado" role="status"><div class="ic">{CHECK}</div><div><b>Certificado auténtico</b><span>Este certificado fue emitido por IAM™ y está vigente.</span></div></div>
 <div class="cab">{SELLO}
  <div><p class="ced"><i>IAM™</i> certifica a</p><h1>{e(nombre)}</h1><p class="cargo">{e(cargo)} · Comfacesar</p></div></div>
 <p class="prog">como {rol} de marca por haber cursado exitosamente el programa <em>IAM™ Ambassadors</em>, programa de embajadores de marca para LinkedIn con <em>inteligencia artificial</em> aplicada.</p>
 <p class="coh">Primera generación de embajadores de Comfacesar</p>
 <dl class="datos">
  <div><dt>Código del certificado</dt><dd><code>{code}</code></dd></div>
  <div><dt>Fecha de expedición</dt><dd>{EXP}</dd></div>
  <div><dt>Estado</dt><dd style="color:var(--ok);font-weight:600">Vigente</dd></div>
 </dl>
 <section class="logros"><h2>Lo que construyó en el programa</h2><div class="kpi">{red}{crec}<div><b>4 pilares</b><span>perfil, red, contenido y networking</span></div></div></section>
 <section class="comp"><h2>Competencias certificadas</h2><div class="chips"><span>Marca profesional en LinkedIn</span><span>Perfil de embajador</span><span>Red con propósito</span><span>Contenido con IA</span><span>Networking estratégico</span><span>Social Selling Index</span><span>Claude · ChatGPT · Gamma · NotebookLM</span></div></section>
 <div class="firma">
  <div class="logo"><img src="/verifica/assets/comfacesar.png" alt="Comfacesar, Estamos cumpliendo sueños"></div>
  <div class="f"><img src="/verifica/assets/firma-sandra.png" alt="Firma de Sandra Curvelo"><div class="r"></div><b>Sandra Curvelo</b><span>Fundadora y mentora, IAM™</span></div>
  <div></div>
 </div>
 <div class="acc">
  <a class="btn li" href="{e(add)}" target="_blank" rel="noopener">{LI}Agregar a mi perfil de LinkedIn</a>
  <a class="btn" href="{e(share)}" target="_blank" rel="noopener">Compartir en LinkedIn</a>
  <a class="btn" href="{e(li_url)}" target="_blank" rel="noopener">Ver su perfil</a>
  <button class="btn au" type="button" onclick="window.print()">Descargar en PDF</button>
 </div>
 <div class="huella"><span>Huella del registro (SHA-256): <code>{huella}</code></span><span id="cuando"></span></div>
</div></main>
<p class="pie">Este registro confirma que el certificado {code} fue emitido por IAM™ a nombre de {e(nombre)}.<br>¿Tienes dudas sobre un certificado? Escríbenos desde <a href="/">iamlatam.co</a>.</p>
<script>
(function(){{var rm=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
var d=new Date();try{{document.getElementById('cuando').textContent='Consultado el '+d.toLocaleDateString('es-CO',{{day:'numeric',month:'long',year:'numeric'}})+' a las '+d.toLocaleTimeString('es-CO',{{hour:'2-digit',minute:'2-digit'}});}}catch(e){{}}
setTimeout(function(){{document.body.classList.add('listo');if(rm)return;
var C=['#e8cf94','#c19a3f','#a97c22','#f8bd01','#e76100','#e0011c'];
for(var i=0;i<70;i++){{var e=document.createElement('i');e.className='cft';e.style.left=(Math.random()*100)+'vw';e.style.background=C[i%C.length];
e.style.setProperty('--x',(Math.random()*160-80)+'px');e.style.setProperty('--r',(Math.random()*900-450)+'deg');e.style.setProperty('--t',(2.2+Math.random()*1.8)+'s');e.style.animationDelay=(.6+Math.random()*.8)+'s';
document.body.appendChild(e);(function(e){{setTimeout(function(){{e.remove()}},5500)}})(e)}}}},rm?0:1300)}})();
</script>
</body></html>'''

def no_encontrado():
    return f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Certificado no encontrado · IAM™</title><meta name="robots" content="noindex">
{FONTS}<style>{CSS}
.no{{display:flex;align-items:center;gap:16px;padding:16px 20px;border-radius:3px;background:#fbe7e4;border:1px solid #e2a59b;color:#6e1a10}}
.no b{{display:block;font-family:Montserrat,Arial,sans-serif;font-size:15px;letter-spacing:.12em;text-transform:uppercase}}
form{{display:flex;gap:10px;flex-wrap:wrap;margin-top:24px}} input{{flex:1;min-width:220px;font:16px ui-monospace,Menlo,monospace;padding:12px 14px;border:1px solid #d9c49a;background:#fffdf8;border-radius:3px}}
</style></head><body class="listo">
<header class="top"><a class="marca" href="/"><b>IAM™</b><small>Registro de certificados</small></a><span class="seg">{LOCK}Verificación oficial</span></header>
<main class="hoja"><div class="trama"></div><div class="in">
<div class="no" role="status"><div><b>No encontramos este certificado</b><span>El código no corresponde a un certificado emitido por IAM™. Revisa que esté completo, con el formato IAM-AMB-CFC-G1-000.</span></div></div>
<form onsubmit="var v=this.c.value.trim().toUpperCase();if(v)location.href='/verifica/'+encodeURIComponent(v);return false"><label class="ced" for="c" style="width:100%">Escribe el código impreso en el certificado</label><input id="c" name="c" placeholder="IAM-AMB-CFC-G1-001" autocomplete="off"><button class="btn au">Verificar</button></form>
</div></main>
<p class="pie">¿Tienes dudas sobre un certificado? Escríbenos desde <a href="/">iamlatam.co</a>.</p>
</body></html>'''

def portada_verifica():
    s = no_encontrado()
    s = s.replace('Certificado no encontrado · IAM™', 'Verificar un certificado · IAM™')
    s = s.replace('<div class="no" role="status"><div><b>No encontramos este certificado</b><span>El código no corresponde a un certificado emitido por IAM™. Revisa que esté completo, con el formato IAM-AMB-CFC-G1-000.</span></div></div>',
                  '<p class="ced" style="font-size:30px"><i>IAM™</i> · Registro de certificados</p><p class="prog" style="text-align:left;margin-left:0">Cada certificado emitido por IAM™ lleva un código único y un QR. Escanéalo o escribe el código para confirmar que es auténtico.</p>')
    return s

os.makedirs(OUT, exist_ok=True)
for p in P:
    d = f'{OUT}/IAM-AMB-CFC-G1-{p[0]}'
    os.makedirs(d, exist_ok=True)
    open(d + '/index.html', 'w', encoding='utf-8').write(pagina(p))
open(OUT + '/no-encontrado.html', 'w', encoding='utf-8').write(no_encontrado())
open(OUT + '/index.html', 'w', encoding='utf-8').write(portada_verifica())
json.dump([{'code': f'IAM-AMB-CFC-G1-{p[0]}', 'nombre': p[1]} for p in P], open(BASE + '/registro.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('ok', len(P))
