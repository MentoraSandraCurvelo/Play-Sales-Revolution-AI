#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera el reporte ejecutivo IAM™ Intelligence a partir de un JSON.
Reutiliza la identidad visual de generar_acta.py (rojo #B71C1C, Cambria).

    python3 generar_reporte.py reportes/<archivo>.json
"""
import html as H
import json
import sys
from pathlib import Path

from generar_acta import ROJO, ALTO, MEDIO, BAJO, GRIS, css, html_a_pdf

SALIDA = Path(__file__).parent / "salida"
NIVEL_COLOR = {"CRITICO": ROJO, "CRÍTICO": ROJO, "ALTO": ALTO, "MEDIO": MEDIO, "BAJO": BAJO}


def e(t):
    return H.escape(str(t if t is not None else ""))


def enfasis(t):
    """_texto_ -> cursiva; *texto* -> negrita. Igual que en las actas."""
    t = e(t)
    for marca, tag in (("_", "em"), ("*", "strong")):
        partes = t.split(marca)
        t = "".join(p if i % 2 == 0 else f"<{tag}>{p}</{tag}>" for i, p in enumerate(partes))
    return t


def css_extra():
    return f"""
.bloque {{ page-break-inside: avoid; margin-bottom: 13px; }}
.bloque .cab {{
  background: {GRIS}; padding: 7px 11px; font-weight: bold; font-size: 8.5pt;
  border-left: 4px solid {ROJO};
}}
.bloque .cab .etq {{ float: right; font-weight: normal; font-style: italic; font-size: 7.5pt; }}
.bloque .cuerpo {{ padding: 8px 11px 2px 15px; font-size: 8pt; }}
.bloque .cuerpo p {{ margin: 0 0 6px 0; }}

.severidad {{ display: inline-block; padding: 1px 7px; border-radius: 8px;
  color: #fff; font-size: 6.8pt; font-weight: bold; letter-spacing: .3px; margin-right: 6px; }}

ul.limpia {{ margin: 4px 0 10px 0; padding-left: 17px; font-size: 8pt; }}
ul.limpia li {{ margin-bottom: 4px; }}

.nota {{ background: {GRIS}; border-left: 4px solid {MEDIO}; padding: 9px 12px;
  font-size: 8pt; margin: 12px 0; page-break-inside: avoid; }}
.nota .t {{ font-weight: bold; display: block; margin-bottom: 4px; }}

.decision {{ border: 1.4px solid {ROJO}; padding: 10px 13px; margin-bottom: 11px;
  page-break-inside: avoid; }}
.decision .t {{ font-weight: bold; color: {ROJO}; font-size: 9pt; margin-bottom: 5px; }}
.decision .q {{ font-size: 8pt; margin-bottom: 6px; }}
.decision .p {{ font-size: 7.6pt; font-style: italic; color: #555; }}

.pie {{ margin-top: 30px; padding-top: 9px; border-top: 1.4px solid {ROJO};
  font-size: 7.2pt; color: #555; font-style: italic; }}
"""


def cabecera(d):
    k = "".join(
        f'<div class="kpi"><div class="valor">{e(x["valor"])}</div>'
        f'<div class="etiqueta">{e(x["etiqueta"])}</div>'
        f'<div class="detalle">{e(x.get("detalle",""))}</div></div>'
        for x in d.get("kpis", [])
    )
    return f"""
<div class="cabecera">
  <div class="marca"><span class="anillo"></span>IAM™ INTELLIGENCE</div>
  <div class="proyecto">{e(d.get('proyecto_meta',''))}</div>
  <div class="kicker">{e(d.get('kicker',''))}</div>
  <div class="titulo">{e(d.get('titulo',''))}</div>
  <div class="meta">{e(d.get('subtitulo_meta',''))}</div>
</div>
<div class="kpis">{k}</div>"""


def seccion(num, titulo, cuerpo, intro=""):
    i = f'<div class="intro">{enfasis(intro)}</div>' if intro else ""
    return f'<h2><span class="n">{num}</span>{e(titulo)}</h2>{i}{cuerpo}'


def tabla(cols, filas):
    th = "".join(f"<th>{e(c)}</th>" for c in cols)
    tr = ""
    for i, f in enumerate(filas):
        cls = ' class="par"' if i % 2 else ""
        tds = "".join(f"<td>{enfasis(c)}</td>" for c in f)
        tr += f"<tr{cls}>{tds}</tr>"
    return f"<table><tr>{th}</tr>{tr}</table>"


def bloques(items):
    out = ""
    for b in items:
        nivel = b.get("nivel", "")
        sev = (f'<span class="severidad" style="background:{NIVEL_COLOR.get(nivel, MEDIO)}">'
               f'{e(nivel)}</span>') if nivel else ""
        etq = f'<span class="etq">{e(b["etiqueta"])}</span>' if b.get("etiqueta") else ""
        parrafos = "".join(f"<p>{enfasis(p)}</p>" for p in b.get("parrafos", []))
        out += (f'<div class="bloque"><div class="cab">{sev}{e(b["titulo"])}{etq}</div>'
                f'<div class="cuerpo">{parrafos}</div></div>')
    return out


def construir(d):
    cuerpo = cabecera(d)
    for s in d.get("secciones", []):
        partes = ""
        if s.get("parrafos"):
            partes += "".join(f'<p style="font-size:8pt;margin:0 0 8px 0">{enfasis(p)}</p>'
                              for p in s["parrafos"])
        if s.get("tabla"):
            partes += tabla(s["tabla"]["columnas"], s["tabla"]["filas"])
        if s.get("bloques"):
            partes += bloques(s["bloques"])
        if s.get("lista"):
            partes += '<ul class="limpia">' + "".join(
                f"<li>{enfasis(x)}</li>" for x in s["lista"]) + "</ul>"
        if s.get("nota"):
            partes += (f'<div class="nota"><span class="t">{e(s["nota"]["titulo"])}</span>'
                       + "".join(f'<p style="margin:0 0 5px 0">{enfasis(p)}</p>'
                                 for p in s["nota"]["parrafos"]) + "</div>")
        if s.get("decisiones"):
            for x in s["decisiones"]:
                partes += (f'<div class="decision"><div class="t">{e(x["titulo"])}</div>'
                           f'<div class="q">{enfasis(x["descripcion"])}</div>'
                           f'<div class="p">{e(x["plazo"])}</div></div>')
        cuerpo += seccion(s.get("num", ""), s.get("titulo", ""), partes, s.get("intro", ""))
    cuerpo += f'<div class="pie">{e(d.get("pie",""))}</div>'
    return (f'<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">'
            f'<title>{e(d.get("titulo",""))}</title>'
            f"<style>{css()}{css_extra()}</style></head><body>{cuerpo}</body></html>")


def main():
    if len(sys.argv) < 2:
        print("uso: python3 generar_reporte.py <archivo.json>", file=sys.stderr)
        sys.exit(1)
    ruta = Path(sys.argv[1])
    d = json.loads(ruta.read_text(encoding="utf-8"))
    SALIDA.mkdir(exist_ok=True)
    base = d.get("archivo") or ruta.stem
    html_p, pdf_p = SALIDA / f"{base}.html", SALIDA / f"{base}.pdf"
    html_p.write_text(construir(d), encoding="utf-8")
    print(f"  HTML  →  {html_p}")
    if html_a_pdf(html_p, pdf_p):
        print(f"  PDF   →  {pdf_p}")


if __name__ == "__main__":
    main()
