#!/usr/bin/env python3
"""Condensa una transcripción de Teams para poder leerla completa.

Un VTT de una hora trae entre 130 y 190 KB: miles de cues de tres segundos, cada
uno con su marca de tiempo y su etiqueta de hablante repetida. El contenido real
—quién dijo qué— cabe en una décima parte.

Lo que hace: junta los cues seguidos del mismo hablante en una sola intervención,
deja una marca de tiempo por intervención y descarta lo que no aporta. No resume
ni interpreta: el texto sale entero, solo deja de estar troceado.

Entrada: un .vtt, o el JSON que devuelve el conector de Dropbox (campo "text").
"""
import html as _html
import io, json, re, sys

def texto_de(ruta):
    crudo = io.open(ruta, encoding="utf-8", errors="replace").read()
    if crudo.lstrip().startswith("{"):
        try:
            return json.loads(crudo)["text"]
        except Exception:
            pass
    return crudo

def mmss(marca):
    """00:12:34.560 --> 12:34 · los milisegundos no le dicen nada a nadie."""
    m = re.match(r"(\d+):(\d+):(\d+)", marca)
    if not m:
        return marca
    h, mi, s = (int(x) for x in m.groups())
    return f"{h*60+mi}:{s:02d}"

def condensar(crudo):
    lineas = crudo.replace("\r\n", "\n").split("\n")
    intervenciones = []   # [hablante, marca, [frases]]
    marca_actual = None

    for linea in lineas:
        linea = linea.strip()
        if not linea or linea == "WEBVTT" or re.fullmatch(r"[0-9a-f\-/]{6,}", linea):
            continue
        if "-->" in linea:
            marca_actual = mmss(linea.split("-->")[0].strip())
            continue
        m = re.match(r"<v ([^>]+)>(.*)$", linea)
        if m:
            # Teams escapa los acentos del nombre: Mar&#237;a Elvira.
            hablante = _html.unescape(m.group(1)).strip()
            frase = m.group(2)
        else:
            # Teams parte la frase en dos líneas: la segunda cierra con </v> y
            # no repite el hablante. Es continuación de quien venía hablando.
            hablante, frase = None, linea
        frase = _html.unescape(frase.replace("</v>", "")).strip()
        if not frase:
            continue
        if intervenciones and (hablante is None or hablante == intervenciones[-1][0]):
            if frase not in intervenciones[-1][2][-1:]:
                intervenciones[-1][2].append(frase)
        elif hablante is not None:
            intervenciones.append([hablante, marca_actual, [frase]])

    salida = []
    for hablante, marca, frases in intervenciones:
        cuerpo = " ".join(frases)
        quien = hablante or "—"
        salida.append(f"[{marca}] {quien}: {cuerpo}")
    return "\n".join(salida)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("uso: condensar_vtt.py <entrada.vtt|entrada.json> <salida.txt>")
    crudo = texto_de(sys.argv[1])
    limpio = condensar(crudo)
    io.open(sys.argv[2], "w", encoding="utf-8").write(limpio)
    print(f"{len(crudo):,} caracteres → {len(limpio):,} "
          f"({100*len(limpio)//max(len(crudo),1)}% del original)")
