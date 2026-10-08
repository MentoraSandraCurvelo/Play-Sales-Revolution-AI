# -*- coding: utf-8 -*-
"""Arma el paquete de datos de un cliente que todavía no tiene historia.

La plantilla nació para el archivo de Comfacesar, así que espera un paquete con
asistencia, pulso, informes y grabaciones. Un cliente nuevo no tiene nada de
eso, pero **la plantilla igual lo espera**: si falta una clave, la vista se cae.

Aquí se genera ese paquete completo con todo en cero, para que el mismo molde
sirva para un espacio recién abierto. Los canales y las carpetas fijadas salen
del archivo del cliente.

    python3 construir_cliente.py novasoft
"""
import json, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
LUCIA = os.path.dirname(AQUI)
CLIENTES = os.path.join(LUCIA, 'clientes')
DESTINO = os.path.join(CLIENTES, 'datos')


SESIONES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sesiones')


def acta(spec):
    """Una entrada de acta: el acta entera, más dónde está su PDF.

    `archivo` es el nombre del acta en `sesiones/`. Si no está, se detiene:
    mejor eso que publicar la app de un cliente con un acta a medias."""
    ruta = os.path.join(SESIONES, spec['archivo'])
    if not os.path.exists(ruta):
        raise SystemExit('el acta declarada no existe: %s' % ruta)
    d = json.load(open(ruta, encoding='utf-8'))
    d['archivo'] = spec['archivo']
    d['pdf'] = 'actas/' + spec['pdf']
    d['iso'] = spec.get('iso', '')
    d['grabacion'] = spec.get('grabacion', '')
    d['informe'] = spec.get('informe')
    d['prevista'] = False
    return d


def canal_vacio(spec):
    """Un canal sin un solo mensaje, con todas las claves que la vista lee."""
    return {
        'canal': spec['canal'],
        'id': spec.get('id', spec['canal']),
        'nombre': spec.get('nombre', spec['canal']),
        'mensajes': [],
        'conteo': 0,
        'conteo_total': 0,
        'desde': '',
        'hasta': '',
        'adjuntos': 0,
        # Las actas que el cliente ya tiene. Se declaran en su archivo y el
        # contenido sale del acta de verdad, la de `sesiones/`, para que la app
        # muestre la misma que se publicó y no una copia que se desactualiza.
        'actas': [acta(a) for a in (spec.get('actas') or [])],
        'fijados': spec.get('fijados', []),
        # Un cliente nuevo no tiene grabaciones, pero puede traerlas de antes
        # de que su espacio existiera: las de Novasoft estaban dentro de la app
        # vieja y se habrían perdido al reconstruirla. Se declaran en el
        # archivo de cliente y entran aquí.
        'grabaciones': spec.get('grabaciones', []),
        'informes': [],
        'pulso': [],
    }


def paquete(cfg):
    canales = cfg.get('canales') or []
    if not canales:
        raise SystemExit('a %s.json le faltan los canales' % cfg['slug'])
    return {
        'espacio': cfg['espacio'],
        'cliente': cfg['nombre'],
        'programa': cfg['programa'],
        'canales': [canal_vacio(c) for c in canales],
        # Todo lo que la vista del archivo lee y un cliente nuevo no tiene.
        'personas': [],
        'n_grabaciones': sum(len(c.get('grabaciones') or []) for c in canales),
        'asistencia': [],
        'mentoria': [],
        'sesiones_informe': [],
        'semanas': [],
        'pulso': [],
        'pulso_actas': [],
        'generales': cfg.get('generales', []),
        'nota_fijados': cfg.get('nota_fijados', ''),
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    slug = sys.argv[1]
    ruta = os.path.join(CLIENTES, slug + '.json')
    if not os.path.exists(ruta):
        raise SystemExit('no hay cliente «%s»' % slug)
    cfg = json.load(open(ruta, encoding='utf-8'))
    d = paquete(cfg)
    os.makedirs(DESTINO, exist_ok=True)
    salida = os.path.join(DESTINO, slug + '.js')
    with open(salida, 'w', encoding='utf-8') as f:
        f.write('window.ARCHIVO=')
        json.dump(d, f, ensure_ascii=False, separators=(',', ':'))
        f.write(';\n')
    print('%s\n  %d canal(es): %s\n  %d bytes'
          % (salida, len(d['canales']),
             ', '.join(c['canal'] for c in d['canales']),
             os.path.getsize(salida)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
