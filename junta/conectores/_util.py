"""Utilidades compartidas por los servidores MCP in-process."""

from __future__ import annotations

import json
from typing import Any

MAX_CARACTERES = 20_000
"""Tope de tamaño de una respuesta de herramienta. El SDK corta los resultados MCP
que superan ~25.000 tokens; recortamos antes para dar un mensaje claro en vez de un
error opaco."""


def texto(contenido: str) -> dict[str, Any]:
    """Respuesta de herramienta MCP con un bloque de texto."""
    if len(contenido) > MAX_CARACTERES:
        contenido = (
            contenido[:MAX_CARACTERES]
            + f"\n\n[...recortado: la respuesta superaba {MAX_CARACTERES} caracteres. "
            "Acota la consulta con filtros o un límite menor.]"
        )
    return {"content": [{"type": "text", "text": contenido}]}


def datos(payload: Any, encabezado: str | None = None) -> dict[str, Any]:
    """Respuesta con un payload JSON legible."""
    cuerpo = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
    if encabezado:
        cuerpo = f"{encabezado}\n\n{cuerpo}"
    return texto(cuerpo)


def error(mensaje: str) -> dict[str, Any]:
    """Respuesta de error. El agente la ve y puede corregir el rumbo.

    La clave es `is_error` en snake_case: es la que lee el SDK para marcar el
    resultado como fallido (`isError` en camelCase se ignora silenciosamente).
    """
    return {"content": [{"type": "text", "text": f"ERROR: {mensaje}"}], "is_error": True}


def bloqueado_por_modo_lectura(accion: str) -> dict[str, Any]:
    """Respuesta estándar cuando se intenta escribir hacia fuera en modo lectura."""
    return error(
        f"Acción bloqueada: '{accion}' escribe hacia un sistema externo y la junta "
        "está en MODO LECTURA. Una junta directiva delibera y recomienda; ejecutar "
        "hacia afuera es una decisión de Sandra. Para habilitarlo, se debe arrancar "
        "con JUNTA_MODO_LECTURA=false. Entrega el contenido propuesto para que ella "
        "lo revise y lo envíe."
    )


async def pedir_json(
    cliente: Any,
    metodo: str,
    url: str,
    **kwargs: Any,
) -> tuple[bool, Any]:
    """Ejecuta una petición HTTP y devuelve `(ok, payload_o_mensaje_de_error)`.

    Nunca lanza por un error de la API remota: el agente necesita ver el mensaje
    para poder reaccionar, no una traza.
    """
    try:
        respuesta = await cliente.request(metodo, url, **kwargs)
    except Exception as exc:  # red caída, DNS, timeout...
        return False, f"fallo de red hacia {url}: {exc}"

    if respuesta.status_code >= 400:
        detalle = respuesta.text[:1200]
        return False, f"HTTP {respuesta.status_code} en {url}: {detalle}"

    if not respuesta.content:
        return True, {}

    try:
        return True, respuesta.json()
    except ValueError:
        return True, {"_raw": respuesta.text[:MAX_CARACTERES]}
