"""Isaía · respuesta automática a quien comenta una palabra clave.

Aprobado por Sandra el 4 nov 2026: texto del mensaje directo, respuesta pública y revisión cada hora.
Regla de Sandra: cada llamado a comentar una palabra lleva su guía y su entrada en PALABRAS.
El token de Meta lo inyecta el entorno como secreto de red: este script nunca lo lee ni lo imprime.

Uso:
  python3 responder_comentarios.py            # envía
  python3 responder_comentarios.py --prueba   # solo muestra a quién le respondería
"""
import json, re, subprocess, sys, datetime as dt

API = "https://graph.facebook.com/v21.0"
IG = "17841448964093245"
YO = "sandracurvelo_iam"
# Palabra clave (expresión regular) -> mensaje directo con su guía. La primera que coincida gana.
PALABRAS = [
    (re.compile(r"\bactiva\b", re.I),
     "¡Hola! Gracias por comentar 🙌 Ya te paso tu guía con los 5 ajustes para que Claude trabaje contigo y no sea solo un buscador. "
     "No es un PDF: es una página interactiva con los prompts que copias con un clic 👉 "
     "https://claude.ai/artifact/JvSbAozt2FJ1DfnvGwagfM Cuéntame cuál activaste primero. Sandra"),
    (re.compile(r"\bconecta\b", re.I),
     "¡Hola! Gracias por comentar 🙌 Ya te paso tu tablero para conectar tu agente a tu calendario, tu Drive y tu CRM. "
     "No es un PDF: es una página interactiva con los 3 pasos y 4 misiones que copias con un clic 👉 "
     "https://claude.ai/artifact/BJAFDW3oL2YmBUvWvpKcy2 Cuéntame qué conectaste primero. Sandra"),
    (re.compile(r"\bagentes?\b", re.I),
     "¡Hola! Gracias por comentar 🙌 Ya te paso tu tablero para crear tu primer agente con IA agéntica. No es un PDF: "
     "es una página interactiva con la misión CREA, los 3 pasos y 5 misiones de agentes que copias con un clic 👉 "
     "https://claude.ai/artifact/XjUgewEynFqSVRr8Pz6mcp Cuéntame cuál armaste primero. Sandra"),
    (re.compile(r"\bventas?\b", re.I),
     "¡Hola! Gracias por comentar 🙌 Ya te paso tu tablero para crear tu agente comercial con Claude. No es un PDF: "
     "es una página interactiva con la misión CREA y 6 tareas de IA agéntica que copias con un clic 👉 "
     "https://claude.ai/artifact/2C6WmB3NDLUKMLLr72xGnB Cuéntame cuál te funcionó. Sandra"),
    (re.compile(r"\b(claude|linkedin)\b", re.I),
     "¡Hola! Gracias por comentar 🙌 Ya te paso tu tablero con los prompts que uso con Claude para mi LinkedIn. "
     "No es un PDF: es una página interactiva donde copias cada prompt con un clic 👉 "
     "https://claude.ai/artifact/XMtd5GiGfXSuGePjeaZRmX Cuéntame cuál te funcionó. Sandra"),
]
def mensaje_para(texto):
    for rx, dm in PALABRAS:
        if rx.search(texto or ""):
            return dm
    return None
PUBLICA = "¡Ya te paso tu tablero por mensaje directo! 📩"
PRUEBA = "--prueba" in sys.argv


def api(method, path, data=None):
    cmd = ["curl", "-sS", "-g", "-X", method, f"{API}/{path}"]
    for k, v in (data or {}).items():
        cmd += ["--data-urlencode", f"{k}={v}"]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    try:
        return json.loads(out)
    except ValueError:
        return {"error": {"message": out[:200]}}


def main():
    ahora = dt.datetime.now(dt.timezone.utc)
    campos = "media.limit(15){id,permalink,timestamp,comments.limit(100){id,text,username,timestamp,replies{username}}}"
    d = api("GET", f"{IG}?fields={campos}")
    if "error" in d:
        print(json.dumps({"estado": "error_lectura", "detalle": d["error"].get("message")}, ensure_ascii=False))
        return
    enviados, fallos, pendientes = [], [], []
    for m in d.get("media", {}).get("data", []):
        for c in m.get("comments", {}).get("data", []):
            DM = mensaje_para(c.get("text", ""))
            if c.get("username") == YO or not DM:
                continue
            if any(r.get("username") == YO for r in c.get("replies", {}).get("data", [])):
                continue  # ya se le respondió
            edad = ahora - dt.datetime.strptime(c["timestamp"], "%Y-%m-%dT%H:%M:%S%z")
            if edad.days >= 7:
                continue  # Instagram solo deja respuesta privada en los días siguientes al comentario
            item = {"usuario": c.get("username"), "comentario": c.get("text"), "publicacion": m.get("permalink")}
            if PRUEBA:
                pendientes.append(item)
                continue
            r = api("POST", f"{IG}/messages", {"recipient": json.dumps({"comment_id": c["id"]}),
                                                "message": json.dumps({"text": DM}, ensure_ascii=False)})
            if "error" in r:
                item["error"] = r["error"].get("message")
                fallos.append(item)
                continue  # sin mensaje directo no se dice en público que se envió
            p = api("POST", f"{c['id']}/replies", {"message": PUBLICA})
            item["respuesta_publica"] = "ok" if "id" in p else p.get("error", {}).get("message")
            enviados.append(item)
    print(json.dumps({"estado": "ok", "prueba": PRUEBA, "enviados": enviados, "fallos": fallos,
                      "pendientes": pendientes}, ensure_ascii=False, indent=1))


main()
