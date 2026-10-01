# -*- coding: utf-8 -*-
"""Recupera del transcript de la sesión los informes de asistencia que el
conector de Dropbox devolvió, y los deja en datos/asistencia/ como JSON.

El contenido ya pasó por el contexto; esto solo lo baja a disco sin volver
a pedirlo ni a escribirlo a mano.
"""
import json, os, glob, re

AQUI = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(AQUI, 'datos', 'asistencia')
TRANS = '/root/.claude/projects/-home-user-Play-Sales-Revolution-AI/*.jsonl'


def recorre(x):
    """Devuelve todas las cadenas que haya dentro de la estructura."""
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from recorre(v)
    elif isinstance(x, list):
        for v in x:
            yield from recorre(v)


def main():
    os.makedirs(DEST, exist_ok=True)
    vistos = {}
    for ruta in glob.glob(TRANS):
        for linea in open(ruta, encoding='utf-8', errors='ignore'):
            try:
                obj = json.loads(linea)
            except Exception:
                continue
            for s in recorre(obj):
                if 'Informe de asistencia' not in s or '1. Resumen' not in s:
                    continue
                # la carga útil del conector es un JSON con id/metadata/text
                for m in re.finditer(r'\{"id":"id:[^"]+","metadata":', s):
                    try:
                        d, _ = json.JSONDecoder().raw_decode(s[m.start():])
                    except Exception:
                        continue
                    if 'text' in d and '1. Resumen' in d.get('text', ''):
                        vistos[d['id']] = d
    for fid, d in vistos.items():
        nombre = fid.replace('id:', '').replace('/', '_') + '.json'
        with open(os.path.join(DEST, nombre), 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False)
    print('informes en disco:', len(vistos))
    return vistos


if __name__ == '__main__':
    main()
