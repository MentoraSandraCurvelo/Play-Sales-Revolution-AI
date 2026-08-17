"""Ensamblado de los conectores MCP de la junta.

Cada conector es opt-in: si faltan sus credenciales, no se monta. La junta arranca
igual y avisa qué le falta, en vez de fallar entera por un servicio no configurado.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from junta.config import Settings
from junta.memoria.repositorio import RepositorioMemoria


@dataclass
class Conectores:
    """Resultado del ensamblado."""

    servidores: dict[str, Any] = field(default_factory=dict)
    herramientas_permitidas: list[str] = field(default_factory=list)
    fijar_sesion_memoria: Callable[[str | None], None] | None = None
    avisos: list[str] = field(default_factory=list)

    @property
    def activos(self) -> list[str]:
        return sorted(self.servidores)


def construir_conectores(
    settings: Settings,
    repo: RepositorioMemoria | None = None,
) -> Conectores:
    """Monta todos los servidores MCP disponibles según la configuración."""
    resultado = Conectores()

    def registrar(nombre: str, servidor: Any) -> None:
        resultado.servidores[nombre] = servidor
        resultado.herramientas_permitidas.append(f"mcp__{nombre}__*")

    # --- Airtable (servidor externo por stdio) ---------------------------
    if settings.tiene_airtable:
        registrar(
            "airtable",
            {
                "command": "npx",
                "args": ["-y", "airtable-mcp-server"],
                "env": {"AIRTABLE_API_KEY": settings.airtable_api_key or ""},
            },
        )
    else:
        resultado.avisos.append(
            "Airtable no configurado (falta AIRTABLE_API_KEY): el CRO y el CFO no "
            "podrán leer el pipeline real."
        )

    # --- Notion (servidor oficial por stdio) -----------------------------
    if settings.tiene_notion:
        registrar(
            "notion",
            {
                "command": "npx",
                "args": ["-y", "@notionhq/notion-mcp-server"],
                "env": {"NOTION_TOKEN": settings.notion_token or ""},
            },
        )
    else:
        resultado.avisos.append(
            "Notion no configurado (falta NOTION_TOKEN): la junta no podrá consultar "
            "la documentación de procesos ni de programas."
        )

    # --- Google: Gmail + Drive (in-process) ------------------------------
    if settings.tiene_google:
        from junta.conectores.google import construir_servidor_google

        registrar("google", construir_servidor_google(settings))
    else:
        resultado.avisos.append(
            "Google no configurado (faltan GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET / "
            "GOOGLE_REFRESH_TOKEN): sin acceso a Gmail ni a Drive."
        )

    # --- WhatsApp Cloud API (in-process) ---------------------------------
    if settings.tiene_whatsapp:
        from junta.conectores.whatsapp import construir_servidor_whatsapp

        registrar("whatsapp", construir_servidor_whatsapp(settings))
    else:
        resultado.avisos.append(
            "WhatsApp no configurado (faltan WHATSAPP_TOKEN / WHATSAPP_PHONE_NUMBER_ID)."
        )

    # --- Meta Graph API (in-process) -------------------------------------
    if settings.tiene_meta:
        from junta.conectores.meta import construir_servidor_meta

        registrar("meta", construir_servidor_meta(settings))
    else:
        resultado.avisos.append(
            "Meta no configurado (falta META_ACCESS_TOKEN): el CMO trabajará sin "
            "métricas reales de contenido ni de campañas."
        )

    # --- Memoria en Supabase (in-process) --------------------------------
    if repo is not None:
        from junta.conectores.memoria_mcp import construir_servidor_memoria

        servidor, fijar_sesion = construir_servidor_memoria(repo)
        registrar("memoria", servidor)
        resultado.fijar_sesion_memoria = fijar_sesion
    else:
        resultado.avisos.append(
            "Supabase no configurado (faltan SUPABASE_URL / SUPABASE_KEY): la junta "
            "funcionará SIN MEMORIA. Cada sesión empezará de cero."
        )

    return resultado
