"""Cliente mínimo de la WhatsApp Cloud API (Meta) y verificación de firmas."""

import hashlib
import hmac
import logging

import httpx

from . import config

log = logging.getLogger(__name__)

_cliente = httpx.AsyncClient(timeout=20.0)


def _url() -> str:
    return f"https://graph.facebook.com/{config.GRAPH_VERSION}/{config.PHONE_NUMBER_ID}/messages"


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {config.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }


def firma_valida(cuerpo: bytes, cabecera: str | None) -> bool:
    """Comprueba X-Hub-Signature-256 contra el App Secret.

    Sin esto, cualquiera que conozca tu URL puede hacer que el agente responda
    (y te cueste dinero). Es la única defensa real del webhook.
    """
    if not cabecera or not cabecera.startswith("sha256="):
        return False
    esperado = hmac.new(
        config.APP_SECRET.encode("utf-8"), cuerpo, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(esperado, cabecera.removeprefix("sha256="))


def trocear(texto: str, limite: int = config.LIMITE_CARACTERES_WHATSAPP) -> list[str]:
    """WhatsApp corta en 4096 caracteres. Partimos por párrafos antes de llegar."""
    texto = texto.strip()
    if len(texto) <= limite:
        return [texto] if texto else []

    partes: list[str] = []
    actual = ""
    for parrafo in texto.split("\n\n"):
        if len(actual) + len(parrafo) + 2 > limite and actual:
            partes.append(actual.strip())
            actual = ""
        if len(parrafo) > limite:
            for i in range(0, len(parrafo), limite):
                partes.append(parrafo[i : i + limite])
        else:
            actual += parrafo + "\n\n"
    if actual.strip():
        partes.append(actual.strip())
    return partes


async def enviar_texto(destinatario: str, texto: str) -> None:
    for parte in trocear(texto):
        cuerpo = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": destinatario,
            "type": "text",
            "text": {"preview_url": True, "body": parte},
        }
        try:
            respuesta = await _cliente.post(_url(), json=cuerpo, headers=_headers())
            respuesta.raise_for_status()
        except httpx.HTTPStatusError as e:
            log.error("WhatsApp rechazó el envío (%s): %s", e.response.status_code, e.response.text)
        except httpx.HTTPError as e:
            log.error("Error de red enviando a WhatsApp: %s", e)


async def marcar_leido(message_id: str, escribiendo: bool = True) -> None:
    """Marca el mensaje como leído y muestra "escribiendo…" mientras Claude piensa."""
    cuerpo: dict = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id,
    }
    if escribiendo:
        cuerpo["typing_indicator"] = {"type": "text"}
    try:
        await _cliente.post(_url(), json=cuerpo, headers=_headers())
    except httpx.HTTPError as e:
        log.warning("No se pudo marcar como leído: %s", e)


async def cerrar() -> None:
    await _cliente.aclose()
