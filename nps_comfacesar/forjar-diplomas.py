import re, pathlib, segno

ORIG = pathlib.Path("artifact-files/efc58cb3-3509-495c-8e83-ce23933f0b95/project/components/Diploma/preview.html")
SALIDA = pathlib.Path("/home/user/Play-Sales-Revolution-AI/nps_comfacesar/diploma-intelligence-001.html")

VERIF = "https://claude.ai/artifact/VZzvTXJi4kNFtF6HfNru3w"
CODIGO = "IAM-INT-CFC-G1-001"
NOMBRE = "Carlos Mario Gamarra"

t = ORIG.read_text("utf-8")

# --- QR como SVG en linea, sin dependencias de red ---
q = segno.make(f"{VERIF}#{CODIGO}", error="l", micro=False)
m = [list(r) for r in q.matrix]
n = len(m)
d = []
for y, fila in enumerate(m):
    x = 0
    while x < n:
        if fila[x]:
            x0 = x
            while x < n and fila[x]:
                x += 1
            d.append(f"M{x0} {y}h{x-x0}v1h-{x-x0}z")
        else:
            x += 1
qr = (f'<svg class="qr-dibujo" viewBox="0 0 {n} {n}" shape-rendering="crispEdges" role="img" '
      f'aria-label="Código QR que abre la verificación de la credencial {CODIGO}">'
      f'<path d="{"".join(d)}" fill="#14110d"/></svg>')
print("modulos", n, "longitud path", len("".join(d)))

# --- texto ---
rep = [
 ("<title>Diploma IAM™ Ambassadors</title>", "<title>Diploma IAM™ Intelligence</title>"),
 ('</span>LOS CERTIFICA COMO</div>', '</span>CERTIFICA A</div>'),
 ('<tspan class="i-tm" dy="-14">™</tspan>', '<tspan class="i-tm" dx="-1.5" dy="-6.2">™</tspan>'),
 ('<text class="s-marca" x="100" y="107">IAM</text>',
  '<text class="s-marca" x="100" y="107">IAM<tspan class="s-tm" dx="-2" dy="-6.5">™</tspan></text>'),
 # el CERTIFICATION recto se cruzaba con el FIRST GENERATION curvo del canto;
 # la palabra ya esta en el arco de arriba, asi que el interior sobra
 ('<text class="s-pie" x="100" y="124">CERTIFICATION</text>', ''),
 ('<div class="fila nombre">Frank Montero</div>', f'<div class="fila nombre">{NOMBRE}</div>'),
 ('Por haber cursado exitosamente el programa de &ldquo;<em>IAM<span class="tm">™</span> Ambassadors</em>&rdquo;, '
  'programa de embajadores de marca para LinkedIn con <em>Inteligencia Artificial (IA)</em> aplicada, '
  'durante un periodo de dos meses.',
  'Por haber cursado exitosamente el programa de &ldquo;<em>IAM<span class="tm">™</span> Intelligence</em>&rdquo;, '
  'programa de <em>Inteligencia Artificial (IA)</em> aplicada a la operación, '
  'durante un periodo de dos meses.'),
 ("<span>Primera generación de embajadores de Comfacesar</span>",
  "<span>Primera generación de IAM<span class=\"tm\">™</span> Intelligence en Comfacesar</span>"),
 ("Expedido en Valledupar, Colombia, a los 28 de septiembre de 2024.",
  "Expedido en Valledupar, Colombia, a los 9 días del mes de octubre de 2026."),
 ('<div class="url izq">www.comfacesar.com</div>',
  f'<div class="sello-qr">{qr}</div>'
  f'<div class="qr-rotulo">Verificación de credencial</div>'
  f'<div class="qr-codigo">{CODIGO}</div>'),
]
for a, b in rep:
    if t.count(a) != 1:
        raise SystemExit(f"NO ENCONTRADO x1 ({t.count(a)}): {a[:70]}")
    t = t.replace(a, b)

# --- CSS del bloque QR, pegado al final de la hoja de estilo original ---
css_qr = """
.esquina.se{display:none}
.sello-qr{position:absolute;left:48px;top:477px;width:86px;height:86px;padding:6px;
  background:var(--papel-100,#fbf8f2);border:1px solid rgba(169,124,34,.55)}
.qr-dibujo{display:block;width:100%;height:100%}
.tm{font-size:.42em;vertical-align:.95em}
.marca-swash .tm{font-size:.4em;vertical-align:.96em}
.iam-palabra .tm{font-size:.3em;vertical-align:1.6em}
.cuerpo .tm{font-size:.42em;vertical-align:.95em;font-style:normal;letter-spacing:0}
.generacion span.tm{font-size:.42em;vertical-align:.95em;font-style:normal;letter-spacing:0}
.s-tm{font-size:30px;letter-spacing:0}
.i-tm{font-size:22px}
.qr-rotulo{position:absolute;left:49px;top:570px;white-space:nowrap;
  font-family:var(--font-sello,"Cinzel",serif);font-size:7px;font-weight:600;
  letter-spacing:.14em;line-height:1;text-transform:uppercase;color:var(--oro-700,#8a6115)}
.qr-codigo{position:absolute;left:48px;top:582px;white-space:nowrap;
  font-family:var(--font-sello,"Cinzel",serif);font-size:9.6px;font-weight:600;
  letter-spacing:.07em;line-height:1;color:var(--tinta-700,#3b332a)}
"""

# --- quitar el envoltorio de documento: el artefacto pone doctype/html/head/body ---
t = re.sub(r'^<!-- @dsCard.*?-->\s*', '', t, flags=re.S)
t = t.replace('<!DOCTYPE html>\n<html lang="es"><head><meta charset="utf-8">', '')
cabeza, cuerpo = t.split("</head><body>")
cuerpo = cuerpo.replace("</body></html>", "").strip()
cabeza = cabeza.replace("</style>", css_qr + "</style>")

# tokens explicitos + encuadre responsive, sin depender de los valores por defecto
tokens = """<meta name="claude:viewport-fit-sides" content="cover">
<style>
/* Lámina fija de 1160x647 escalada al ancho disponible; la pieza nunca se recompone. */
:root{
  --lienzo:#efe9dd; --papel-100:#fbf8f2; --papel-200:#f3ece0;
  --tinta-900:#14110d; --tinta-700:#3b332a;
  --oro-500:#c19a3f; --oro-600:#a97c22; --oro-700:#8a6115;
  --font-display:"Cormorant Garamond",Georgia,"Times New Roman",serif;
  --font-texto:"EB Garamond",Georgia,"Times New Roman",serif;
  --font-sello:"Cinzel",Georgia,serif;
  color-scheme:light;
}
</style>
"""
cabeza = tokens + cabeza

# body -> div envoltorio, con el escenario escalado por JS
cuerpo_css = """<style>
body{background:var(--lienzo);display:block;
  padding-left:max(16px,env(safe-area-inset-left,0px));
  padding-right:max(16px,env(safe-area-inset-right,0px));
  padding-block:24px 28px;
  font-family:var(--font-texto);-webkit-font-smoothing:antialiased}
.marco{position:relative;width:min(100%,1160px);margin:0 auto}
.marco .escenario{position:absolute;top:0;left:0;transform-origin:0 0}
.al-pie{width:min(100%,1160px);margin:18px auto 0;display:flex;gap:10px 24px;
  flex-wrap:wrap;align-items:baseline;justify-content:space-between;
  font-size:14.5px;line-height:1.5;color:#5e5446}
.al-pie b{font-family:var(--font-sello);font-size:12.5px;font-weight:700;
  letter-spacing:.07em;color:var(--tinta-700)}
.al-pie a{color:var(--oro-700);text-decoration:none;border-bottom:1px solid rgba(138,97,21,.35)}
</style>
<div class="marco" id="marco">
"""
pie = f"""</div>
<p class="al-pie">
  <span><b>{CODIGO}</b> &middot; {NOMBRE} &middot; Jurídica</span>
  <span>El QR abre <a href="{VERIF}#{CODIGO}">la página de verificación</a></span>
</p>
<script>
const marco = document.getElementById("marco");
const esc = marco.querySelector(".escenario");
function encajar(){{
  const k = Math.min(1, marco.clientWidth / 1160);
  esc.style.transform = "scale(" + k + ")";
  marco.style.height = (647 * k) + "px";
}}
new ResizeObserver(encajar).observe(marco);
encajar();
</script>
"""
SALIDA.write_text(cabeza + cuerpo_css + cuerpo + pie, "utf-8")
print("escrito", SALIDA, SALIDA.stat().st_size, "bytes")
