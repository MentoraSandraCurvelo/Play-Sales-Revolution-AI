#!/usr/bin/env python3
"""Web IA · auditor de iamlatam.co (IAM™ · Sandra Curvelo).

Revisa una URL en vivo o un index.html local y entrega un informe en Markdown
con cuatro frentes: mensaje, conversión, SEO y salud técnica.

Uso:
    python3 scripts/web_ia_auditar.py https://iamlatam.co/
    python3 scripts/web_ia_auditar.py web/index.html
    python3 scripts/web_ia_auditar.py web/index.html --enlaces   # además prueba enlaces externos

Solo usa la librería estándar. No modifica nada: solo lee y reporta.
Cada cifra del informe sale de una medición directa sobre el HTML analizado.
"""
import os
import re
import sys
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

UA = "Mozilla/5.0 (compatible; WebIA-Auditor/1.0)"
# Palabras que deben aparecer en el primer pantallazo para que el mensaje sea IA empresarial medida.
CLAVES_HERO = ["ia", "inteligencia artificial", "mid", "productividad", "iae"]


class Pagina(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.metas = {}
        self.links_rel = {}
        self.lang = ""
        self.ids = set()
        self.anclas = []          # (href, texto)
        self.imgs = []            # (src, alt, loading)
        self.h = {"h1": [], "h2": []}
        self.iframes = []
        self.videos = []
        self.jsonld = 0
        self._pila = []
        self._txt = []
        self._a = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "html":
            self.lang = a.get("lang", "")
        elif tag == "meta":
            k = a.get("name") or a.get("property")
            if k:
                self.metas[k.lower()] = a.get("content", "")
        elif tag == "link":
            self.links_rel.setdefault((a.get("rel") or "").lower(), a.get("href", ""))
        elif tag == "img":
            self.imgs.append((a.get("src", ""), a.get("alt"), a.get("loading", "")))
        elif tag == "iframe":
            self.iframes.append(a.get("src", ""))
        elif tag in ("video", "source") and a.get("src"):
            self.videos.append(a["src"])
        elif tag == "script" and a.get("type") == "application/ld+json":
            self.jsonld += 1
        elif tag == "a":
            self._a = [a.get("href", ""), ""]
        if tag == "br" and self._pila:
            self._txt.append(" ")
        if tag in ("title", "h1", "h2"):
            self._pila.append(tag)
            self._txt = []
        if tag == "div" and "calendly-inline-widget" in a.get("class", ""):
            self.iframes.append(a.get("data-url", "calendly"))

    def handle_endtag(self, tag):
        if self._pila and self._pila[-1] == tag:
            self._pila.pop()
            texto = " ".join("".join(self._txt).split())
            if tag == "title":
                self.title = texto
            else:
                self.h[tag].append(texto)
        if tag == "a" and self._a:
            self.anclas.append((self._a[0], " ".join(self._a[1].split())))
            self._a = None

    def handle_data(self, data):
        if self._pila:
            self._txt.append(data)
        if self._a is not None:
            self._a[1] += data


def leer(origen):
    if origen.startswith("http"):
        req = urllib.request.Request(origen, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.read(), origen, r.status
    with open(origen, "rb") as f:
        return f.read(), None, None


def estado(url, metodo="HEAD"):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA}, method=metodo)
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status
    except urllib.error.HTTPError as e:
        if metodo == "HEAD" and e.code in (403, 405, 999):
            return estado(url, "GET") if e.code == 405 else e.code
        return e.code
    except Exception as e:  # red bloqueada, DNS, tiempo agotado
        return "sin respuesta (%s)" % type(e).__name__


def auditar(origen, probar_enlaces=False):
    crudo, base, _ = leer(origen)
    html = crudo.decode("utf-8", "replace")
    p = Pagina()
    p.feed(html)
    carpeta = None if base else os.path.dirname(os.path.abspath(origen))
    hallazgos = []   # (nivel, frente, texto)

    def ok(frente, t): hallazgos.append(("OK", frente, t))
    def alerta(frente, t): hallazgos.append(("ALERTA", frente, t))
    def critico(frente, t): hallazgos.append(("CRÍTICO", frente, t))

    def existe(ruta):
        """True/False para un recurso propio del sitio; None si no se puede comprobar."""
        if base:
            return estado(urljoin(base, ruta)) == 200
        local = os.path.join(carpeta, ruta.lstrip("/").split("?")[0])
        if os.path.isdir(local):
            local = os.path.join(local, "index.html")
        return os.path.exists(local)

    # ---------- MENSAJE ----------
    h1 = p.h["h1"]
    if len(h1) != 1:
        critico("Mensaje", "La página tiene %d titulares H1; debe tener exactamente 1." % len(h1))
    hero = (h1[0] if h1 else "").lower()
    presentes = [c for c in CLAVES_HERO if re.search(r"\b%s" % re.escape(c), hero)]
    if h1:
        if "ia" in presentes or "inteligencia artificial" in presentes:
            ok("Mensaje", "El titular principal habla de IA: «%s»." % h1[0])
        else:
            critico("Mensaje", "El titular principal no menciona la IA: «%s»." % h1[0])
        if not any(c in presentes for c in ("mid", "productividad", "iae")):
            alerta("Mensaje", "El titular no habla de medir ni de productividad.")
    if "iae" in p.ids:
        ok("Mensaje", "Existe la sección del IAE™ (ancla #iae).")
    else:
        critico("Mensaje", "No existe una sección propia del IAE™ (ancla #iae).")
    tableros = [s for s, _, _ in p.imgs if "tablero" in s.lower()]
    if "iae-tablero" in p.ids:
        tableros.append("#iae-tablero")
        ok("Mensaje", "El Tablero IAE™ está en la página y con movimiento (#iae-tablero).")
    elif tableros:
        ok("Mensaje", "Hay %d pantallazos de tableros en la página, pero estáticos." % len(tableros))
    else:
        alerta("Mensaje", "No hay tableros de medición en la página.")
    menciones = len(re.findall(r"IAE™", html))
    (ok if menciones >= 5 else alerta)("Mensaje", "El IAE™ se menciona %d veces en toda la página." % menciones)
    if re.search(r"datos simulados|demostraci[oó]n", html, re.I) or not tableros:
        if tableros:
            ok("Mensaje", "El tablero está marcado como demostración con datos simulados.")
    else:
        critico("Mensaje", "Hay tableros sin aclarar si los datos son reales o simulados.")

    # ---------- CONVERSIÓN ----------
    internos = [(h, t) for h, t in p.anclas if h.startswith("#")]
    a_contacto = [t for h, t in internos if h == "#contacto"]
    (ok if len(a_contacto) >= 3 else alerta)("Conversión", "%d botones o enlaces llevan a agendar (#contacto)." % len(a_contacto))
    if any("calendly" in (s or "") for s in p.iframes) or "calendly" in html:
        ok("Conversión", "Calendly está integrado en la página.")
    else:
        critico("Conversión", "No se encontró Calendly en la página.")
    rotas = sorted({h for h, _ in internos if len(h) > 1 and h[1:] not in p.ids})
    if rotas:
        critico("Conversión", "Anclas internas rotas (el botón no lleva a ningún lado): %s." % ", ".join(rotas))
    else:
        ok("Conversión", "Todas las anclas internas llevan a una sección que existe.")
    vacios = [t or "(sin texto)" for h, t in p.anclas if h == "#" and t]
    if vacios:
        alerta("Conversión", "%d enlaces sin destino (href=\"#\"): %s." % (len(vacios), "; ".join(sorted(set(vacios)))))
    if "wa.me" in html:
        ok("Conversión", "Hay botón directo de WhatsApp.")

    # ---------- SEO ----------
    lt = len(p.title)
    (ok if 30 <= lt <= 65 else alerta)("SEO", "Título de %d caracteres (ideal entre 30 y 65): «%s»." % (lt, p.title))
    d = p.metas.get("description", "")
    (ok if 110 <= len(d) <= 165 else alerta)("SEO", "Meta descripción de %d caracteres (ideal entre 110 y 165)." % len(d))
    if d and not re.search(r"\bIA\b|inteligencia artificial", d):
        alerta("SEO", "La meta descripción no menciona la IA.")
    (ok if p.lang.startswith("es") else alerta)("SEO", "Idioma declarado: «%s»." % p.lang)
    (ok if p.links_rel.get("canonical") else alerta)("SEO", "Etiqueta canonical: %s." % (p.links_rel.get("canonical") or "no existe"))
    (ok if p.jsonld else alerta)("SEO", "Datos estructurados (JSON-LD): %d bloques." % p.jsonld)
    og = p.metas.get("og:image", "")
    if not og:
        critico("SEO", "No hay imagen para compartir en LinkedIn y WhatsApp (og:image).")
    else:
        ruta = urlparse(og).path
        e = existe(ruta)
        (ok if e else critico)("SEO", "Imagen para compartir en LinkedIn y WhatsApp (%s): %s." % (ruta, "existe" if e else "NO existe, el enlace se comparte sin imagen"))
    for ruta in ("/robots.txt", "/sitemap.xml", "/favicon.ico"):
        e = existe(ruta)
        (ok if e else alerta)("SEO", "%s: %s." % (ruta, "existe" if e else "no existe"))
    sin_alt = [s for s, alt, _ in p.imgs if alt is None or (alt == "" and "logo" not in s and "ico" not in s and not s.startswith("data:image/png"))]
    (ok if not sin_alt else alerta)("SEO", "%d de %d imágenes sin texto alternativo." % (len(sin_alt), len(p.imgs)))

    # ---------- SALUD TÉCNICA ----------
    peso = len(crudo)
    b64 = sum(len(m) for m in re.findall(r"base64,[A-Za-z0-9+/=]+", html))
    nivel = ok if peso < 500_000 else (alerta if peso < 1_500_000 else critico)
    nivel("Técnica", "El HTML pesa %.2f MB; %.0f%% son imágenes incrustadas en base64 (%.2f MB)." % (peso / 1e6, 100 * b64 / peso, b64 / 1e6))
    dup = {}
    for m in re.findall(r"base64,([A-Za-z0-9+/=]{2000,})", html):
        dup[hash(m)] = dup.get(hash(m), [0, len(m)])
        dup[hash(m)][0] += 1
    rep = sum((n - 1) * tam for n, tam in dup.values() if n > 1)
    if rep:
        alerta("Técnica", "Hay imágenes incrustadas repetidas: %.2f MB de peso desperdiciado." % (rep / 1e6))
    perezosas = sum(1 for _, _, l in p.imgs if l == "lazy")
    (ok if perezosas >= len(p.imgs) * 0.5 else alerta)("Técnica", "%d de %d imágenes cargan de forma diferida (loading=lazy)." % (perezosas, len(p.imgs)))
    for src in sorted({s for s, _, _ in p.imgs if s and not s.startswith(("data:", "http"))} | {v for v in p.videos if not v.startswith(("data:", "http"))}):
        if existe(src) is False:
            (critico if base else alerta)("Técnica", "Recurso propio no encontrado: %s%s." % (src, "" if base else " (no está en la carpeta local; verificar que siga en Netlify)"))
    if "viewport" not in p.metas:
        critico("Técnica", "Falta la etiqueta viewport: la página no se adapta al celular.")

    if probar_enlaces:
        externos = sorted({h for h, _ in p.anclas if h.startswith("http")})
        for u in externos:
            s = estado(u)
            if s == 200:
                ok("Enlaces", "%s responde 200." % u)
            elif s in (403, 999) or isinstance(s, str):
                alerta("Enlaces", "%s: %s. No concluyente, estas redes suelen bloquear robots; verificar a mano." % (u, s))
            else:
                critico("Enlaces", "%s responde %s." % (u, s))

    return hallazgos


def informe(origen, hallazgos):
    n = {k: sum(1 for h in hallazgos if h[0] == k) for k in ("OK", "ALERTA", "CRÍTICO")}
    total = len(hallazgos)
    puntaje = round(100 * (n["OK"] + 0.5 * n["ALERTA"]) / total) if total else 0
    out = ["# Web IA · Auditoría de %s" % origen, "",
           "**Puntaje: %d/100** · %d revisiones: %d bien, %d alertas, %d críticos." % (puntaje, total, n["OK"], n["ALERTA"], n["CRÍTICO"]),
           "", "_Cómo se calcula: cada revisión aprobada vale 1 punto, cada alerta 0,5 y cada crítico 0; se divide por el total de revisiones._", ""]
    for frente in ("Mensaje", "Conversión", "SEO", "Técnica", "Enlaces"):
        filas = [h for h in hallazgos if h[1] == frente]
        if not filas:
            continue
        out.append("## %s" % frente)
        orden = {"CRÍTICO": 0, "ALERTA": 1, "OK": 2}
        for nivel, _, t in sorted(filas, key=lambda h: orden[h[0]]):
            out.append("- **%s** · %s" % (nivel, t))
        out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    print(informe(args[0], auditar(args[0], "--enlaces" in sys.argv)))
