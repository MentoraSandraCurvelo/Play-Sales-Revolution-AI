"""Configuración del agente de WhatsApp.

Todas las credenciales se leen de variables de entorno. Nunca escribas
tokens dentro del código: usa el archivo .env (ver .env.example).
"""

import os

from dotenv import load_dotenv

load_dotenv()


def _requerido(nombre: str) -> str:
    valor = os.getenv(nombre, "").strip()
    if not valor:
        raise RuntimeError(
            f"Falta la variable de entorno {nombre}. "
            "Revisa tu archivo .env (guíate por .env.example)."
        )
    return valor


# --- Meta / WhatsApp Cloud API ---
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "").strip()
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "").strip()
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "").strip()
APP_SECRET = os.getenv("WHATSAPP_APP_SECRET", "").strip()
GRAPH_VERSION = os.getenv("WHATSAPP_GRAPH_VERSION", "v23.0").strip()

# --- Claude ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
MODELO = os.getenv("AGENTE_MODELO", "claude-opus-5").strip()
# low = respuestas rápidas y baratas (lo normal en chat).
# Súbelo a "medium" o "high" si quieres respuestas más elaboradas.
ESFUERZO = os.getenv("AGENTE_ESFUERZO", "low").strip()

# --- Negocio ---
NOMBRE_NEGOCIO = os.getenv("NOMBRE_NEGOCIO", "IAM · Sandra Curvelo")
LINK_AGENDA = os.getenv("LINK_AGENDA", "").strip()
NUMERO_ESCALAMIENTO = os.getenv("NUMERO_ESCALAMIENTO", "").strip()

# --- Almacenamiento ---
DB_PATH = os.getenv("DB_PATH", "whatsapp_agent.db")

# Máximo de turnos (usuario + agente) que se envían como historial a Claude.
MAX_TURNOS_HISTORIAL = int(os.getenv("MAX_TURNOS_HISTORIAL", "20"))

# WhatsApp corta los mensajes de texto en 4096 caracteres.
LIMITE_CARACTERES_WHATSAPP = 4000


def validar_configuracion() -> None:
    """Falla al arrancar si falta algo crítico, en vez de fallar en el primer mensaje."""
    for nombre in (
        "WHATSAPP_TOKEN",
        "WHATSAPP_PHONE_NUMBER_ID",
        "WHATSAPP_VERIFY_TOKEN",
        "WHATSAPP_APP_SECRET",
        "ANTHROPIC_API_KEY",
    ):
        _requerido(nombre)
