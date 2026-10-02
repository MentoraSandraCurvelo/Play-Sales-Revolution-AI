# -*- coding: utf-8 -*-
"""Baja a `plantilla_v2/vendor/` las librer\u00edas que la plantilla pide a un CDN.

Solo hace falta para armar la versi\u00f3n sin internet (`empaquetar.py --sin-internet`).
Se bajan del registro de npm, que es la misma fuente que publica esos CDN.
"""
import os, shutil, subprocess, sys, tarfile, tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(AQUI, 'plantilla_v2', 'vendor')

# destino local -> (paquete con versi\u00f3n, ruta dentro del paquete)
LIBRERIAS = {
    'react.js':     ('react@18.3.1',            'package/umd/react.production.min.js'),
    'react-dom.js': ('react-dom@18.3.1',        'package/umd/react-dom.production.min.js'),
    'babel.js':     ('@babel/standalone@7.29.0', 'package/babel.min.js'),
    'three.js':     ('three@0.160.0',           'package/build/three.min.js'),
}


def main():
    os.makedirs(VENDOR, exist_ok=True)
    tmp = tempfile.mkdtemp()
    try:
        for destino, (paquete, dentro) in LIBRERIAS.items():
            salida = subprocess.run(['npm', 'pack', paquete, '--silent'],
                                    cwd=tmp, capture_output=True, text=True)
            if salida.returncode:
                sys.exit('no se pudo bajar %s:\n%s' % (paquete, salida.stderr.strip()))
            tgz = os.path.join(tmp, salida.stdout.strip().splitlines()[-1])
            with tarfile.open(tgz) as t, open(os.path.join(VENDOR, destino), 'wb') as f:
                shutil.copyfileobj(t.extractfile(dentro), f)
            print('  %-14s %7.0f KB  <- %s' % (
                destino, os.path.getsize(os.path.join(VENDOR, destino)) / 1024, paquete))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(VENDOR)


if __name__ == '__main__':
    main()
