"""El cerebro: arma el contexto, llama a Claude y ejecuta las herramientas."""

import asyncio
import logging
from collections import defaultdict
from typing import Any

import anthropic

from . import config, prompts, store

log = logging.getLogger(__name__)

_cliente = anthropic.AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY or None)

MAX_VUELTAS_HERRAMIENTAS = 4

# Un candado por conversación: si alguien manda dos mensajes seguidos, se
# procesan en orden y ninguno se pierde del historial.
_candados: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

RESPUESTA_ERROR = (
    "Se me cruzaron los cables un momento. ¿Me repites lo último, por favor?"
)


async def _ejecutar_herramienta(nombre: str, entrada: dict[str, Any], wa_id: str) -> tuple[str, bool]:
    """Devuelve (resultado_para_claude, hay_que_pausar_el_bot)."""
    if nombre == "registrar_lead":
        await store.guardar_lead(wa_id, entrada)
        log.info("Lead guardado (%s): %s", wa_id, entrada.get("nombre") or "sin nombre")
        return "Ficha guardada. No se lo menciones al usuario, sigue la conversación con naturalidad.", False

    if nombre == "escalar_a_humano":
        log.warning(
            "ESCALAMIENTO (%s) — motivo: %s | resumen: %s",
            wa_id,
            entrada.get("motivo"),
            entrada.get("resumen"),
        )
        return (
            "Conversación escalada. Sandra fue notificada. Despídete confirmando "
            "que ella responde personalmente y no hagas más preguntas.",
            True,
        )

    log.error("Herramienta desconocida: %s", nombre)
    return f"La herramienta {nombre} no existe.", False


async def responder(wa_id: str, texto_usuario: str, nombre_contacto: str | None) -> str | None:
    """Procesa un mensaje entrante y devuelve la respuesta a enviar (o None si el bot está en pausa)."""
    async with _candados[wa_id]:
        return await _responder(wa_id, texto_usuario, nombre_contacto)


async def _responder(wa_id: str, texto_usuario: str, nombre_contacto: str | None) -> str | None:
    conversacion = await store.leer_conversacion(wa_id)

    if conversacion["pausada"]:
        # Sandra ya tomó el control de este chat: guardamos el mensaje pero no contestamos.
        historial = conversacion["historial"] + [{"role": "user", "content": texto_usuario}]
        await store.guardar_conversacion(wa_id, nombre_contacto, historial, True)
        log.info("Chat en pausa (%s), no se responde.", wa_id)
        return None

    mensajes: list[dict[str, Any]] = list(conversacion["historial"])
    mensajes.append({"role": "user", "content": texto_usuario})

    contexto = f"Nombre que muestra WhatsApp: {nombre_contacto or 'desconocido'}."
    sistema = [
        {
            "type": "text",
            "text": prompts.SISTEMA,
            # El prompt de sistema no cambia entre mensajes: se cachea y abarata
            # cada llamada hasta un 90%.
            "cache_control": {"type": "ephemeral"},
        },
        {"type": "text", "text": contexto},
    ]

    pausar = False
    texto_final = ""

    try:
        for _ in range(MAX_VUELTAS_HERRAMIENTAS):
            respuesta = await _cliente.messages.create(
                model=config.MODELO,
                max_tokens=2000,
                system=sistema,
                messages=mensajes,
                tools=prompts.HERRAMIENTAS,
                thinking={"type": "adaptive"},
                output_config={"effort": config.ESFUERZO},
            )

            if respuesta.stop_reason == "refusal":
                log.warning("Claude declinó responder (%s).", wa_id)
                texto_final = (
                    "Prefiero que este tema lo veas directamente con Sandra. "
                    "Ya le paso tu mensaje."
                )
                pausar = True
                break

            texto_final = "".join(
                bloque.text for bloque in respuesta.content if bloque.type == "text"
            ).strip()

            if respuesta.stop_reason != "tool_use":
                break

            # Hay que devolver los bloques tal cual llegaron (incluido el thinking).
            mensajes.append({"role": "assistant", "content": respuesta.content})

            resultados = []
            for bloque in respuesta.content:
                if bloque.type != "tool_use":
                    continue
                salida, pausar_ahora = await _ejecutar_herramienta(
                    bloque.name, dict(bloque.input), wa_id
                )
                pausar = pausar or pausar_ahora
                resultados.append(
                    {"type": "tool_result", "tool_use_id": bloque.id, "content": salida}
                )
            # Todos los tool_result van en UN solo mensaje de usuario.
            mensajes.append({"role": "user", "content": resultados})

    except anthropic.RateLimitError:
        log.error("Límite de peticiones de la API alcanzado (%s).", wa_id)
        return "Estoy recibiendo muchos mensajes ahora mismo. Dame un minuto y te respondo."
    except anthropic.APIError as e:
        log.exception("Error de la API de Claude (%s): %s", wa_id, e)
        return RESPUESTA_ERROR

    if not texto_final:
        texto_final = RESPUESTA_ERROR

    # Guardamos solo el texto de los turnos: el ida y vuelta de herramientas no
    # necesita persistirse y mantiene el historial liviano.
    historial = list(conversacion["historial"])
    historial.append({"role": "user", "content": texto_usuario})
    historial.append({"role": "assistant", "content": texto_final})
    await store.guardar_conversacion(wa_id, nombre_contacto, historial, pausar)

    return texto_final
