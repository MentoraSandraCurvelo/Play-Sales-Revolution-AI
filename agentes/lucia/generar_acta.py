#!/usr/bin/env python3
"""
Generador de ACTAS DE SESIÓN — IAM™ Intelligence
Agente LUCÍA · Sandra Curvelo

Toma un JSON con los datos de una sesión y produce el acta en HTML y PDF,
replicando exactamente la identidad visual IAM™ (rojo #B71C1C, tipografía
Cambria/Caladea, mapa de calor, alertas críticas y tabla de tareas).

Uso:
    python3 generar_acta.py sesiones/subsidio-s1-2026-08-24.json
    python3 generar_acta.py sesiones/mi-sesion.json --salida salida/ --solo-html

El binario de Chromium se resuelve automáticamente; se puede forzar con la
variable de entorno CHROME_BIN.
"""

import argparse
import html
import json
import os
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

# ---------------------------------------------------------------------------
# Identidad de marca IAM™ (extraída del acta de referencia Subsidio S1)
# ---------------------------------------------------------------------------
ROJO = "#B71C1C"      # rojo institucional IAM™ / nivel CRÍTICO
ALTO = "#BF360C"      # nivel ALTO
MEDIO = "#E65100"     # nivel MEDIO
BAJO = "#2E7D32"      # nivel BAJO
GRIS = "#F5F5F5"      # fondo de filas y bloques
NEGRO = "#1A1A1A"     # barras de oportunidad estratégica
TEXTO = "#1A1A1A"
TENUE = "#6B6B6B"

NIVELES = {
    "CRITICO": ("CRÍTICO", ROJO, "#E53935"),
    "CRÍTICO": ("CRÍTICO", ROJO, "#E53935"),
    "ALTO": ("ALTO", ALTO, "#FB8C00"),
    "MEDIO": ("MEDIO", MEDIO, "#FDD835"),
    "BAJO": ("BAJO", BAJO, "#66BB6A"),
}

PRIORIDADES = {"URGENTE": ROJO, "ALTA": ALTO, "MEDIA": MEDIO, "BAJA": BAJO}


def e(valor):
    """Escapa texto para HTML."""
    return html.escape(str(valor if valor is not None else ""))


def enlace(url, texto):
    """Enlace clicable — así la grabación se abre desde el acta."""
    return f'<a href="{e(url)}" style="color:{ROJO};">{e(texto)}</a>'


def punto(color):
    """Círculo de color (reemplaza los emoji del acta original: se imprime igual
    en cualquier sistema, sin depender de fuentes de emoji)."""
    return (
        f'<span style="display:inline-block;width:8px;height:8px;'
        f'border-radius:50%;background:{color};vertical-align:middle;'
        f'margin-right:5px;"></span>'
    )


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
def css():
    return f"""
@page {{ size: letter; margin: 0.75in 0.72in; }}

* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; }}

body {{
  font-family: Cambria, Caladea, Georgia, "Times New Roman", serif;
  font-size: 9pt;
  line-height: 1.35;
  color: {TEXTO};
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}}

/* ---------- Cabecera ---------- */
.cabecera {{
  background: {ROJO};
  color: #fff;
  padding: 20px 24px 22px 24px;
  margin-bottom: 26px;
}}
.marca {{ font-size: 15pt; font-weight: bold; letter-spacing: .3px; margin: 0 0 5px 0; }}
.marca .anillo {{
  display: inline-block; width: 10px; height: 10px; border-radius: 50%;
  border: 3px solid #fff; margin-right: 7px; vertical-align: middle;
}}
.proyecto {{ font-style: italic; font-size: 8.5pt; opacity: .93; margin-bottom: 7px; }}
.kicker {{ font-size: 8pt; font-weight: bold; letter-spacing: .4px; margin-bottom: 9px; }}
.titulo {{ font-size: 21pt; font-weight: bold; line-height: 1.15; margin: 0 0 9px 0; }}
.meta {{ font-style: italic; font-size: 8.5pt; opacity: .95; }}

/* ---------- Franja de KPIs ---------- */
.kpis {{ display: flex; gap: 10px; margin: 0 0 30px 0; padding: 0 2px; }}
.kpi {{ flex: 1; }}
.kpi .valor {{
  font-size: 20pt; font-weight: bold; color: {ROJO};
  line-height: 1.05; margin-bottom: 4px; min-height: 26pt;
}}
.kpi .etiqueta {{ font-size: 7.5pt; font-weight: bold; margin-bottom: 3px; }}
.kpi .detalle {{ font-size: 6.8pt; color: {TENUE}; line-height: 1.3; }}
.kpi .circulo {{
  display: inline-block; width: 17px; height: 17px; border-radius: 50%;
  background: {ROJO}; vertical-align: -2px; margin-right: 5px;
}}
.kpi .estrella {{ font-size: 17pt; color: {ROJO}; }}

/* ---------- Encabezados de sección ---------- */
h2 {{
  font-size: 10pt; font-weight: bold; color: {ROJO};
  letter-spacing: .5px; margin: 26px 0 10px 0;
  padding-bottom: 5px; border-bottom: 1.4px solid {ROJO};
  page-break-after: avoid;
}}
h2 .n {{ margin-right: 7px; }}
.intro {{ font-style: italic; font-size: 7.8pt; color: {TENUE}; margin-bottom: 11px; }}

/* ---------- Tablas ---------- */
table {{ width: 100%; border-collapse: collapse; font-size: 8pt; }}
th {{
  background: {ROJO}; color: #fff; font-weight: bold; text-align: left;
  padding: 6px 9px; font-size: 8pt;
}}
td {{ padding: 6px 9px; vertical-align: top; }}
tr.par td {{ background: {GRIS}; }}
.datos td.clave {{ font-weight: bold; width: 30%; }}
.datos tr.par td {{ background: {GRIS}; }}

/* ---------- Mapa de calor ---------- */
.riesgo {{
  display: flex; align-items: stretch; margin-bottom: 13px;
  page-break-inside: avoid; font-size: 8pt;
}}
.riesgo .r-titulo {{
  width: 30%; background: {GRIS}; font-weight: bold;
  padding: 9px 11px; display: flex; align-items: center;
}}
.riesgo .r-nivel {{
  width: 13%; color: #fff; font-weight: bold; font-size: 7.6pt;
  padding: 9px 6px; text-align: center; display: flex;
  align-items: center; justify-content: center;
}}
.riesgo .r-desc {{ width: 37%; padding: 9px 12px; }}
.riesgo .r-resp {{
  width: 20%; background: {GRIS}; color: {TENUE}; font-size: 7.6pt;
  padding: 9px 11px;
}}
.escala {{ font-style: italic; font-size: 7.5pt; color: {TENUE}; margin-bottom: 12px; }}

/* ---------- Alertas críticas ---------- */
.alerta {{ margin-bottom: 20px; page-break-inside: avoid; }}
.alerta .barra {{
  color: #fff; font-weight: bold; font-size: 9pt;
  padding: 7px 12px;
}}
.alerta .barra .num {{ margin: 0 7px 0 0; }}
.alerta .cuerpo {{ padding: 8px 12px 0 12px; font-size: 8.2pt; }}
.alerta .firma {{ padding: 5px 12px 0 12px; font-size: 8.2pt; }}
.alerta .firma b {{ font-weight: bold; }}
.alerta .plazo {{ color: {ROJO}; font-weight: bold; }}

/* ---------- Ejercicios ---------- */
.ejercicio {{ margin-bottom: 22px; page-break-inside: avoid; }}
.ejercicio .barra {{
  background: {ROJO}; color: #fff; font-weight: bold; font-size: 9pt;
  padding: 7px 12px;
}}
.ejercicio .barra .dur {{ font-weight: normal; font-style: italic; font-size: 8pt; }}
.ejercicio .objetivo {{
  font-style: italic; font-size: 7.9pt; color: {TENUE};
  padding: 8px 12px 10px 12px;
}}
.pasos {{ display: flex; gap: 0; padding: 0 4px; }}
.pasos .col {{ width: 50%; }}
.paso {{ padding: 5px 9px; font-size: 7.9pt; line-height: 1.32; }}
.paso.par {{ background: {GRIS}; }}
.paso .np {{ color: {ROJO}; font-weight: bold; margin-right: 5px; }}

/* ---------- Oportunidades ---------- */
.oportunidad {{ margin-bottom: 22px; page-break-inside: avoid; }}
.oportunidad .barra {{
  background: {NEGRO}; color: #fff; font-weight: bold; font-size: 8.2pt;
  letter-spacing: .3px; padding: 7px 12px;
}}
.oportunidad .op-titulo {{
  font-weight: bold; font-size: 9pt; padding: 9px 12px 4px 12px;
}}
.oportunidad .op-desc {{ padding: 0 12px; font-size: 8.2pt; }}
.oportunidad .op-pie {{ padding: 6px 12px 0 12px; font-size: 8.2pt; }}

/* ---------- Aviso ---------- */
.aviso {{
  font-weight: bold; font-size: 8.2pt; margin-bottom: 12px; line-height: 1.4;
}}
.aviso .sig {{ color: {ROJO}; margin-right: 4px; }}

/* ---------- Próxima sesión ---------- */
.proxima td {{ vertical-align: top; }}
.proxima .linea {{ display: block; margin-bottom: 4px; }}

/* ---------- Pie ---------- */
.pie {{
  margin-top: 34px; padding-top: 12px; border-top: 1px solid #DDD;
  font-size: 7.2pt; color: {TENUE}; text-align: center;
}}
.pie .anillo {{
  display: inline-block; width: 7px; height: 7px; border-radius: 50%;
  border: 2px solid {ROJO}; margin-right: 5px; vertical-align: middle;
}}
"""


# ---------------------------------------------------------------------------
# Secciones
# ---------------------------------------------------------------------------
def cabecera(d):
    kicker = f"ACTA DE SESIÓN N° {e(d.get('sesion_num',''))}"
    if d.get("fase"):
        kicker += f" · {e(d['fase'])}"
    titulo = e(d.get("area", ""))
    if d.get("area_completa"):
        titulo += f" — {e(d['area_completa'])}"
    meta = d.get("subtitulo_meta") or " · ".join(
        x for x in [d.get("fecha"), d.get("duracion"), d.get("modalidad_corta")] if x
    )
    return f"""
<div class="cabecera">
  <div class="marca"><span class="anillo"></span>IAM™ INTELLIGENCE</div>
  <div class="proyecto">Proyecto {e(d.get('proyecto',''))} · {e(d.get('anio',''))}</div>
  <div class="kicker">{kicker}</div>
  <div class="titulo">{titulo}</div>
  <div class="meta">{e(meta)}</div>
</div>"""


def franja_kpis(d):
    kpis = d.get("kpis") or []
    if not kpis:
        return ""
    celdas = []
    for k in kpis:
        icono = k.get("icono", "")
        valor = e(k.get("valor", ""))
        if icono == "punto-critico":
            valor = f'<span class="circulo"></span>{valor}'
        elif icono == "estrella":
            valor = f'<span class="estrella">★</span>{valor}'
        celdas.append(
            f'<div class="kpi"><div class="valor">{valor}</div>'
            f'<div class="etiqueta">{e(k.get("etiqueta",""))}</div>'
            f'<div class="detalle">{e(k.get("detalle",""))}</div></div>'
        )
    return f'<div class="kpis">{"".join(celdas)}</div>'


def seccion(numero, titulo, contenido):
    if not contenido:
        return ""
    return f'<h2><span class="n">{numero}</span>{e(titulo)}</h2>{contenido}'


def tabla_datos(d):
    filas = d.get("datos_sesion") or []
    if not filas:
        return ""
    def celda(valor):
        """Un valor que sea una URL se imprime como enlace, no como texto crudo."""
        v = str(valor)
        if v.startswith("http"):
            return enlace(v, "Ver grabación de la sesión")
        return e(v)

    cuerpo = "".join(
        f'<tr class="{"par" if i % 2 == 0 else ""}">'
        f'<td class="clave">{e(f[0])}</td><td>{celda(f[1])}</td></tr>'
        for i, f in enumerate(filas)
    )
    return f'<table class="datos">{cuerpo}</table>'


def tabla_participantes(d):
    p = d.get("participantes") or []
    if not p:
        return ""
    filas = "".join(
        f'<tr class="{"par" if i % 2 else ""}">'
        f'<td>{e(x.get("nombre"))}</td><td>{e(x.get("cargo"))}</td>'
        f'<td>{e(x.get("correo"))}</td><td>{e(x.get("modalidad"))}</td>'
        f'<td>{e(x.get("nivel"))}</td></tr>'
        for i, x in enumerate(p)
    )
    return (
        "<table><tr><th>Participante</th><th>Cargo / Área</th><th>Correo</th>"
        f"<th>Modalidad</th><th>Nivel IA Inicial</th></tr>{filas}</table>"
    )


def mapa_calor(d):
    riesgos = d.get("riesgos") or []
    if not riesgos:
        return ""
    escala = " · ".join(
        f"{punto(NIVELES[k][2])}{NIVELES[k][0]}" for k in ["CRITICO", "ALTO", "MEDIO", "BAJO"]
    )
    intro = e(d.get("mapa_calor_intro", ""))
    cabeza = f'<div class="escala">{intro} Escala: {escala}</div>'
    bloques = []
    for r in riesgos:
        etiqueta, fondo, punto_color = NIVELES.get(
            str(r.get("nivel", "")).upper(), NIVELES["MEDIO"]
        )
        bloques.append(
            f'<div class="riesgo">'
            f'<div class="r-titulo">{e(r.get("titulo"))}</div>'
            f'<div class="r-nivel" style="background:{fondo}">'
            f'{punto(punto_color)}{etiqueta}</div>'
            f'<div class="r-desc">{e(r.get("descripcion"))}</div>'
            f'<div class="r-resp">{e(r.get("responsable"))}</div>'
            f"</div>"
        )
    return cabeza + "".join(bloques)


def alertas(d):
    lista = d.get("alertas") or []
    if not lista:
        return ""
    salida = []
    for a in lista:
        nivel = str(a.get("nivel", "")).upper()
        if nivel in ("OPORTUNIDAD", "OPP"):
            fondo, marca = NEGRO, "★"
        else:
            etiqueta, fondo, punto_color = NIVELES.get(nivel, NIVELES["MEDIO"])
            marca = punto(punto_color)
        salida.append(
            f'<div class="alerta">'
            f'<div class="barra" style="background:{fondo}">'
            f'{marca}<span class="num"> {e(a.get("num",""))}</span>{e(a.get("titulo"))}</div>'
            f'<div class="cuerpo">{e(a.get("descripcion"))}</div>'
            f'<div class="firma"><b>Responsable:</b> {e(a.get("responsable"))} &nbsp;|&nbsp; '
            f'<b>Plazo:</b> <span class="plazo">{e(a.get("plazo"))}</span></div>'
            f"</div>"
        )
    return "".join(salida)


def ejercicios(d):
    lista = d.get("ejercicios") or []
    if not lista:
        return ""
    salida = []
    for ej in lista:
        pasos = ej.get("pasos") or []
        mitad = (len(pasos) + 1) // 2
        columnas = []
        for inicio, trozo in ((0, pasos[:mitad]), (mitad, pasos[mitad:])):
            items = "".join(
                f'<div class="paso {"par" if (inicio + i) % 2 == 0 else ""}">'
                f'<span class="np">{inicio + i + 1:02d}</span>{e(p)}</div>'
                for i, p in enumerate(trozo)
            )
            columnas.append(f'<div class="col">{items}</div>')
        dur = f' · <span class="dur">{e(ej.get("duracion"))}</span>' if ej.get("duracion") else ""
        salida.append(
            f'<div class="ejercicio">'
            f'<div class="barra">{e(ej.get("titulo"))}{dur}</div>'
            f'<div class="objetivo"><b>Objetivo:</b> {e(ej.get("objetivo"))}</div>'
            f'<div class="pasos">{"".join(columnas)}</div>'
            f"</div>"
        )
    return "".join(salida)


def oportunidades(d):
    lista = d.get("oportunidades") or []
    if not lista:
        return ""
    salida = []
    for o in lista:
        salida.append(
            f'<div class="oportunidad">'
            f'<div class="barra">★ {e(o.get("encabezado"))}</div>'
            f'<div class="op-titulo">{e(o.get("titulo"))}</div>'
            f'<div class="op-desc">{e(o.get("descripcion"))}</div>'
            f'<div class="op-pie"><b>Estado:</b> {e(o.get("estado"))} &nbsp;|&nbsp; '
            f'<b>Próximo paso:</b> {e(o.get("proximo_paso"))} &nbsp;|&nbsp; '
            f'<b>Target:</b> {e(o.get("target"))}</div>'
            f"</div>"
        )
    return "".join(salida)


def tabla_tareas(d):
    tareas = d.get("tareas") or []
    if not tareas:
        return ""
    aviso = ""
    if d.get("tareas_intro"):
        aviso = f'<div class="aviso"><span class="sig">⚠</span>{e(d["tareas_intro"])}</div>'
    filas = "".join(
        f'<tr class="{"par" if i % 2 else ""}">'
        f'<td style="text-align:center;font-weight:bold;color:{ROJO}">{i + 1}</td>'
        f'<td>{e(t.get("tarea"))}</td><td>{e(t.get("responsable"))}</td>'
        f'<td style="text-align:center;font-weight:bold;'
        f'color:{PRIORIDADES.get(str(t.get("prioridad","")).upper(), TENUE)}">'
        f'{e(t.get("prioridad"))}</td>'
        f'<td style="text-align:center">{e(t.get("plazo"))}</td></tr>'
        for i, t in enumerate(tareas)
    )
    return (
        aviso
        + '<table><tr><th style="width:5%;text-align:center">#</th><th style="width:43%">Tarea</th>'
        f'<th style="width:19%">Responsable</th><th style="width:14%;text-align:center">Prioridad</th>'
        f'<th style="width:19%;text-align:center">Plazo</th></tr>{filas}</table>'
    )


def tabla_observaciones(d):
    obs = d.get("observaciones") or []
    if not obs:
        return ""
    filas = "".join(
        f'<tr class="{"par" if i % 2 else ""}">'
        f'<td style="width:6%;text-align:center;font-weight:bold;color:{ROJO}">{i + 1}</td>'
        f"<td>{e(o)}</td></tr>"
        for i, o in enumerate(obs)
    )
    return (
        '<table><tr><th style="width:6%;text-align:center">N°</th>'
        f"<th>Observación</th></tr>{filas}</table>"
    )


def proxima_sesion(d):
    p = d.get("proxima_sesion") or {}
    if not p:
        return ""
    cond = "".join(f'<span class="linea">{e(c)}</span>' for c in p.get("condiciones", []))
    agen = "".join(f'<span class="linea">{e(a)}</span>' for a in p.get("agendamiento", []))
    return (
        '<table class="proxima"><tr><th style="width:34%">SESIÓN</th>'
        '<th style="width:33%">CONDICIÓN DE ENTRADA</th>'
        "<th>AGENDAMIENTO</th></tr>"
        f'<tr class="par"><td><b>{e(p.get("sesion"))}</b></td>'
        f"<td>{cond}</td><td>{agen}</td></tr></table>"
    )


# ---------------------------------------------------------------------------
# Documento
# ---------------------------------------------------------------------------
def construir_html(d):
    pie = e(d.get("pie", "IAM™ Intelligence — Documento Confidencial"))
    partes = [
        cabecera(d),
        franja_kpis(d),
        seccion("01", "DATOS DE LA SESIÓN", tabla_datos(d)),
        seccion("02", "PARTICIPANTES Y DIAGNÓSTICO INICIAL", tabla_participantes(d)),
        seccion("03", "MAPA DE CALOR — RIESGOS DEL PROYECTO", mapa_calor(d)),
        seccion("04", "ALERTAS CRÍTICAS — ACCIONES REQUERIDAS", alertas(d)),
        seccion("05", "EJERCICIOS CUBIERTOS — PASO A PASO", ejercicios(d)),
        seccion("06", "OPORTUNIDAD ESTRATÉGICA — CONFIRMADA EN ACTA", oportunidades(d)),
        seccion(
            "07",
            f"TAREAS PARA LA PRÓXIMA SESIÓN (SESIÓN {d.get('sesion_num', 0) + 1})",
            tabla_tareas(d),
        ),
        seccion("08", "OBSERVACIONES Y NOTAS ADICIONALES", tabla_observaciones(d)),
        seccion("09", "PRÓXIMA SESIÓN", proxima_sesion(d)),
        f'<div class="pie"><span class="anillo"></span>{pie}</div>',
    ]
    titulo_doc = f"ACTA Sesión {d.get('sesion_num','')} · {d.get('area','')} · {d.get('proyecto','')}"
    return (
        "<!doctype html><html lang=\"es\"><head><meta charset=\"utf-8\">"
        f"<title>{e(titulo_doc)}</title><style>{css()}</style></head>"
        f"<body>{''.join(partes)}</body></html>"
    )


# ---------------------------------------------------------------------------
# PDF
# ---------------------------------------------------------------------------
def buscar_chromium():
    if os.environ.get("CHROME_BIN"):
        return os.environ["CHROME_BIN"]
    candidatos = [
        "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/bin/google-chrome",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    for c in candidatos:
        if Path(c).exists():
            return c
    for patron in Path("/opt/pw-browsers").glob("chromium-*/chrome-linux/chrome"):
        return str(patron)
    return shutil.which("chromium") or shutil.which("google-chrome")


def html_a_pdf(ruta_html, ruta_pdf):
    chrome = buscar_chromium()
    if not chrome:
        print("  ! No se encontró Chromium: se generó solo el HTML.", file=sys.stderr)
        print("    Ábrelo en el navegador e imprime a PDF, o define CHROME_BIN.", file=sys.stderr)
        return False
    cmd = [
        chrome, "--headless", "--disable-gpu", "--no-sandbox",
        "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=6000",
        f"--print-to-pdf={ruta_pdf}", f"file://{Path(ruta_html).resolve()}",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if not Path(ruta_pdf).exists():
        print(r.stderr[-800:], file=sys.stderr)
        return False
    return True


def nombre_archivo(d):
    """ACTA_Sesion1_Subsidio_24Agosto2026 — sin tildes ni espacios."""
    area = str(d.get("area", "Area")).title().replace(" ", "")
    fecha = str(d.get("fecha_corta") or d.get("fecha") or "").replace(" ", "")
    fecha = fecha.replace("de", "")
    base = f"ACTA_Sesion{d.get('sesion_num','')}_{area}_{fecha}"
    base = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode()
    return "".join(c for c in base if c.isalnum() or c == "_")


def main():
    ap = argparse.ArgumentParser(description="Genera el acta IAM™ de una sesión.")
    ap.add_argument("json", help="Ruta al JSON de la sesión")
    ap.add_argument("--salida", default=None, help="Carpeta de salida (default: ./salida)")
    ap.add_argument("--solo-html", action="store_true", help="No generar PDF")
    args = ap.parse_args()

    d = json.loads(Path(args.json).read_text(encoding="utf-8"))
    destino = Path(args.salida or Path(__file__).parent / "salida")
    destino.mkdir(parents=True, exist_ok=True)

    base = nombre_archivo(d)
    ruta_html = destino / f"{base}.html"
    ruta_html.write_text(construir_html(d), encoding="utf-8")
    print(f"  HTML  →  {ruta_html}")

    if not args.solo_html:
        ruta_pdf = destino / f"{base}.pdf"
        if html_a_pdf(ruta_html, ruta_pdf):
            print(f"  PDF   →  {ruta_pdf}")


if __name__ == "__main__":
    main()
