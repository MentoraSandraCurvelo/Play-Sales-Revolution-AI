"""MATIA: agente que envía 10 toques de valor diarios al pipeline (modo simulado)."""

from __future__ import annotations

import html
import random
from dataclasses import asdict
from datetime import date, datetime

from .contenido import ANGULO_ETAPA, ASUNTOS, DOLORES, MARCA
from .crm_simulado import ETAPAS, Actividad, Deal

CORREOS_POR_DIA = 10
DIAS_MINIMOS_ENTRE_TOQUES = 3


def puntaje_prioridad(deal: Deal, hoy: date) -> float:
    """Prioridad = valor ponderado (en millones) x días sin toque. Más alto, primero."""
    return (deal.valor_ponderado / 1_000_000) * max(deal.dias_sin_toque(hoy), 1)


def seleccionar_del_dia(deals: list[Deal], hoy: date, n: int = CORREOS_POR_DIA) -> list[Deal]:
    """El Cliente Demo siempre entra (es para la clase); el resto por prioridad."""
    elegibles = [d for d in deals if d.dias_sin_toque(hoy) >= DIAS_MINIMOS_ENTRE_TOQUES or d.demo]
    elegibles.sort(key=lambda d: (not d.demo, -puntaje_prioridad(d, hoy)))
    return elegibles[:n]


def _dolor_del_toque(deal: Deal) -> int:
    """Rota el dolor destacado en cada toque, empezando por el principal del cliente."""
    return (deal.dolor_principal + deal.toques_matia) % len(DOLORES)


def generar_correo(deal: Deal) -> dict:
    nombre = deal.contacto.split()[0]
    foco = _dolor_del_toque(deal)
    asunto = ASUNTOS[deal.toques_matia % len(ASUNTOS)].format(
        nombre=nombre, empresa=deal.empresa, industria=deal.industria.lower()
    )
    return {
        "deal_id": deal.id,
        "para": deal.email,
        "contacto": deal.contacto,
        "empresa": deal.empresa,
        "etapa": deal.etapa,
        "asunto": asunto,
        "dolor_foco": DOLORES[foco]["titulo"],
        "html": render_html(deal, nombre, foco),
    }


def render_html(deal: Deal, nombre: str, foco: int) -> str:
    m = MARCA
    e = html.escape
    tarjetas = ""
    for i, dolor in enumerate(DOLORES):
        destacado = i == foco
        borde = m["rojo"] if destacado else "#2a2d36"
        etiqueta = (
            f'<span style="background:{m["rojo"]};color:#fff;font-size:11px;font-weight:600;'
            f'padding:3px 8px;border-radius:3px;letter-spacing:.5px;">EL QUE MÁS VEO EN {e(deal.industria.upper())}</span><br><br>'
            if destacado else ""
        )
        tarjetas += f"""
        <tr><td style="padding:8px 0;">
          <table width="100%" cellpadding="0" cellspacing="0" style="background:{m['gris']};border-left:4px solid {borde};border-radius:4px;">
            <tr><td style="padding:18px 20px;">
              {etiqueta}
              <div style="color:{m['rojo']};font-size:13px;font-weight:600;">DOLOR {i + 1}</div>
              <div style="color:{m['blanco']};font-size:17px;font-weight:600;margin:4px 0 8px;">{e(dolor['titulo'])}</div>
              <div style="color:{m['texto_suave']};font-size:14px;line-height:1.5;">{e(dolor['sintoma'])} {e(dolor['consecuencia'])}</div>
            </td></tr>
          </table>
        </td></tr>"""

    d = DOLORES[foco]
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap" rel="stylesheet"></head>
<body style="margin:0;background:{m['negro']};font-family:{m['fuente']};">
<table width="100%" cellpadding="0" cellspacing="0" style="background:{m['negro']};"><tr><td align="center" style="padding:24px 12px;">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">
  <tr><td style="padding:0 0 20px;border-bottom:3px solid {m['rojo']};">
    <span style="color:{m['blanco']};font-size:22px;font-weight:800;letter-spacing:1px;">{e(m['nombre'])}</span>
    <span style="color:{m['rojo']};font-size:22px;font-weight:800;"> ●</span>
    <div style="color:{m['texto_suave']};font-size:12px;letter-spacing:2px;margin-top:4px;">SOCIAL SELLING · MARCA PROFESIONAL</div>
  </td></tr>
  <tr><td style="padding:28px 0 8px;color:{m['blanco']};font-size:16px;line-height:1.6;">
    Hola {e(nombre)},<br><br>{e(ANGULO_ETAPA[deal.etapa])}<br><br>
    Trabajando con equipos comerciales veo que casi siempre aparecen estos <b style="color:{m['rojo']};">3 dolores</b>:
  </td></tr>
  {tarjetas}
  <tr><td style="padding:22px 0 6px;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background:{m['rojo']};border-radius:4px;"><tr><td style="padding:20px 22px;color:#fff;">
      <div style="font-size:12px;font-weight:600;letter-spacing:1.5px;">TOQUE DE VALOR PARA {e(deal.empresa.upper())}</div>
      <div style="font-size:15px;line-height:1.6;margin-top:8px;">{e(d['valor'])}</div>
      <div style="font-size:14px;line-height:1.6;margin-top:10px;font-weight:600;">{e(d['tip'])}</div>
    </td></tr></table>
  </td></tr>
  <tr><td align="center" style="padding:26px 0;">
    <a href="{e(m['cta_url'])}" style="background:{m['blanco']};color:{m['negro']};text-decoration:none;font-weight:800;font-size:14px;padding:14px 28px;border-radius:4px;display:inline-block;">Agendemos 20 minutos</a>
  </td></tr>
  <tr><td style="padding:18px 0;border-top:1px solid #2a2d36;color:{m['texto_suave']};font-size:13px;line-height:1.6;">
    <b style="color:{m['blanco']};">{e(m['firma'])}</b><br>{e(m['rol'])}<br>{e(m['nombre'])}
    <div style="font-size:11px;margin-top:14px;color:#6b6f7b;">Correo de demostración generado por MATIA en modo simulado. No fue enviado a ninguna persona real.</div>
  </td></tr>
</table></td></tr></table></body></html>"""


def ejecutar_dia(deals: list[Deal], hoy: date, semilla: int | None = None) -> dict:
    """Corre la jornada de MATIA: selecciona, genera, 'envía' y actualiza el CRM simulado."""
    rnd = random.Random(semilla if semilla is not None else hoy.toordinal())
    seleccion = seleccionar_del_dia(deals, hoy)
    enviados = []
    ahora = datetime.now().strftime("%H:%M")
    for deal in seleccion:
        correo = generar_correo(deal)
        correo["hora"] = ahora
        correo["estado"] = "Enviado (simulado)"
        # Simulación de respuesta: el Cliente Demo responde siempre para que la clase vea el avance
        respondio = deal.demo or rnd.random() < 0.2
        deal.actividades.append(asdict(Actividad(hoy.isoformat(), "Correo MATIA", f"Toque de valor: {correo['dolor_foco']}. Asunto: {correo['asunto']}")))
        deal.ultimo_toque = hoy.isoformat()
        deal.toques_matia += 1
        if respondio:
            correo["estado"] = "Respondió (simulado)"
            idx = ETAPAS.index(deal.etapa)
            if idx < len(ETAPAS) - 1:
                anterior, deal.etapa = deal.etapa, ETAPAS[idx + 1]
                deal.actividades.append(asdict(Actividad(hoy.isoformat(), "Cambio de etapa", f"{anterior} → {deal.etapa} tras respuesta al correo.")))
            else:
                deal.actividades.append(asdict(Actividad(hoy.isoformat(), "Respuesta", "El cliente respondió, listo para cierre.")))
        enviados.append(correo)
    return {"fecha": hoy.isoformat(), "enviados": enviados}
