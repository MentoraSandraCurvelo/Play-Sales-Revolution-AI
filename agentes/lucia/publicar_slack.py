#!/usr/bin/env python3
"""
Publica un acta en Slack — con el PDF y el CSV como archivos adjuntos de verdad.

Es la pieza que la conexión de Slack de Claude no puede hacer: subir archivos.
Habla directo con la API de Slack usando un token propio del workspace.

Uso:
    export SLACK_BOT_TOKEN="xoxb-..."       # nunca en el código, nunca en el chat
    python3 publicar_slack.py \
        --canal C0BPDN9PKPH \
        --mensaje mensaje.txt \
        --archivo salida/ACTA_Sesion2_Contabilidad_26agosto2026.pdf \
        --archivo "…/Informe de asistencia 8-26-26.csv"

    # Para revisar sin publicar nada:
    python3 publicar_slack.py ... --simular

Requisitos del entorno:
  1. Una app de Slack en el workspace con los permisos files:write y chat:write.
  2. El bot invitado al canal donde se va a publicar.
  3. Salida de red hacia slack.com (ver GUIA-APP-SLACK.md).

Solo usa la biblioteca estándar: no hay nada que instalar.
"""

import argparse
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://slack.com/api/"


def token():
    t = os.environ.get("SLACK_BOT_TOKEN", "").strip()
    if not t:
        salir("Falta SLACK_BOT_TOKEN en el entorno. No lo escribas en el código ni en el chat.")
    if not t.startswith("xoxb-"):
        salir("El token no parece de bot: debe empezar por 'xoxb-'.")
    return t


def salir(mensaje):
    print(f"  ✗ {mensaje}", file=sys.stderr)
    sys.exit(1)


def llamar(metodo, datos, autorizar=True):
    """Llama a la API de Slack y devuelve el JSON, o corta con un mensaje claro."""
    cuerpo = urllib.parse.urlencode(datos).encode()
    pet = urllib.request.Request(API + metodo, data=cuerpo)
    pet.add_header("Content-Type", "application/x-www-form-urlencoded; charset=utf-8")
    if autorizar:
        pet.add_header("Authorization", f"Bearer {token()}")
    try:
        with urllib.request.urlopen(pet, timeout=60) as r:
            resp = json.loads(r.read())
    except urllib.error.URLError as e:
        salir(f"No se pudo llegar a slack.com ({metodo}): {e.reason}.\n"
              f"    Si dice 403 o 'connect rejected', la red del entorno bloquea Slack.\n"
              f"    Revisa GUIA-APP-SLACK.md, sección «Abrir la red».")
    if not resp.get("ok"):
        salir(f"Slack rechazó {metodo}: {resp.get('error')}\n"
              f"    {PISTAS.get(resp.get('error'), '')}")
    return resp


PISTAS = {
    "not_in_channel": "El bot no está en el canal. Invítalo con /invite @nombre-del-bot.",
    "missing_scope": "Al token le falta un permiso. Necesita files:write y chat:write.",
    "invalid_auth": "El token no es válido o fue revocado. Genera uno nuevo.",
    "channel_not_found": "Revisa el ID del canal.",
}


def subir(ruta, canal, comentario=None):
    """Sube un archivo en los tres pasos que pide la API de Slack."""
    archivo = Path(ruta)
    if not archivo.is_file():
        salir(f"No existe el archivo: {ruta}")
    datos = archivo.read_bytes()

    # 1 · Pedir la URL de subida
    paso1 = llamar("files.getUploadURLExternal",
                   {"filename": archivo.name, "length": len(datos)})

    # 2 · Enviar el contenido a esa URL
    tipo = mimetypes.guess_type(archivo.name)[0] or "application/octet-stream"
    pet = urllib.request.Request(paso1["upload_url"], data=datos, method="POST")
    pet.add_header("Content-Type", tipo)
    try:
        urllib.request.urlopen(pet, timeout=120).read()
    except urllib.error.URLError as e:
        salir(f"Falló la subida de {archivo.name}: {e.reason}")

    # 3 · Confirmar y compartir en el canal
    entrada = {"id": paso1["file_id"], "title": archivo.stem}
    peticion = {"files": json.dumps([entrada]), "channel_id": canal}
    if comentario:
        peticion["initial_comment"] = comentario
    llamar("files.completeUploadExternal", peticion)
    print(f"  ✓ {archivo.name}  ({len(datos):,} bytes)")


def main():
    ap = argparse.ArgumentParser(description="Publica un acta con sus archivos en Slack.")
    ap.add_argument("--canal", required=True, help="ID del canal, p. ej. C0BPDN9PKPH")
    ap.add_argument("--mensaje", required=True, help="Archivo de texto con el mensaje")
    ap.add_argument("--archivo", action="append", default=[],
                    help="Archivo a adjuntar. Repetir para varios.")
    ap.add_argument("--simular", action="store_true",
                    help="Muestra lo que haría, sin publicar nada")
    args = ap.parse_args()

    texto = Path(args.mensaje).read_text(encoding="utf-8")

    if args.simular:
        print(f"\n  SIMULACIÓN — no se publica nada\n")
        print(f"  Canal:     {args.canal}")
        print(f"  Mensaje:   {len(texto)} caracteres")
        for a in args.archivo:
            r = Path(a)
            estado = f"{r.stat().st_size:,} bytes" if r.is_file() else "NO EXISTE"
            print(f"  Adjunto:   {r.name}  ({estado})")
        print(f"\n  ── Mensaje ──\n{texto}\n")
        return

    print(f"\n  Publicando en {args.canal}…")
    resp = llamar("chat.postMessage", {"channel": args.canal, "text": texto})
    print(f"  ✓ Mensaje publicado")

    # Los archivos van dentro del hilo, para no partir el canal en tres mensajes
    hilo = resp["ts"]
    for a in args.archivo:
        subir(a, args.canal, None)

    print(f"\n  Listo. Anota la publicación en registro-slack.md.\n")


if __name__ == "__main__":
    main()
