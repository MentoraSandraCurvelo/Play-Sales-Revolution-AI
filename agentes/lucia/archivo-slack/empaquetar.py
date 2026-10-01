# -*- coding: utf-8 -*-
"""Arma un HTML único y autónomo: la app con los datos dentro.

A diferencia de lo publicado, aquí no hay archivos aparte — se abre con doble
clic y funciona sin servidor, sin internet y sin nada al lado.
"""
import os, sys, json, datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(AQUI, 'app')
DEST = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, 'entregable')

ESQUELETO = (
    '<!doctype html>\n<html lang="es">\n<head>\n'
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
    '<style>\n'
    '  :root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);\n'
    '        padding-bottom:env(safe-area-inset-bottom,0px)}\n'
    '  body{margin:0;background:#fafafa;font:14px system-ui,sans-serif}\n'
    '  img{max-width:100%}\n'
    '  [hidden]{display:none!important}\n'
    '</style>\n</head>\n<body>\n'
)


def main():
    os.makedirs(DEST, exist_ok=True)
    frag = open(os.path.join(APP, 'archivo.html'), encoding='utf-8').read()
    datos = open(os.path.join(APP, 'datos.js'), encoding='utf-8').read()

    # En un archivo suelto no hay PDFs al lado, así que se quita el campo:
    # el botón no se dibuja solo, sin tocar el código de la app.
    a = json.loads(datos[len('window.ARCHIVO='):-2])
    for c in a['canales']:
        for acta in c['actas']:
            acta.pop('pdf', None)
    datos = 'window.ARCHIVO=' + json.dumps(a, ensure_ascii=False, separators=(',', ':')) + ';'

    # el <script src="datos.js"> se reemplaza por los datos en línea
    marca = '<script src="datos.js"></script>'
    assert marca in frag, 'no encuentro la etiqueta de datos'
    frag = frag.replace(marca, '<script>\n' + datos + '</script>')

    html = ESQUELETO + frag + '\n</body>\n</html>\n'
    ruta = os.path.join(DEST, 'IAM-archivo-comfacesar.html')
    open(ruta, 'w', encoding='utf-8').write(html)
    kb = os.path.getsize(ruta) / 1024
    print('%s\n  %.1f MB · %d canales · %d mensajes · %d actas · %d grabaciones · %d personas'
          % (ruta, kb / 1024, len(a['canales']),
             sum(c['conteo'] for c in a['canales']),
             sum(len(c['actas']) for c in a['canales']),
             a['n_grabaciones'], len(a['asistencia'])))


if __name__ == '__main__':
    main()
