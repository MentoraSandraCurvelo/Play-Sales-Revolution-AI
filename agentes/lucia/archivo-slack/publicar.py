# -*- coding: utf-8 -*-
"""Prepara la app para publicarla como página web.

Lo publicado no es un documento completo sino un **fragmento**: el esqueleto
(`<!doctype>`, `<head>`, `<body>`) lo pone la plataforma al publicar. Así que
aquí se quita ese envoltorio y se dejan, en orden, los tres scripts locales y
el componente.

Las librerías salen del CDN —en la web sí se alcanzan—, de modo que el
fragmento pesa 2 MB y no 6. Los PDF viajan aparte, en `actas/`, que es a donde
ya apuntan los enlaces.
"""
import os, re, shutil, sys
import empaquetar

AQUI = os.path.dirname(os.path.abspath(__file__))
PLANTILLA = os.path.join(AQUI, 'plantilla_v2')
DEST = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, 'publicado')

SCRIPTS = (('<script src="./support.js"></script>', 'support.js'),
           ('<script src="lib/iam.js"></script>', os.path.join('lib', 'iam.js')),
           ('<script src="data/archivo.js"></script>', os.path.join('data', 'archivo.js')))


def en_linea(js):
    return js.replace('</script', '<\\/script').replace('<!--', '<\\!--')


def main():
    os.makedirs(DEST, exist_ok=True)
    html = open(os.path.join(PLANTILLA, 'IAM Archivo.dc.html'), encoding='utf-8').read()
    html = empaquetar.sin_internet(html)
    for etiqueta, archivo in SCRIPTS:
        js = open(os.path.join(PLANTILLA, archivo), encoding='utf-8').read()
        html = html.replace(etiqueta, '<script>\n' + en_linea(js) + '\n</script>')

    # fuera el envoltorio: lo pone la plataforma
    cuerpo = re.search(r'<body[^>]*>(.*)</body>', html, re.S).group(1)
    cabeza = re.search(r'<head[^>]*>(.*)</head>', html, re.S).group(1)
    # Del <head> hay que rescatar **todos** los scripts y en su orden: ahí viven
    # support.js y, con las librerías dentro, también React, Babel y three.js.
    # Quedándose solo con el primero, el fragmento salía a 2,8 MB en vez de 6 y
    # no arrancaba.
    guiones = re.findall(r'<script(?:\s[^>]*)?>.*?</script>', cabeza, re.S)
    frag = '\n'.join(guiones) + '\n' + cuerpo.strip() + '\n'

    ruta = os.path.join(DEST, 'iam-hello.html')
    open(ruta, 'w', encoding='utf-8').write(frag)

    actas = os.path.join(DEST, 'actas')
    os.makedirs(actas, exist_ok=True)
    origen = os.path.join(os.path.dirname(AQUI), 'salida')
    n = 0
    for f in sorted(os.listdir(origen)):
        if f.endswith('.pdf'):
            shutil.copy(os.path.join(origen, f), os.path.join(actas, f)); n += 1
    print('%s  (%.1f MB)\n  %d actas en actas/' % (ruta, os.path.getsize(ruta) / 1048576, n))


if __name__ == '__main__':
    main()
