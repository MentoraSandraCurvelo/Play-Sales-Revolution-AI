"""Servidor MCP in-process: Meta Graph API (páginas, contenido y anuncios).

Da al CMO y al CDO acceso al rendimiento real del contenido y de las campañas, para
que las recomendaciones de marca descansen en métricas y no en intuición.
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


def construir_servidor_meta(settings: Settings) -> Any:
    base = f"https://graph.facebook.com/{settings.graph_api_version}"

    def cliente() -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=45.0)

    def con_token(params: dict[str, Any]) -> dict[str, Any]:
        return {**params, "access_token": settings.meta_access_token}

    @tool(
        "identidad",
        "Verifica a qué cuenta pertenece el token de Meta configurado y qué páginas "
        "administra. Úsalo primero si dudas de qué activos puedes consultar.",
        {"type": "object", "properties": {}, "additionalProperties": False},
    )
    async def identidad(_args: dict[str, Any]) -> dict[str, Any]:
        async with cliente() as c:
            ok_me, me = await pedir_json(
                c, "GET", f"{base}/me", params=con_token({"fields": "id,name"})
            )
            ok_pag, pags = await pedir_json(
                c,
                "GET",
                f"{base}/me/accounts",
                params=con_token({"fields": "id,name,category"}),
            )
        if not ok_me:
            return error(str(me))
        return datos(
            {
                "cuenta": me,
                "paginas": pags.get("data", []) if ok_pag and isinstance(pags, dict) else [],
                "pagina_configurada": settings.meta_page_id,
                "cuenta_publicitaria_configurada": settings.meta_ad_account_id,
            },
            "Identidad y activos accesibles en Meta",
        )

    @tool(
        "publicaciones_recientes",
        "Trae las publicaciones recientes de la página con sus métricas básicas "
        "(impresiones, interacciones, clics). Es la base para evaluar qué contenido "
        "funciona de verdad. Recuerda: alcance sin conversación comercial es vanidad.",
        {
            "type": "object",
            "properties": {
                "limite": {"type": "integer", "default": 15, "maximum": 50},
                "page_id": {
                    "type": "string",
                    "description": "Id de página. Si se omite, usa META_PAGE_ID.",
                },
            },
            "additionalProperties": False,
        },
    )
    async def publicaciones_recientes(args: dict[str, Any]) -> dict[str, Any]:
        page_id = args.get("page_id") or settings.meta_page_id
        if not page_id:
            return error(
                "no hay página configurada. Define META_PAGE_ID o pasa `page_id`."
            )
        params = con_token(
            {
                "limit": int(args.get("limite", 15)),
                "fields": (
                    "id,created_time,message,permalink_url,"
                    "insights.metric(post_impressions,post_engaged_users,post_clicks)"
                ),
            }
        )
        async with cliente() as c:
            ok, payload = await pedir_json(c, "GET", f"{base}/{page_id}/posts", params=params)
        if not ok:
            return error(str(payload))
        posts = payload.get("data", []) if isinstance(payload, dict) else []
        if not posts:
            return texto("La página no tiene publicaciones en el rango consultado.")
        return datos(posts, f"{len(posts)} publicación(es)")

    @tool(
        "metricas_pagina",
        "Consulta métricas agregadas de la página (impresiones, alcance, interacción, "
        "seguidores) en un rango de fechas. Úsalo para ver tendencia, no una foto.",
        {
            "type": "object",
            "properties": {
                "metricas": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Métricas de Meta. Por defecto: page_impressions, "
                    "page_post_engagements, page_fans.",
                },
                "desde": {"type": "string", "description": "Fecha inicial AAAA-MM-DD."},
                "hasta": {"type": "string", "description": "Fecha final AAAA-MM-DD."},
                "periodo": {
                    "type": "string",
                    "enum": ["day", "week", "days_28"],
                    "default": "day",
                },
                "page_id": {"type": "string"},
            },
            "additionalProperties": False,
        },
    )
    async def metricas_pagina(args: dict[str, Any]) -> dict[str, Any]:
        page_id = args.get("page_id") or settings.meta_page_id
        if not page_id:
            return error(
                "no hay página configurada. Define META_PAGE_ID o pasa `page_id`."
            )
        metricas = args.get("metricas") or [
            "page_impressions",
            "page_post_engagements",
            "page_fans",
        ]
        params: dict[str, Any] = {
            "metric": ",".join(metricas),
            "period": args.get("periodo", "day"),
        }
        if args.get("desde"):
            params["since"] = args["desde"]
        if args.get("hasta"):
            params["until"] = args["hasta"]
        async with cliente() as c:
            ok, payload = await pedir_json(
                c, "GET", f"{base}/{page_id}/insights", params=con_token(params)
            )
        if not ok:
            return error(str(payload))
        return datos(payload.get("data", payload), "Métricas de la página")

    @tool(
        "metricas_anuncios",
        "Consulta el rendimiento de las campañas publicitarias: gasto, impresiones, "
        "clics, CPC, CTR y conversiones. Imprescindible antes de opinar sobre si la "
        "inversión publicitaria se justifica.",
        {
            "type": "object",
            "properties": {
                "rango": {
                    "type": "string",
                    "enum": [
                        "today",
                        "yesterday",
                        "last_7d",
                        "last_14d",
                        "last_30d",
                        "last_90d",
                        "this_month",
                        "last_month",
                    ],
                    "default": "last_30d",
                },
                "nivel": {
                    "type": "string",
                    "enum": ["account", "campaign", "adset", "ad"],
                    "default": "campaign",
                },
                "ad_account_id": {
                    "type": "string",
                    "description": "Id de cuenta publicitaria con prefijo 'act_'. "
                    "Si se omite, usa META_AD_ACCOUNT_ID.",
                },
            },
            "additionalProperties": False,
        },
    )
    async def metricas_anuncios(args: dict[str, Any]) -> dict[str, Any]:
        cuenta = args.get("ad_account_id") or settings.meta_ad_account_id
        if not cuenta:
            return error(
                "no hay cuenta publicitaria configurada. Define META_AD_ACCOUNT_ID "
                "(con el prefijo 'act_') o pasa `ad_account_id`."
            )
        if not cuenta.startswith("act_"):
            cuenta = f"act_{cuenta}"
        params = con_token(
            {
                "level": args.get("nivel", "campaign"),
                "date_preset": args.get("rango", "last_30d"),
                "fields": (
                    "campaign_name,adset_name,ad_name,spend,impressions,clicks,"
                    "ctr,cpc,cpm,reach,actions"
                ),
                "limit": 50,
            }
        )
        async with cliente() as c:
            ok, payload = await pedir_json(
                c, "GET", f"{base}/{cuenta}/insights", params=params
            )
        if not ok:
            return error(str(payload))
        filas = payload.get("data", []) if isinstance(payload, dict) else []
        if not filas:
            return texto("No hay datos de anuncios en ese rango.")
        return datos(filas, f"{len(filas)} fila(s) de rendimiento publicitario")

    @tool(
        "publicar_en_pagina",
        "Publica una entrada en la página de Meta. Acción de escritura hacia el "
        "exterior: requiere que la junta NO esté en modo lectura. En modo lectura, "
        "entrega el texto propuesto para revisión humana en lugar de publicarlo.",
        {
            "type": "object",
            "properties": {
                "mensaje": {"type": "string", "description": "Texto de la publicación."},
                "enlace": {"type": "string", "description": "URL a adjuntar, opcional."},
                "page_id": {"type": "string"},
            },
            "required": ["mensaje"],
            "additionalProperties": False,
        },
    )
    async def publicar_en_pagina(args: dict[str, Any]) -> dict[str, Any]:
        if settings.modo_lectura:
            return bloqueado_por_modo_lectura("publicar_en_pagina de Meta")
        page_id = args.get("page_id") or settings.meta_page_id
        if not page_id:
            return error("no hay página configurada. Define META_PAGE_ID.")
        cuerpo: dict[str, Any] = {"message": args["mensaje"]}
        if args.get("enlace"):
            cuerpo["link"] = args["enlace"]
        async with cliente() as c:
            ok, payload = await pedir_json(
                c, "POST", f"{base}/{page_id}/feed", data=con_token(cuerpo)
            )
        if not ok:
            return error(str(payload))
        return datos(payload, "Publicación creada en la página")

    return create_sdk_mcp_server(
        name="meta",
        version="1.0.0",
        tools=[
            identidad,
            publicaciones_recientes,
            metricas_pagina,
            metricas_anuncios,
            publicar_en_pagina,
        ],
    )
