"""Webhook de WhatsApp. Arranca con:

    uvicorn whatsapp_agent.main:app --host 0.0.0.0 --port 8000
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request, Response

from . import agent, config, store, whatsapp_api

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
log = logging.getLogger("whatsapp_agent")

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "").strip()

TIPOS_NO_SOPORTADOS = {
    "audio": "Por ahora solo leo texto. ¿Me lo escribes en un mensaje?",
    "image": "Recibí tu imagen, pero todavía no puedo verla. ¿Me cuentas por escrito de qué se trata?",
    "video": "Recibí tu video, pero todavía no puedo verlo. ¿Me lo resumes por escrito?",
    "document": "Recibí tu documento. Aún no puedo abrirlo aquí; cuéntame por escrito qué necesitas.",
    "sticker": "😄 Cuéntame, ¿en qué te ayudo?",
    "location": "Gracias por la ubicación. Cuéntame en qué te puedo ayudar.",
}


@asynccontextmanager
async def ciclo_de_vida(_: FastAPI):
    config.validar_configuracion()
    log.info("Agente listo. Modelo: %s (esfuerzo: %s)", config.MODELO, config.ESFUERZO)
    yield
    await whatsapp_api.cerrar()


app = FastAPI(title="Agente WhatsApp · IAM", lifespan=ciclo_de_vida)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/webhook")
async def verificar(request: Request) -> Response:
    """Meta llama aquí una sola vez, al configurar el webhook."""
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == config.VERIFY_TOKEN
    ):
        log.info("Webhook verificado por Meta.")
        return Response(content=params.get("hub.challenge", ""), media_type="text/plain")
    log.warning("Intento de verificación con token incorrecto.")
    raise HTTPException(status_code=403, detail="Token de verificación inválido")


@app.post("/webhook")
async def recibir(
    request: Request,
    tareas: BackgroundTasks,
    x_hub_signature_256: str | None = Header(default=None),
) -> Response:
    crudo = await request.body()

    if not whatsapp_api.firma_valida(crudo, x_hub_signature_256):
        log.warning("Firma inválida: petición descartada.")
        raise HTTPException(status_code=403, detail="Firma inválida")

    payload = await request.json()

    # Respondemos 200 de inmediato y procesamos aparte: si tardamos, Meta
    # reintenta el webhook y el usuario recibe respuestas duplicadas.
    tareas.add_task(_procesar, payload)
    return Response(status_code=200)


async def _procesar(payload: dict) -> None:
    try:
        for entrada in payload.get("entry", []):
            for cambio in entrada.get("changes", []):
                valor = cambio.get("value", {})
                nombres = {
                    c.get("wa_id"): c.get("profile", {}).get("name")
                    for c in valor.get("contacts", [])
                }
                for mensaje in valor.get("messages", []):
                    await _procesar_mensaje(mensaje, nombres)
    except Exception:
        log.exception("Fallo procesando el webhook.")


async def _procesar_mensaje(mensaje: dict, nombres: dict) -> None:
    message_id = mensaje.get("id", "")
    wa_id = mensaje.get("from", "")
    tipo = mensaje.get("type", "")

    if not message_id or not wa_id:
        return

    if not await store.es_mensaje_nuevo(message_id):
        log.info("Mensaje duplicado ignorado: %s", message_id)
        return

    await whatsapp_api.marcar_leido(message_id)

    if tipo == "text":
        texto = mensaje.get("text", {}).get("body", "").strip()
    elif tipo == "interactive":
        interactivo = mensaje.get("interactive", {})
        texto = (
            interactivo.get("button_reply", {}).get("title")
            or interactivo.get("list_reply", {}).get("title")
            or ""
        ).strip()
    elif tipo == "button":
        texto = mensaje.get("button", {}).get("text", "").strip()
    else:
        aviso = TIPOS_NO_SOPORTADOS.get(tipo)
        if aviso:
            await whatsapp_api.enviar_texto(wa_id, aviso)
        else:
            log.info("Tipo de mensaje sin manejar: %s", tipo)
        return

    if not texto:
        return

    nombre = nombres.get(wa_id)
    log.info("Mensaje de %s (%s): %s", nombre or "?", wa_id, texto[:120])

    respuesta = await agent.responder(wa_id, texto, nombre)
    if respuesta:
        await whatsapp_api.enviar_texto(wa_id, respuesta)


@app.get("/leads")
async def leads(authorization: str | None = Header(default=None)) -> dict:
    """Consulta rápida de los leads capturados. Requiere ADMIN_TOKEN configurado."""
    if not ADMIN_TOKEN:
        raise HTTPException(status_code=404, detail="No disponible")
    if authorization != f"Bearer {ADMIN_TOKEN}":
        raise HTTPException(status_code=401, detail="No autorizado")
    return {"leads": await store.listar_leads()}


@app.post("/reanudar/{wa_id}")
async def reanudar(wa_id: str, authorization: str | None = Header(default=None)) -> dict:
    """Devuelve el control al agente en un chat que fue escalado a Sandra."""
    if not ADMIN_TOKEN:
        raise HTTPException(status_code=404, detail="No disponible")
    if authorization != f"Bearer {ADMIN_TOKEN}":
        raise HTTPException(status_code=401, detail="No autorizado")
    await store.pausar(wa_id, False)
    return {"wa_id": wa_id, "pausada": False}
