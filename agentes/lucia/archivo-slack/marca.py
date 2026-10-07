# -*- coding: utf-8 -*-
"""Aplica la identidad de un cliente al fragmento ya armado.

La plantilla se escribió para Comfacesar y lleva su nombre escrito a mano en
cuatro sitios. Aquí se reemplazan por los del cliente que se esté publicando,
leídos de `clientes/<slug>.json`.

**Lo que no se toca es la marca IAM.** El rojo `#C00000`, Geist y el fondo
oscuro son los mismos para todos los clientes: el cliente tiene que reconocer
que está en IAM™Hello. Lo único que cambia es el nombre y el logo.

**Un reemplazo que no encuentra su texto detiene la publicación.** Si alguien
edita la plantilla y cambia uno de estos textos, el error es preferible a
publicarle a Novasoft una app que dice Comfacesar.

    python3 marca.py novasoft     para ver qué cambiaría
"""
import json, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
CLIENTES = os.path.join(os.path.dirname(AQUI), 'clientes')

# El nombre del producto es fijo. `espacio` es otra cosa: el nombre que el
# cliente ve arriba, que en Comfacesar es su espacio de Slack («IAM™Team»).
PRODUCTO = 'IAM™Hello'

# El texto tal como está en la plantilla, y de qué campo del cliente sale.
# `veces` es cuántas veces debe aparecer: si aparecen más o menos, algo cambió.
IDENTIDAD = (
    ('Archivo · Comfacesar',        'subtitulo', 1),
    ('IAM™ Intelligence · Comfacesar', '@programa · @nombre', 1),
    ('IAM™Hello · Archivo Comfacesar', 'IAM™Hello · @subtitulo', 1),
)


class MarcaIncompleta(Exception):
    pass


def cargar(slug):
    ruta = os.path.join(CLIENTES, slug + '.json')
    if not os.path.exists(ruta):
        disponibles = sorted(f[:-5] for f in os.listdir(CLIENTES) if f.endswith('.json')
                             and f != 'registro.json')
        raise MarcaIncompleta('no hay cliente «%s». Hay: %s' % (slug, ', '.join(disponibles)))
    cfg = json.load(open(ruta, encoding='utf-8'))
    for campo in ('slug', 'nombre', 'programa', 'espacio', 'subtitulo'):
        if not cfg.get(campo):
            raise MarcaIncompleta('a %s.json le falta «%s»' % (slug, campo))
    return cfg


def _valor(plantilla, cfg):
    """`@campo · @otro` se resuelve contra el cliente."""
    if not plantilla.startswith('@') and ' @' not in plantilla:
        return cfg[plantilla]
    out = plantilla
    for campo in ('programa', 'nombre', 'espacio', 'subtitulo', 'nombre_largo'):
        out = out.replace('@' + campo, cfg.get(campo, ''))
    return out


def aplicar(frag, cfg):
    """Devuelve el fragmento con la identidad del cliente puesta."""
    cambios = []
    for viejo, plantilla, veces in IDENTIDAD:
        hay = frag.count(viejo)
        if hay != veces:
            raise MarcaIncompleta(
                '«%s» aparece %d veces en la plantilla y se esperaban %d. '
                'Alguien la editó: hay que actualizar IDENTIDAD en marca.py '
                'antes de publicar, o la app saldría con el nombre de otro cliente.'
                % (viejo, hay, veces))
        nuevo = _valor(plantilla, cfg)
        if nuevo != viejo:
            frag = frag.replace(viejo, nuevo)
            cambios.append((viejo, nuevo))
    return frag, cambios


def logo(cfg):
    """La ruta del logo si existe, o None para caer en la sigla."""
    rel = cfg.get('logo')
    if not rel:
        return None
    ruta = os.path.join(CLIENTES, rel)
    return ruta if os.path.exists(ruta) else None


def main():
    if len(sys.argv) < 2:
        print(__doc__); return 1
    cfg = cargar(sys.argv[1])
    print('%s  ·  %s' % (cfg['nombre'], cfg.get('estado', '')))
    for viejo, plantilla, _ in IDENTIDAD:
        print('  %-34s →  %s' % (viejo, _valor(plantilla, cfg)))
    l = logo(cfg)
    print('  logo: %s' % (l if l else 'no está, sale la sigla «%s»' % cfg.get('sigla', '?')))
    return 0


if __name__ == '__main__':
    sys.exit(main())
