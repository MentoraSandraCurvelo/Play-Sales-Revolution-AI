#!/usr/bin/env python3
"""
Reporte de corte del programa — IAM™ Intelligence
Agente LUCÍA · Sandra Curvelo

El documento que va a la contraparte del cliente: dónde va el programa,
qué pasa esta semana y qué se necesita de su lado. Misma identidad que las
actas, otra estructura: aquí manda el avance, no el detalle de una sesión.

Uso:
    python3 generar_reporte.py cortes/corte-2026-08-30.json
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

ROJO, ALTO, MEDIO, BAJO = "#B71C1C", "#BF360C", "#E65100", "#2E7D32"
GRIS, NEGRO, TEXTO, TENUE = "#F5F5F5", "#1A1A1A", "#1A1A1A", "#6B6B6B"

NIVELES = {
    "CRITICO": ("CRÍTICO", ROJO, "#E53935"),
    "ALTO": ("ALTO", ALTO, "#FB8C00"),
    "MEDIO": ("MEDIO", MEDIO, "#FDD835"),
    "BAJO": ("BAJO", BAJO, "#66BB6A"),
}


def e(v):
    return html.escape(str(v if v is not None else ""))


def punto(color):
    return (f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;'
            f'background:{color};vertical-align:middle;margin-right:5px;"></span>')


def css():
    return f"""
@page {{ size: letter; margin: 0.75in 0.72in; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; }}
body {{
  font-family: Cambria, Caladea, Georgia, "Times New Roman", serif;
  font-size: 9pt; line-height: 1.35; color: {TEXTO};
  -webkit-print-color-adjust: exact; print-color-adjust: exact;
}}

.cabecera {{ background: {ROJO}; color: #fff; padding: 20px 24px 22px 24px; margin-bottom: 26px; }}
.marca {{ font-size: 15pt; font-weight: bold; letter-spacing: .3px; margin: 0 0 5px 0; }}
.marca .anillo {{
  display: inline-block; width: 10px; height: 10px; border-radius: 50%;
  border: 3px solid #fff; margin-right: 7px; vertical-align: middle;
}}
.proyecto {{ font-style: italic; font-size: 8.5pt; opacity: .93; margin-bottom: 7px; }}
.kicker {{ font-size: 8pt; font-weight: bold; letter-spacing: .4px; margin-bottom: 9px; }}
.titulo {{ font-size: 21pt; font-weight: bold; line-height: 1.15; margin: 0 0 9px 0; }}
.meta {{ font-style: italic; font-size: 8.5pt; opacity: .95; }}

.kpis {{ display: flex; gap: 10px; margin: 0 0 26px 0; padding: 0 2px; }}
.kpi {{ flex: 1; }}
.kpi .valor {{
  font-size: 20pt; font-weight: bold; color: {ROJO};
  line-height: 1.05; margin-bottom: 4px; min-height: 26pt;
}}
.kpi .etiqueta {{ font-size: 7.5pt; font-weight: bold; margin-bottom: 3px; }}
.kpi .detalle {{ font-size: 6.8pt; color: {TENUE}; line-height: 1.3; }}

h2 {{
  font-size: 10pt; font-weight: bold; color: {ROJO}; letter-spacing: .5px;
  margin: 24px 0 10px 0; padding-bottom: 5px; border-bottom: 1.4px solid {ROJO};
  page-break-after: avoid;
}}
h2 .n {{ margin-right: 7px; }}
.entrada {{ font-size: 8.5pt; margin-bottom: 13px; }}
.intro {{ font-style: italic; font-size: 7.8pt; color: {TENUE}; margin-bottom: 11px; }}

table {{ width: 100%; border-collapse: collapse; font-size: 8pt; }}
th {{
  background: {ROJO}; color: #fff; font-weight: bold; text-align: left;
  padding: 6px 9px; font-size: 8pt;
}}
td {{ padding: 5px 9px; vertical-align: middle; }}
tr.par td {{ background: {GRIS}; }}

/* Barra de avance por área */
.barra-fondo {{
  display: inline-block; width: 100%; height: 9px; background: #E8E8E8;
  border-radius: 1px; overflow: hidden; vertical-align: middle;
}}
.barra-relleno {{ display: block; height: 9px; background: {ROJO}; }}

/* Agenda */
.dia {{ margin-bottom: 14px; page-break-inside: avoid; }}
.dia-cab {{
  background: {NEGRO}; color: #fff; font-weight: bold; font-size: 8.5pt;
  padding: 5px 12px; letter-spacing: .3px;
}}
.dia-cab .cuantas {{ float: right; font-weight: normal; font-style: italic; }}
.cita {{ display: flex; font-size: 8pt; padding: 5px 12px; }}
.cita.par {{ background: {GRIS}; }}
.cita .hora {{ width: 18%; font-weight: bold; color: {ROJO}; }}
.cita .area {{ width: 34%; font-weight: bold; }}
.cita .ses {{ width: 16%; color: {TENUE}; }}
.cita .quien {{ width: 32%; color: {TENUE}; }}

/* Alertas */
.alerta {{ margin-bottom: 18px; page-break-inside: avoid; }}
.alerta .barra {{ color: #fff; font-weight: bold; font-size: 9pt; padding: 7px 12px; }}
.alerta .barra .num {{ margin: 0 7px 0 0; }}
.alerta .cuerpo {{ padding: 8px 12px 0 12px; font-size: 8.2pt; }}
.alerta .firma {{ padding: 5px 12px 0 12px; font-size: 8.2pt; }}
.alerta .plazo {{ color: {ROJO}; font-weight: bold; }}

.pie {{
  margin-top: 30px; padding-top: 12px; border-top: 1px solid #DDD;
  font-size: 7.2pt; color: {TENUE}; text-align: center;
}}
.pie .anillo {{
  display: inline-block; width: 7px; height: 7px; border-radius: 50%;
  border: 2px solid {ROJO}; margin-right: 5px; vertical-align: middle;
}}
"""


def cabecera(d):
    return f"""
<div class="cabecera">
  <div class="marca"><span class="anillo"></span>IAM™ INTELLIGENCE</div>
  <div class="proyecto">Proyecto {e(d.get('proyecto'))} · {e(d.get('anio'))}</div>
  <div class="kicker">{e(d.get('kicker'))}</div>
  <div class="titulo">{e(d.get('titulo'))}</div>
  <div class="meta">{e(d.get('meta'))}</div>
</div>"""


def kpis(d):
    celdas = "".join(
        f'<div class="kpi"><div class="valor">{e(k.get("valor"))}</div>'
        f'<div class="etiqueta">{e(k.get("etiqueta"))}</div>'
        f'<div class="detalle">{e(k.get("detalle"))}</div></div>'
        for k in d.get("kpis", [])
    )
    return f'<div class="kpis">{celdas}</div>' if celdas else ""


def seccion(n, titulo, contenido):
    return f'<h2><span class="n">{n}</span>{e(titulo)}</h2>{contenido}' if contenido else ""


def avance(d):
    areas = d.get("avance") or []
    if not areas:
        return ""
    tope = max(a["sesiones"] for a in areas) or 1
    filas = "".join(
        f'<tr class="{"par" if i % 2 else ""}">'
        f'<td style="width:26%;font-weight:bold">{e(a["area"])}</td>'
        f'<td style="width:7%;text-align:center;font-weight:bold;color:{ROJO}">{a["sesiones"]}</td>'
        f'<td style="width:30%"><span class="barra-fondo">'
        f'<span class="barra-relleno" style="width:{round(a["sesiones"]/tope*100)}%"></span></span></td>'
        f'<td style="width:15%">{e(a.get("funcionarios",""))}</td>'
        f'<td>{e(a.get("estado",""))}</td></tr>'
        for i, a in enumerate(areas)
    )
    return ('<table><tr><th>Área</th><th style="text-align:center">Ses.</th><th>Avance</th>'
            f'<th>Personas</th><th>Estado</th></tr>{filas}</table>')


def agenda(d):
    dias = d.get("agenda") or []
    if not dias:
        return ""
    salida = []
    for dia in dias:
        citas = "".join(
            f'<div class="cita {"par" if i % 2 else ""}">'
            f'<span class="hora">{e(c["hora"])}</span>'
            f'<span class="area">{e(c["area"])}</span>'
            f'<span class="ses">{e(c.get("sesion",""))}</span>'
            f'<span class="quien">{e(c.get("quien",""))}</span></div>'
            for i, c in enumerate(dia["citas"])
        )
        n = len(dia["citas"])
        salida.append(
            f'<div class="dia"><div class="dia-cab">{e(dia["dia"])}'
            f'<span class="cuantas">{n} {"sesión" if n == 1 else "sesiones"}</span></div>{citas}</div>'
        )
    return "".join(salida)


def alertas(d):
    salida = []
    for a in d.get("alertas", []):
        nivel = str(a.get("nivel", "")).upper()
        if nivel in ("OPORTUNIDAD", "OPP"):
            fondo, marca = NEGRO, "★"
        else:
            _, fondo, pc = NIVELES.get(nivel, NIVELES["MEDIO"])
            marca = punto(pc)
        salida.append(
            f'<div class="alerta"><div class="barra" style="background:{fondo}">'
            f'{marca}<span class="num"> {e(a.get("num"))}</span>{e(a.get("titulo"))}</div>'
            f'<div class="cuerpo">{e(a.get("descripcion"))}</div>'
            f'<div class="firma"><b>Responsable:</b> {e(a.get("responsable"))} &nbsp;|&nbsp; '
            f'<b>Plazo:</b> <span class="plazo">{e(a.get("plazo"))}</span></div></div>'
        )
    return "".join(salida)


def tabla_simple(filas, encabezados):
    if not filas:
        return ""
    cab = "".join(f"<th>{e(h)}</th>" for h in encabezados)
    cuerpo = "".join(
        f'<tr class="{"par" if i % 2 else ""}">'
        + "".join(f"<td>{e(c)}</td>" for c in fila) + "</tr>"
        for i, fila in enumerate(filas)
    )
    return f"<table><tr>{cab}</tr>{cuerpo}</table>"


def numerada(items):
    if not items:
        return ""
    filas = [[i + 1, t] for i, t in enumerate(items)]
    cab = '<tr><th style="width:6%;text-align:center">N°</th><th>Detalle</th></tr>'
    cuerpo = "".join(
        f'<tr class="{"par" if i % 2 else ""}">'
        f'<td style="text-align:center;font-weight:bold;color:{ROJO}">{i + 1}</td>'
        f"<td>{e(t)}</td></tr>"
        for i, t in enumerate(items)
    )
    return f"<table>{cab}{cuerpo}</table>"


def construir(d):
    partes = [
        cabecera(d), kpis(d),
        seccion("01", "DÓNDE VA EL PROGRAMA",
                f'<div class="entrada">{e(d.get("resumen",""))}</div>'),
        seccion("02", "AVANCE POR ÁREA", avance(d)),
        seccion("03", "LA SEMANA QUE VIENE", agenda(d)),
        seccion("04", "LO QUE NECESITA ATENCIÓN", alertas(d)),
        seccion("05", "ÁREAS SIN ARRANCAR",
                tabla_simple(d.get("sin_arrancar", []), ["Área", "Personas", "Situación"])),
        seccion("06", "OBSERVACIONES DEL CORTE", numerada(d.get("observaciones", []))),
    ]
    return ('<!doctype html><html lang="es"><head><meta charset="utf-8">'
            f'<title>{e(d.get("titulo_doc", "Reporte de corte"))}</title>'
            f'<style>{css()}</style></head><body>{"".join(partes)}'
            f'<div class="pie"><span class="anillo"></span>{e(d.get("pie",""))}</div>'
            '</body></html>')


def buscar_chromium():
    if os.environ.get("CHROME_BIN"):
        return os.environ["CHROME_BIN"]
    for c in ["/opt/pw-browsers/chromium-1194/chrome-linux/chrome", "/usr/bin/chromium",
              "/usr/bin/google-chrome",
              "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]:
        if Path(c).exists():
            return c
    for p in Path("/opt/pw-browsers").glob("chromium-*/chrome-linux/chrome"):
        return str(p)
    return shutil.which("chromium") or shutil.which("google-chrome")


def main():
    ap = argparse.ArgumentParser(description="Genera el reporte de corte del programa.")
    ap.add_argument("json")
    ap.add_argument("--salida", default=None)
    args = ap.parse_args()

    d = json.loads(Path(args.json).read_text(encoding="utf-8"))
    destino = Path(args.salida or Path(__file__).parent / "salida")
    destino.mkdir(parents=True, exist_ok=True)

    base = unicodedata.normalize("NFKD", d.get("archivo", "REPORTE")).encode("ascii", "ignore").decode()
    base = "".join(c for c in base if c.isalnum() or c == "_")

    ruta_html = destino / f"{base}.html"
    ruta_html.write_text(construir(d), encoding="utf-8")
    print(f"  HTML  →  {ruta_html}")

    chrome = buscar_chromium()
    if not chrome:
        print("  ! Sin Chromium: solo se generó el HTML.", file=sys.stderr)
        return
    ruta_pdf = destino / f"{base}.pdf"
    subprocess.run([chrome, "--headless", "--disable-gpu", "--no-sandbox",
                    "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
                    "--virtual-time-budget=6000", f"--print-to-pdf={ruta_pdf}",
                    f"file://{ruta_html.resolve()}"], capture_output=True)
    if ruta_pdf.exists():
        print(f"  PDF   →  {ruta_pdf}")


if __name__ == "__main__":
    main()
