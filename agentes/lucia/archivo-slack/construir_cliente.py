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
ARCHIVO_SLACK = os.path.join(AQUI, 'datos', 'archivo.json')


def canal_slack(nombre):
    """El canal ya parseado de raw/, si el cliente declara uno.

    Un cliente puede tener su propio canal de Slack y entonces no nace vacio:
    trae su conversacion. Se lee del mismo archivo normalizado que usa
    Comfacesar, para no parsear dos veces lo mismo."""
    if not os.path.exists(ARCHIVO_SLACK):
        raise SystemExit('falta %s: corre parsear.py antes' % ARCHIVO_SLACK)
    d = json.load(open(ARCHIVO_SLACK, encoding='utf-8'))
    for c in d['canales']:
        if c['canal'] == nombre:
            return c
    raise SystemExit('el canal declarado no esta en el archivo: %s' % nombre)


def acta(spec):
    """Una entrada de acta: el acta entera, más dónde está su PDF.

    `archivo` es el nombre del acta en `sesiones/`. Si no está, se detiene:
    mejor eso que publicar la app de un cliente con un acta a medias."""
    ruta = os.path.join(SESIONES, spec['archivo'])
    if not os.path.exists(ruta):
        raise SystemExit('el acta declarada no existe: %s' % ruta)
    d = json.load(open(ruta, encoding='utf-8'))
    d['archivo'] = spec['archivo']
    # Un acta puede quedarse sin PDF a proposito, cuando el original se retira
    # porque llevaba dentro algo que no debe circular. El acta escrita sigue
    # siendo la version vigente, asi que la vista se arma igual y solo deja de
    # ofrecer el boton de abrir el PDF.
    d['pdf'] = ('actas/' + spec['pdf']) if spec.get('pdf') else ''
    d['iso'] = spec.get('iso', '')
    d['grabacion'] = spec.get('grabacion', '')
    d['informe'] = spec.get('informe')
    d['prevista'] = False
    return d


def recortar(slack, desde):
    """Deja el canal a partir de una fecha, si el cliente declara `desde`.

    Un espacio de cliente no siempre empieza el dia que nace el canal de Slack.
    Klaren's arranca en su kick off: lo anterior fueron sesiones de preparacion
    con una sola persona, con conversacion que no corresponde al equipo que hoy
    entra a la app. El recorte es de presentacion, no de borrado: en `raw/` y en
    el archivo normalizado queda todo."""
    if not slack or not desde:
        return slack
    ms = [m for m in slack.get('mensajes') or [] if m.get('fecha', '') >= desde]
    vivos = [m for m in ms if not m.get('sistema')]
    q = dict(slack)
    q['mensajes'] = ms
    q['conteo'] = len(vivos)
    q['conteo_total'] = len(ms)
    q['desde'] = min((m['fecha'] for m in ms), default='')
    q['hasta'] = max((m['fecha'] for m in ms), default='')
    q['adjuntos'] = sum(len(m.get('adjuntos') or []) for m in ms)
    return q


def enlazar_adjuntos(mensajes, carpeta):
    """Apunta cada adjunto al archivo bajado de Slack, nombrado por su ID.

    Es el mismo trato que reciben los adjuntos de Comfacesar: el nombre que
    traen en Slack lleva emojis y tildes y no sobrevive al viaje, asi que en
    disco se guardan como <ID de Slack>.<extension>. Sin esto la tarjeta del
    mensaje se ve igual pero al pinchar el adjunto no pasa nada.

    `carpeta` es la del propio cliente, declarada en su `fuente_archivos`. No
    se comparte con Comfacesar a proposito: publicar.py copia esa carpeta
    entera dentro de la app, y la de Comfacesar lleva 71 adjuntos del programa
    que no tienen por que viajar al espacio de otro cliente."""
    if not carpeta or not os.path.isdir(carpeta):
        return 0
    hay = {}
    for f in os.listdir(carpeta):
        hay[f.split('.')[0]] = f
    n = 0
    for m in mensajes:
        for a in m.get('adjuntos') or []:
            if a.get('url'):
                continue
            f = hay.get(a.get('id'))
            if f:
                a['url'] = 'archivos/' + f
                n += 1
    return n


MENTORIA = 'Sandra Curvelo'


def asistencia_de(canales):
    """Las vistas de asistencia y de personas, armadas con los informes de cada acta.

    La plantilla espera tres listas que en Comfacesar salen de los informes de
    Teams. Aqui salen de lo que cada acta declara en su clave `informe`, que es
    lo mismo medido a mano. La facilitadora va aparte, en `mentoria`, para que
    no compita en el ranking con el equipo del cliente."""
    gente, sesiones = {}, []
    for c in canales:
        for a in c.get('actas') or []:
            inf = a.get('informe')
            if not inf:
                continue
            num = a.get('sesion_num') or 0
            sesiones.append({
                'titulo': a.get('subtitulo_meta') or a.get('archivo'),
                'fecha': a.get('iso', ''), 'hora': '',
                'duracion_min': inf.get('duracion_min', 0),
                'media_min': inf.get('media_min', 0),
                'canal': c['canal'], 'sesion': num,
                'archivo': a.get('archivo', ''),
                'participantes': inf.get('participantes') or [],
            })
            for q in inf.get('participantes') or []:
                r = gente.setdefault(q['nombre'], {
                    'nombre': q['nombre'], 'cargo': '', 'correo': q.get('correo') or '',
                    'minutos': 0, 'sesiones': []})
                r['minutos'] += q.get('minutos', 0)
                r['correo'] = r['correo'] or (q.get('correo') or '')
                r['sesiones'].append({'canal': c['canal'], 'sesion': num,
                                      'fecha': a.get('iso', ''),
                                      'minutos': q.get('minutos', 0),
                                      'rol': q.get('rol', '')})
            for q in a.get('participantes') or []:
                if q.get('nombre') in gente and q.get('cargo'):
                    gente[q['nombre']]['cargo'] = q['cargo']
    for r in gente.values():
        r['sesiones'].sort(key=lambda x: x['fecha'], reverse=True)
    equipo = sorted((r for n, r in gente.items() if n != MENTORIA),
                    key=lambda r: -r['minutos'])
    mentoria = [r for n, r in gente.items() if n == MENTORIA]
    sesiones.sort(key=lambda x: x['fecha'], reverse=True)
    return equipo, mentoria, sesiones


def personas_de(hechos):
    """Quien escribio en los canales que el cliente trae de Slack.

    Se cuenta sobre los mensajes que la app va a mostrar, ya recortados por
    `desde`, y no sobre la lectura completa: si no, aparece gente que escribio
    antes de que el espacio del cliente empezara. Los nombres y correos salen
    del archivo normalizado, que es donde el conector los deja."""
    cuenta, vistos = {}, {}
    for c in hechos:
        for m in c.get('mensajes') or []:
            if m.get('sistema'):
                continue
            cuenta[m['uid']] = cuenta.get(m['uid'], 0) + 1
            vistos.setdefault(m['uid'], set()).add(c['canal'])
    if not cuenta:
        return []
    d = json.load(open(ARCHIVO_SLACK, encoding='utf-8'))
    salida = []
    for p in d['personas']:
        if p['uid'] in cuenta:
            q = dict(p)
            q['mensajes'] = cuenta[p['uid']]
            q['canales'] = sorted(vistos[p['uid']])
            salida.append(q)
    salida.sort(key=lambda q: (-q['mensajes'], q['nombre']))
    return salida


def canal_vacio(spec, adjuntos=None):
    """Un canal con todas las claves que la vista lee.

    Nace vacio salvo que el cliente declare `fuente_slack`: entonces trae la
    conversacion real de ese canal."""
    slack = canal_slack(spec['fuente_slack']) if spec.get('fuente_slack') else {}
    slack = recortar(slack, spec.get('desde'))
    if slack:
        enlazados = enlazar_adjuntos(slack.get('mensajes') or [], adjuntos)
        print('  %s: %d mensajes de Slack, %d adjuntos enlazados'
              % (spec['canal'], len(slack.get('mensajes') or []), enlazados))
    return {
        'canal': spec['canal'],
        'id': spec.get('id', spec['canal']),
        'nombre': spec.get('nombre', spec['canal']),
        # El icono es adorno y se elige por canal. `cerrado` no es adorno: la
        # vista no lista el canal a quien no edita, y sus mensajes van a la
        # colección `privado`, que el servidor solo abre a los editores. Por eso
        # un canal cerrado nace vacío aquí: lo que se mete en la página lo lee
        # cualquiera que mire el código.
        'icono': spec.get('icono', ''),
        'cerrado': bool(spec.get('cerrado')),
        'mensajes': slack.get('mensajes', []),
        'conteo': slack.get('conteo', 0),
        'conteo_total': slack.get('conteo_total', 0),
        'desde': slack.get('desde', ''),
        'hasta': slack.get('hasta', ''),
        'adjuntos': slack.get('adjuntos', 0),
        # Las actas que el cliente ya tiene. Se declaran en su archivo y el
        # contenido sale del acta de verdad, la de `sesiones/`, para que la app
        # muestre la misma que se publicó y no una copia que se desactualiza.
        'actas': [acta(a) for a in (spec.get('actas') or [])
                  if not spec.get('desde') or a.get('iso', '') >= spec['desde']],
        'fijados': spec.get('fijados', []),
        # Un cliente nuevo no tiene grabaciones, pero puede traerlas de antes
        # de que su espacio existiera: las de Novasoft estaban dentro de la app
        # vieja y se habrían perdido al reconstruirla. Se declaran en el
        # archivo de cliente y entran aquí.
        'grabaciones': [g for g in (spec.get('grabaciones') or [])
                        if not spec.get('desde') or g.get('fecha', '') >= spec['desde']],
        'informes': [],
        'pulso': [],
    }


def paquete(cfg):
    canales = cfg.get('canales') or []
    rel = cfg.get('fuente_archivos')
    adjuntos = (rel if not rel or os.path.isabs(rel)
                else os.path.join(LUCIA, rel))
    hechos = [canal_vacio(c, adjuntos) for c in canales]
    asistencia = asistencia_de(hechos)
    if not canales:
        raise SystemExit('a %s.json le faltan los canales' % cfg['slug'])
    return {
        'espacio': cfg['espacio'],
        'cliente': cfg['nombre'],
        'programa': cfg['programa'],
        'canales': hechos,
        # Todo lo que la vista del archivo lee y un cliente nuevo no tiene.
        'personas': personas_de(hechos),
        'n_grabaciones': sum(len(c.get('grabaciones') or []) for c in hechos),
        'asistencia': asistencia[0],
        'mentoria': asistencia[1],
        'sesiones_informe': asistencia[2],
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
