"""Isaía · descarga las fotos y videos de una publicación PROPIA de Instagram de Sandra.

Aprobado por Sandra el 27 nov 2026 (regla de permiso en .claude/settings.json).
Solo trabaja con la cuenta de Sandra (17841448964093245) y solo descarga desde los
servidores de Instagram (cdninstagram.com / fbcdn.net). Guarda dentro de estrategia/.
El token de Meta lo inyecta el entorno: este script nunca lo lee ni lo imprime.

Uso:
  python3 estrategia/instagram/herramientas/bajar_media_ig.py <permalink o shortcode> <carpeta destino dentro de estrategia/>
"""
import json, os, re, subprocess, sys, urllib.parse

API = "https://graph.facebook.com/v21.0"
IG = "17841448964093245"
RAIZ = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", ".."))  # estrategia/


def get(url):
    out = subprocess.run(["curl", "-sS", "-G", url, "--data-urlencode",
                          "fields=id,permalink,media_type,media_url,caption,children{media_type,media_url}",
                          "--data-urlencode", "limit=50"], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    m = re.search(r"/(?:p|reel)/([^/?#]+)", sys.argv[1])
    code = m.group(1) if m else sys.argv[1].strip("/")
    destino = os.path.realpath(sys.argv[2])
    if not destino.startswith(RAIZ + os.sep):
        sys.exit("La carpeta destino debe estar dentro de estrategia/.")
    datos = get(f"{API}/{IG}/media")
    if "error" in datos:
        sys.exit("Error de la API: " + datos["error"].get("message", ""))
    pub = next((p for p in datos.get("data", []) if f"/{code}/" in p.get("permalink", "")), None)
    if not pub:
        sys.exit("No encontré esa publicación entre las últimas 50 de la cuenta.")
    os.makedirs(destino, exist_ok=True)
    items = pub.get("children", {}).get("data") or [pub]
    for i, c in enumerate(items, 1):
        host = urllib.parse.urlparse(c["media_url"]).hostname or ""
        if not (host.endswith(".cdninstagram.com") or host.endswith(".fbcdn.net")):
            sys.exit(f"Servidor no permitido: {host}")
        ext = "mp4" if c.get("media_type") == "VIDEO" else "jpg"
        ruta = os.path.join(destino, f"slide{i}.{ext}")
        subprocess.run(["curl", "-sS", "-o", ruta, c["media_url"]], check=True)
        print(ruta)
    with open(os.path.join(destino, "caption.txt"), "w") as f:
        f.write((pub.get("caption") or "") + "\n")


if __name__ == "__main__":
    main()
