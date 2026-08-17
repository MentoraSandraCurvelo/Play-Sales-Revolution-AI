"""Configuración de la Junta Directiva IAM™.

Todo se lee de variables de entorno (o de un archivo `.env`). Los conectores son
opt-in: si faltan las credenciales de un servicio, ese conector simplemente no se
monta y la junta sigue funcionando con el resto.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:  # python-dotenv es opcional; si está, carga .env automáticamente
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover - entorno sin dotenv
    pass


RAIZ = Path(__file__).resolve().parent.parent

# Modelos. Opus 5 para los consejeros que hacen análisis de fondo; el resto puede
# bajarse a Sonnet 5 desde el .env si se quiere abaratar la operación.
MODELO_PRINCIPAL = "claude-opus-5"
MODELO_APOYO = "claude-opus-5"


def _flag(nombre: str, por_defecto: bool = False) -> bool:
    valor = os.environ.get(nombre)
    if valor is None:
        return por_defecto
    return valor.strip().lower() in {"1", "true", "si", "sí", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Configuración resuelta de una ejecución de la junta."""

    # --- Rutas ---
    raiz: Path = RAIZ
    dir_contexto: Path = RAIZ / "contexto"
    dir_salidas: Path = RAIZ / "salidas"

    # --- Modelos ---
    modelo_presidencia: str = MODELO_PRINCIPAL
    modelo_consejeros: str = MODELO_APOYO
    esfuerzo: str = "high"

    # --- Anthropic ---
    anthropic_api_key: str | None = None

    # --- Supabase (memoria) ---
    supabase_url: str | None = None
    supabase_key: str | None = None

    # --- Airtable ---
    airtable_api_key: str | None = None

    # --- Notion ---
    notion_token: str | None = None

    # --- Google (Gmail + Drive) ---
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_refresh_token: str | None = None

    # --- WhatsApp Cloud API ---
    whatsapp_token: str | None = None
    whatsapp_phone_number_id: str | None = None
    whatsapp_waba_id: str | None = None

    # --- Meta Graph API ---
    meta_access_token: str | None = None
    meta_page_id: str | None = None
    meta_ad_account_id: str | None = None

    # --- Versión de la Graph API (WhatsApp y Meta comparten host) ---
    graph_api_version: str = "v21.0"

    # --- Comportamiento ---
    modo_lectura: bool = True
    """Si es True, los conectores no ejecutan acciones de escritura hacia afuera
    (enviar WhatsApp, publicar en Meta, enviar correo). Es el valor por defecto:
    una junta directiva delibera y recomienda; ejecutar hacia el exterior exige
    activarlo explícitamente."""

    max_turnos: int = 60

    extras: dict[str, str] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Disponibilidad de conectores
    # ------------------------------------------------------------------
    @property
    def tiene_supabase(self) -> bool:
        return bool(self.supabase_url and self.supabase_key)

    @property
    def tiene_airtable(self) -> bool:
        return bool(self.airtable_api_key)

    @property
    def tiene_notion(self) -> bool:
        return bool(self.notion_token)

    @property
    def tiene_google(self) -> bool:
        return bool(
            self.google_client_id
            and self.google_client_secret
            and self.google_refresh_token
        )

    @property
    def tiene_whatsapp(self) -> bool:
        return bool(self.whatsapp_token and self.whatsapp_phone_number_id)

    @property
    def tiene_meta(self) -> bool:
        return bool(self.meta_access_token)

    def conectores_activos(self) -> list[str]:
        """Nombres de los servidores MCP que se van a montar."""
        activos: list[str] = []
        if self.tiene_airtable:
            activos.append("airtable")
        if self.tiene_notion:
            activos.append("notion")
        if self.tiene_google:
            activos.append("google")
        if self.tiene_whatsapp:
            activos.append("whatsapp")
        if self.tiene_meta:
            activos.append("meta")
        if self.tiene_supabase:
            activos.append("memoria")
        return activos

    def conectores_faltantes(self) -> dict[str, str]:
        """Conectores no configurados y qué variable de entorno les falta."""
        faltantes: dict[str, str] = {}
        if not self.tiene_airtable:
            faltantes["airtable"] = "AIRTABLE_API_KEY"
        if not self.tiene_notion:
            faltantes["notion"] = "NOTION_TOKEN"
        if not self.tiene_google:
            faltantes["google"] = (
                "GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET + GOOGLE_REFRESH_TOKEN"
            )
        if not self.tiene_whatsapp:
            faltantes["whatsapp"] = "WHATSAPP_TOKEN + WHATSAPP_PHONE_NUMBER_ID"
        if not self.tiene_meta:
            faltantes["meta"] = "META_ACCESS_TOKEN"
        if not self.tiene_supabase:
            faltantes["memoria"] = "SUPABASE_URL + SUPABASE_KEY"
        return faltantes


def cargar_settings(**overrides: object) -> Settings:
    """Construye los `Settings` desde el entorno, con overrides opcionales."""
    base = Settings(
        modelo_presidencia=os.environ.get("JUNTA_MODELO_PRESIDENCIA", MODELO_PRINCIPAL),
        modelo_consejeros=os.environ.get("JUNTA_MODELO_CONSEJEROS", MODELO_APOYO),
        esfuerzo=os.environ.get("JUNTA_ESFUERZO", "high"),
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
        supabase_url=os.environ.get("SUPABASE_URL"),
        supabase_key=os.environ.get("SUPABASE_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY"),
        airtable_api_key=os.environ.get("AIRTABLE_API_KEY"),
        notion_token=os.environ.get("NOTION_TOKEN"),
        google_client_id=os.environ.get("GOOGLE_CLIENT_ID"),
        google_client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
        google_refresh_token=os.environ.get("GOOGLE_REFRESH_TOKEN"),
        whatsapp_token=os.environ.get("WHATSAPP_TOKEN"),
        whatsapp_phone_number_id=os.environ.get("WHATSAPP_PHONE_NUMBER_ID"),
        whatsapp_waba_id=os.environ.get("WHATSAPP_WABA_ID"),
        meta_access_token=os.environ.get("META_ACCESS_TOKEN"),
        meta_page_id=os.environ.get("META_PAGE_ID"),
        meta_ad_account_id=os.environ.get("META_AD_ACCOUNT_ID"),
        graph_api_version=os.environ.get("GRAPH_API_VERSION", "v21.0"),
        modo_lectura=_flag("JUNTA_MODO_LECTURA", True),
        max_turnos=int(os.environ.get("JUNTA_MAX_TURNOS", "60")),
    )
    if overrides:
        from dataclasses import replace

        base = replace(base, **overrides)  # type: ignore[arg-type]
    base.dir_salidas.mkdir(parents=True, exist_ok=True)
    return base
