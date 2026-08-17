"""Servidor MCP in-process: WhatsApp Cloud API (Meta).

Alcance real de la API: la Cloud API permite **enviar** mensajes y consultar
plantillas y perfil de empresa. Los mensajes **entrantes** solo llegan por webhook,
no hay endpoint para leer el historial. Por eso aquí no existe una herramienta de
"leer conversaciones": prometerla sería mentirle al agente.

Si quieres que la junta lea entrantes, la vía es: webhook → guardar en Supabase →
consultarlo desde el conector de memoria.
"""

from __future__ import annotations

from typing import Any

import httpx
from claude_agent_sdk import create_sdk_mcp_server, tool

from junta.conectores._util import (
    bloqueado_por_modo_lectura,
    datos,
    error,
    pedir_json,
    texto,
)
from junta.config import Settings


def construir_servidor_whatsapp(settings: Settings) -> Any:
    base = f"https://graph.facebook.com/{settings.graph_api_version}"
    cabeceras = {
        "Authorization": f"Bearer {settings.whatsapp_token}",
        "Content-Type": "application/json",
    }

    def cliente() -> httpx.AsyncClient:
        return httpx.AsyncClient(headers=cabeceras, timeout=30.0)

    @tool(
        "enviar_mensaje",
        "Envía un mensaje de texto de WhatsApp a un número. Solo funciona si el "
        "destinatario escribió en las últimas 24 horas (ventana de servicio de Meta); "
        "fuera de esa ventana hay que usar `enviar_plantilla`. Acción de escritura: "
        "requiere que la junta NO esté en modo lectura.",
        {
            "type": "object",
            "properties": {
                "telefono": {
                    "type": "string",
                    "description": "Número en formato internacional sin '+' ni espacios. "
                    "Ej: 573001234567",
                },
                "mensaje": {"type": "string", "description": "Texto a enviar."},
            },
            "required": ["telefono", "mensaje"],
            "additionalProperties": False,
        },
    )
    async def enviar_mensaje(args: dict[str, Any]) -> dict[str, Any]:
        if settings.modo_lectura:
            return bloqueado_por_modo_lectura("enviar_mensaje de WhatsApp")
        url = f"{base}/{settings.whatsapp_phone_number_id}/messages"
        cuerpo = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": args["telefono"],
            "type": "text",
            "text": {"preview_url": False, "body": args["mensaje"]},
        }
        async with cliente() as c:
            ok, payload = await pedir_json(c, "POST", url, json=cuerpo)
        if not ok:
            return error(str(payload))
        return datos(payload, "Mensaje de WhatsApp enviado")

    @tool(
        "enviar_plantilla",
        "Envía una plantilla de WhatsApp previamente aprobada por Meta. Es la única "
        "forma de iniciar conversación fuera de la ventana de 24 horas. Consulta "
        "primero `listar_plantillas` para conocer el nombre exacto y sus variables. "
        "Acción de escritura: requiere que la junta NO esté en modo lectura.",
        {
            "type": "object",
            "properties": {
                "telefono": {
                    "type": "string",
                    "description": "Número internacional sin '+'. Ej: 573001234567",
                },
                "plantilla": {"type": "string", "description": "Nombre de la plantilla."},
                "idioma": {
                    "type": "string",
                    "default": "es",
                    "description": "Código de idioma de la plantilla. Ej: es, es_CO, en_US.",
                },
                "variables": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Valores de las variables {{1}}, {{2}}... en orden.",
                },
            },
            "required": ["telefono", "plantilla"],
            "additionalProperties": False,
        },
    )
    async def enviar_plantilla(args: dict[str, Any]) -> dict[str, Any]:
        if settings.modo_lectura:
            return bloqueado_por_modo_lectura("enviar_plantilla de WhatsApp")
        url = f"{base}/{settings.whatsapp_phone_number_id}/messages"
        plantilla: dict[str, Any] = {
            "name": args["plantilla"],
            "language": {"code": args.get("idioma", "es")},
        }
        variables = args.get("variables") or []
        if variables:
            plantilla["components"] = [
                {
                    "type": "body",
                    "parameters": [{"type": "text", "text": v} for v in variables],
                }
            ]
        cuerpo = {
            "messaging_product": "whatsapp",
            "to": args["telefono"],
            "type": "template",
            "template": plantilla,
        }
        async with cliente() as c:
            ok, payload = await pedir_json(c, "POST", url, json=cuerpo)
        if not ok:
            return error(str(payload))
        return datos(payload, "Plantilla de WhatsApp enviada")

    @tool(
        "listar_plantillas",
        "Lista las plantillas de mensaje de WhatsApp de la cuenta y su estado de "
        "aprobación en Meta. Úsalo antes de proponer un envío para saber qué hay "
        "disponible y qué variables espera cada plantilla.",
        {
            "type": "object",
            "properties": {"limite": {"type": "integer", "default": 25, "maximum": 100}},
            "additionalProperties": False,
        },
    )
    async def listar_plantillas(args: dict[str, Any]) -> dict[str, Any]:
        if not settings.whatsapp_waba_id:
            return error(
                "falta WHATSAPP_WABA_ID en el entorno (el id de la WhatsApp Business "
                "Account). Sin él no se pueden listar las plantillas."
            )
        url = f"{base}/{settings.whatsapp_waba_id}/message_templates"
        params = {
            "limit": int(args.get("limite", 25)),
            "fields": "name,status,category,language,components",
        }
        async with cliente() as c:
            ok, payload = await pedir_json(c, "GET", url, params=params)
        if not ok:
            return error(str(payload))
        plantillas = payload.get("data", []) if isinstance(payload, dict) else []
        if not plantillas:
            return texto("La cuenta no tiene plantillas de WhatsApp registradas.")
        return datos(plantillas, f"{len(plantillas)} plantilla(s)")

    @tool(
        "perfil_empresa",
        "Consulta el perfil de empresa asociado al número de WhatsApp: descripción, "
        "sector, dirección, sitio web. Útil para revisar coherencia de marca.",
        {"type": "object", "properties": {}, "additionalProperties": False},
    )
    async def perfil_empresa(_args: dict[str, Any]) -> dict[str, Any]:
        url = f"{base}/{settings.whatsapp_phone_number_id}/whatsapp_business_profile"
        params = {
            "fields": "about,address,description,email,profile_picture_url,websites,vertical"
        }
        async with cliente() as c:
            ok, payload = await pedir_json(c, "GET", url, params=params)
        if not ok:
            return error(str(payload))
        return datos(payload, "Perfil de empresa en WhatsApp")

    return create_sdk_mcp_server(
        name="whatsapp",
        version="1.0.0",
        tools=[enviar_mensaje, enviar_plantilla, listar_plantillas, perfil_empresa],
    )
