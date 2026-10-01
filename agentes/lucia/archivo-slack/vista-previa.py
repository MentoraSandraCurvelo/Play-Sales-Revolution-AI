# -*- coding: utf-8 -*-
"""Envuelve app/archivo.html en el mismo esqueleto que añade la publicación,
para poder verlo en local tal como se verá publicado."""
import os, sys, shutil
AQUI = os.path.dirname(os.path.abspath(__file__))
DEST = sys.argv[1] if len(sys.argv) > 1 else '/tmp/claude-0/vista'
EXTRA = sys.argv[2] if len(sys.argv) > 2 else ''
os.makedirs(DEST, exist_ok=True)
frag = open(os.path.join(AQUI, 'app', 'archivo.html'), encoding='utf-8').read()
html = ('<!doctype html><html lang="es"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);'
        'padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;background:#fafafa;'
        'font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>'
        '</head><body>' + frag + EXTRA + '</body></html>')
open(os.path.join(DEST, 'index.html'), 'w', encoding='utf-8').write(html)
shutil.copy(os.path.join(AQUI, 'app', 'datos.js'), os.path.join(DEST, 'datos.js'))
print(os.path.join(DEST, 'index.html'))
