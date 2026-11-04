"""Isaía · respuesta automática a quien comenta CLAUDE o LINKEDIN.

Aprobado por Sandra el 4 nov 2026: texto del mensaje directo, respuesta pública y revisión cada hora.
El token de Meta lo inyecta el entorno como secreto de red: este script nunca lo lee ni lo imprime.

Uso:
  python3 responder_comentarios.py            # envía
  python3 responder_comentarios.py --prueba   # solo muestra a quién le respondería
"""
import json, re, subprocess, sys, datetime as dt

API = "https://graph.facebook.com/v21.0"
IG = "17841448964093245"
YO = "sandracurvelo_iam"
GUIA = "https://claude.ai/artifact/XMtd5GiGfXSuGePjeaZRmX"
CLAVE = re.compile(r"\b(claude|linkedin)\b", re.I)
DM = ("¡Hola! Gracias por comentar 🙌 Aquí tienes la guía con los prompts que uso con Claude "
      f"para mi LinkedIn: {GUIA} Cópialos y cuéntame cuál te funcionó. Sandra")
PUBLICA = "¡Te lo envié por mensaje directo! 📩"
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
            if c.get("username") == YO or not CLAVE.search(c.get("text", "")):
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
