"""Prueba de humo sin gastar dinero ni conectar cuentas reales.

Simula un webhook de Meta y una respuesta de Claude para verificar que toda la
cañería funciona: firma, deduplicación, historial, herramientas y envío.

    python -m whatsapp_agent.prueba_local
"""

import hashlib
import hmac
import json
import os
import tempfile
from types import SimpleNamespace

# Credenciales de mentira: esto debe ir ANTES de importar el paquete.
os.environ.update(
    {
        "WHATSAPP_TOKEN": "token-de-prueba",
        "WHATSAPP_PHONE_NUMBER_ID": "000000000000000",
        "WHATSAPP_VERIFY_TOKEN": "verificacion-de-prueba",
        "WHATSAPP_APP_SECRET": "secreto-de-prueba",
        "ANTHROPIC_API_KEY": "sk-ant-de-prueba",
        "DB_PATH": os.path.join(tempfile.mkdtemp(), "prueba.db"),
        "ADMIN_TOKEN": "admin-de-prueba",
    }
)

from fastapi.testclient import TestClient  # noqa: E402

from whatsapp_agent import agent, config, main, store, whatsapp_api  # noqa: E402

ENVIADOS: list[tuple[str, str]] = []
GUION: list[SimpleNamespace] = []


def _bloque_texto(texto):
    return SimpleNamespace(type="text", text=texto)


def _bloque_herramienta(nombre, entrada, id_="tu_1"):
    return SimpleNamespace(type="tool_use", name=nombre, input=entrada, id=id_)


async def _claude_falso(**kwargs):
    assert kwargs["model"] == config.MODELO
    assert kwargs["messages"][0]["role"] == "user", "El historial debe empezar en 'user'"
    return GUION.pop(0)


async def _enviar_falso(destinatario, texto):
    ENVIADOS.append((destinatario, texto))


async def _leido_falso(message_id, escribiendo=True):
    return None


agent._cliente.messages.create = _claude_falso
whatsapp_api.enviar_texto = _enviar_falso
main.whatsapp_api.enviar_texto = _enviar_falso
main.whatsapp_api.marcar_leido = _leido_falso


def _firmar(cuerpo: bytes) -> str:
    return "sha256=" + hmac.new(
        config.APP_SECRET.encode(), cuerpo, hashlib.sha256
    ).hexdigest()


def _webhook(texto: str, message_id: str, wa_id: str = "573001112233"):
    return {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "contacts": [{"wa_id": wa_id, "profile": {"name": "Laura Gómez"}}],
                            "messages": [
                                {
                                    "id": message_id,
                                    "from": wa_id,
                                    "type": "text",
                                    "text": {"body": texto},
                                }
                            ],
                        }
                    }
                ]
            }
        ]
    }


def _postear(cliente, payload, firma=None):
    crudo = json.dumps(payload).encode()
    return cliente.post(
        "/webhook",
        content=crudo,
        headers={
            "X-Hub-Signature-256": firma or _firmar(crudo),
            "Content-Type": "application/json",
        },
    )


def main_prueba() -> None:
    fallos = 0

    def comprobar(descripcion, condicion):
        nonlocal fallos
        print(f"  {'✅' if condicion else '❌'} {descripcion}")
        if not condicion:
            fallos += 1

    with TestClient(main.app) as cliente:
        print("\n1. Verificación del webhook (lo que hace Meta al configurarlo)")
        ok = cliente.get(
            "/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": config.VERIFY_TOKEN,
                "hub.challenge": "reto-123",
            },
        )
        comprobar("token correcto → devuelve el challenge", ok.text == "reto-123")
        mal = cliente.get(
            "/webhook",
            params={"hub.mode": "subscribe", "hub.verify_token": "malo", "hub.challenge": "x"},
        )
        comprobar("token incorrecto → 403", mal.status_code == 403)

        print("\n2. Seguridad: firma del webhook")
        r = _postear(cliente, _webhook("hola", "msg_x"), firma="sha256=falsa")
        comprobar("firma inválida → 403 y no se responde", r.status_code == 403)
        comprobar("no se envió nada", not ENVIADOS)

        print("\n3. Conversación normal")
        GUION.append(SimpleNamespace(
            content=[_bloque_texto("¡Hola, Laura! Soy el asistente de Sandra. ¿En qué te ayudo?")],
            stop_reason="end_turn",
        ))
        r = _postear(cliente, _webhook("Hola, quiero info", "msg_1"))
        comprobar("webhook aceptado → 200", r.status_code == 200)
        comprobar("se envió una respuesta", len(ENVIADOS) == 1)
        comprobar("va al número correcto", ENVIADOS[0][0] == "573001112233")

        print("\n4. Mensaje duplicado (Meta reintenta)")
        r = _postear(cliente, _webhook("Hola, quiero info", "msg_1"))
        comprobar("no se responde dos veces", len(ENVIADOS) == 1)

        print("\n5. Captura de lead con herramienta")
        GUION.append(SimpleNamespace(
            content=[_bloque_herramienta("registrar_lead", {
                "nombre": "Laura Gómez",
                "empresa": "TechCorp",
                "cargo": "Directora Comercial",
                "necesidad": "Su equipo no genera reuniones desde LinkedIn",
                "urgencia": "alta",
                "temperatura": "caliente",
                "notas": "Equipo de 12 vendedores",
            })],
            stop_reason="tool_use",
        ))
        GUION.append(SimpleNamespace(
            content=[_bloque_texto("Entendido, Laura. ¿Cuántas reuniones al mes buscan?")],
            stop_reason="end_turn",
        ))
        _postear(cliente, _webhook("Soy directora comercial en TechCorp, 12 vendedores", "msg_2"))
        leads = cliente.get("/leads", headers={"Authorization": "Bearer admin-de-prueba"}).json()["leads"]
        comprobar("el lead quedó guardado", len(leads) == 1)
        comprobar("con la temperatura correcta", leads and leads[0]["temperatura"] == "caliente")
        comprobar("y el agente siguió conversando", len(ENVIADOS) == 2)

        print("\n6. Historial: Claude recibe los turnos anteriores")
        capturado = {}

        async def _espia(**kwargs):
            capturado["mensajes"] = kwargs["messages"]
            return SimpleNamespace(content=[_bloque_texto("Perfecto.")], stop_reason="end_turn")

        agent._cliente.messages.create = _espia
        _postear(cliente, _webhook("Unas 20", "msg_3"))
        comprobar("se envían los turnos previos", len(capturado["mensajes"]) == 5)
        agent._cliente.messages.create = _claude_falso

        print("\n7. Escalamiento a humano")
        GUION.append(SimpleNamespace(
            content=[_bloque_herramienta("escalar_a_humano", {
                "motivo": "Pide hablar con Sandra",
                "resumen": "Directora comercial, 12 vendedores, quiere avanzar ya.",
            }, id_="tu_2")],
            stop_reason="tool_use",
        ))
        GUION.append(SimpleNamespace(
            content=[_bloque_texto("Le paso tu caso a Sandra, ella te escribe personalmente.")],
            stop_reason="end_turn",
        ))
        _postear(cliente, _webhook("Quiero hablar con Sandra directamente", "msg_4"))
        enviados_tras_escalar = len(ENVIADOS)
        comprobar("avisa que Sandra responde", enviados_tras_escalar == 4)

        print("\n8. Con el chat escalado, el bot se calla")
        _postear(cliente, _webhook("¿Sigues ahí?", "msg_5"))
        comprobar("no responde estando en pausa", len(ENVIADOS) == enviados_tras_escalar)

        print("\n9. Reanudar el chat")
        r = cliente.post("/reanudar/573001112233", headers={"Authorization": "Bearer admin-de-prueba"})
        comprobar("endpoint /reanudar funciona", r.status_code == 200)
        GUION.append(SimpleNamespace(content=[_bloque_texto("Aquí sigo.")], stop_reason="end_turn"))
        _postear(cliente, _webhook("¿Hola?", "msg_6"))
        comprobar("el agente vuelve a responder", len(ENVIADOS) == enviados_tras_escalar + 1)

        print("\n10. Mensaje de audio (todavía no soportado)")
        payload = _webhook("", "msg_7")
        payload["entry"][0]["changes"][0]["value"]["messages"][0] = {
            "id": "msg_7", "from": "573001112233", "type": "audio", "audio": {"id": "a1"},
        }
        _postear(cliente, payload)
        comprobar("responde pidiendo texto", "solo leo texto" in ENVIADOS[-1][1])

        print("\n11. /leads sin autorización")
        comprobar("sin token → 401", cliente.get("/leads").status_code == 401)

    print("\n" + "─" * 60)
    if fallos:
        print(f"❌ {fallos} comprobación(es) fallaron.")
        raise SystemExit(1)
    print("✅ Todo funciona. La cañería está lista para conectar las cuentas reales.")


if __name__ == "__main__":
    main_prueba()
