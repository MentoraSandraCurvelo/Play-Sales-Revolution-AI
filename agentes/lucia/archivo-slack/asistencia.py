# -*- coding: utf-8 -*-
"""Convierte los informes de asistencia de Teams en datos por sesión y por persona.

Entrada:  datos/asistencia/*.json   (lo que devolvió el conector de Dropbox)
Salida:   datos/asistencia-teams.json
"""
import json, os, glob, re, unicodedata
from collections import defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
ORIGEN = os.path.join(AQUI, 'datos', 'asistencia')
INDICE = '/tmp/claude-0/asis-indice.json'

# carpeta del Dropbox -> canal de Slack
CANAL_DE = {
    '1. Comunicaciones': 'comunicaciones',
    '2. Vivienda': 'vivienda',
    '3. Agencia de Empleo': 'agencia-de-empleo',
    '4. Mercadeo': 'mercadeo',
    '5. Juridica': 'juridica',
    '6. Educacion': 'educacion',
    '7. Talento humano': 'talento-humano',
    '8. Tecnologia': 'tecnologia',
    '9. Gerencia Financiera': 'gerencia-financiera',
    '10. Servicios Sociales': 'serivcios-sociales',
    '11.Planeacion': 'planeacion',
    '12. Contabilidad': 'contabilidad',
    '13. Sub-Operativa': 'sub-operativa',
    '14. Tesoreria': 'tesoreriaa',
    '15. Subdireccion Financiera': 'sub-admin-y-financiera-infraestructura',
    '16. IPS': 'ips',
    '17. Subisidio': 'subsidio',
    '18. Cumplimineto': 'cumplimiento',
}

# El notetaker no es una persona del equipo y no entra en la asistencia.
RX_BOT = re.compile(r'(read\.?ai|fireflies|meeting assistant|notetaker|meeting notes)', re.I)
RX_DUR = re.compile(r'(?:(\d+)\s*h)?\s*(?:(\d+)\s*min)?\s*(?:(\d+)s)?')
RX_FECHA = re.compile(r'(\d{1,2})/(\d{1,2})/(\d{2}),\s*(\d{1,2}):(\d{2}):(\d{2})\s*([AP]M)')


def minutos(t):
    m = RX_DUR.match((t or '').strip())
    if not m:
        return 0
    h, mi, s = (int(x) if x else 0 for x in m.groups())
    return h * 60 + mi + (1 if s >= 30 else 0)


def iso(t):
    m = RX_FECHA.search(t or '')
    if not m:
        return None, None
    mes, dia, ano, hh, mm, _, ampm = m.groups()
    hh = int(hh) % 12 + (12 if ampm == 'PM' else 0)
    return '20%s-%02d-%02d' % (ano, int(mes), int(dia)), '%02d:%s' % (hh, mm)


def clave(n):
    """Nombres como 'RINA ROPAÍN', 'Rina Ropaín' y 'Rina R.' deben juntarse."""
    s = unicodedata.normalize('NFD', n or '').encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\(.*?\)|[^a-z\s]', ' ', s)
    return ' '.join(s.split())


def seccion(texto, titulo):
    partes = re.split(r'\n\s*\d\.\s', '\n' + texto)
    for p in partes:
        if p.strip().lower().startswith(titulo.lower()):
            return p
    return ''


def parsear(d, meta):
    t = d['text']
    res = dict(re.findall(r'^([^\t\n]+)\t(.+)$', seccion(t, 'Resumen'), re.M))
    fecha, hora = iso(res.get('Hora de inicio', ''))
    gente, orden = {}, []
    for ln in seccion(t, 'Participantes').split('\n'):
        c = ln.split('\t')
        if len(c) < 4 or c[0].strip() in ('Nombre', 'Participantes') or not c[0].strip():
            continue
        nombre = re.sub(r'\s*\((No comprobado|Externo)\)\s*$', '', c[0]).strip()
        if not nombre or RX_BOT.search(nombre):
            continue
        k = clave(nombre)
        if not k:
            continue
        if k not in gente:
            gente[k] = {'nombre': nombre, 'minutos': 0, 'correo': '', 'rol': ''}
            orden.append(k)
        # varias entradas de la misma persona: se queda la más larga, no la suma,
        # porque Teams repite el tramo completo en cada reconexión
        gente[k]['minutos'] = max(gente[k]['minutos'], minutos(c[3]))
        if len(c) > 4 and '@' in c[4] and not gente[k]['correo']:
            gente[k]['correo'] = c[4].strip()
        if len(c) > 6 and c[6].strip():
            gente[k]['rol'] = c[6].strip()
        if len(nombre) > len(gente[k]['nombre']):
            gente[k]['nombre'] = nombre

    return {
        'titulo': res.get('Título de la reunión', '').strip('"').strip(),
        'fecha': fecha, 'hora': hora,
        'duracion_min': minutos(res.get('Duración de la reunión', '')),
        'media_min': minutos(res.get('Tiempo medio de asistencia', '')),
        'canal': meta['canal'], 'sesion': meta['sesion'], 'archivo': meta['nombre'],
        'participantes': [gente[k] for k in orden],
    }


def main():
    idx = json.load(open(INDICE, encoding='utf-8'))
    sesiones = []
    for ruta in sorted(glob.glob(os.path.join(ORIGEN, '*.json'))):
        d = json.load(open(ruta, encoding='utf-8'))
        info = idx.get(d['id']) or {}
        p = info.get('path', '') or d.get('metadata', {}).get('path_display', '')
        m = re.search(r'IAM™ Intelligence/([^/]+)/[Ss]esion\s*(\d+)', p)
        if not m:
            print('  sin ruta:', d['id']); continue
        canal = CANAL_DE.get(m.group(1))
        if not canal:
            print('  sin canal:', m.group(1)); continue
        s = parsear(d, {'canal': canal, 'sesion': int(m.group(2)),
                        'nombre': info.get('name', '')})
        if s['fecha']:
            sesiones.append(s)

    # una sesión puede tener dos informes (el mismo archivo guardado dos veces)
    vistas, limpio = {}, []
    for s in sorted(sesiones, key=lambda x: (x['canal'], x['sesion'], -len(x['participantes']))):
        k = (s['canal'], s['fecha'], s['hora'])
        if k in vistas:
            continue
        vistas[k] = True
        limpio.append(s)
    limpio.sort(key=lambda s: (s['fecha'], s['hora'] or ''))

    personas = defaultdict(lambda: {'nombre': '', 'correo': '', 'minutos': 0, 'sesiones': []})
    for s in limpio:
        for p in s['participantes']:
            g = personas[clave(p['nombre'])]
            if len(p['nombre']) > len(g['nombre']):
                g['nombre'] = p['nombre']
            if p['correo'] and not g['correo']:
                g['correo'] = p['correo']
            g['minutos'] += p['minutos']
            g['sesiones'].append({'canal': s['canal'], 'sesion': s['sesion'],
                                  'fecha': s['fecha'], 'minutos': p['minutos'],
                                  'rol': p['rol']})
    for g in personas.values():
        g['n'] = len(g['sesiones'])
        g['canales'] = sorted({x['canal'] for x in g['sesiones']})
        g['sesiones'].sort(key=lambda x: x['fecha'], reverse=True)

    salida = {
        'sesiones': limpio,
        'personas': sorted(personas.values(), key=lambda g: (-g['n'], -g['minutos'])),
    }
    with open(os.path.join(AQUI, 'datos', 'asistencia-teams.json'), 'w', encoding='utf-8') as f:
        json.dump(salida, f, ensure_ascii=False)
    print('%d sesiones con informe · %d personas · %d participaciones · %d horas'
          % (len(limpio), len(personas), sum(g['n'] for g in personas.values()),
             round(sum(g['minutos'] for g in personas.values()) / 60)))


if __name__ == '__main__':
    main()


# ──────────────────────────────────────────────────────────────────────────
# Conciliación contra el listado oficial: los nombres canónicos salen de los
# participantes de las actas. Lo que no case no se publica como persona —
# queda aparte para que Sandra decida, que es la regla.
# ──────────────────────────────────────────────────────────────────────────

LUCIA = os.path.dirname(AQUI)
RX_ACTA = re.compile(r'(.+?)-s(\d+)(?:-prevista)?-(\d{4}-\d{2}-\d{2})\.json$')

GENERICO = re.compile(
    r'^(comunicaciones|comfacesar|vivienda|subdireccion|coordinacion|aa|lucy)\b|'
    r'\b(comfacesar|comunicaciones|operativa|obras)\b$', re.I)


def canonicos():
    """nombre canónico -> (canal, cargo), sacado de los participantes de las actas."""
    from importlib import import_module
    cn = json.load(open(os.path.join(AQUI, 'datos', 'canal-de-acta.json'), encoding='utf-8'))
    por_canal = defaultdict(dict)
    for ruta in sorted(glob.glob(os.path.join(LUCIA, 'sesiones', '*.json'))):
        m = RX_ACTA.search(os.path.basename(ruta))
        canal = cn.get(m.group(1)) if m else None
        if not canal:
            continue
        d = json.load(open(ruta, encoding='utf-8'))
        for p in (d.get('participantes') or []):
            n = p.get('nombre') if isinstance(p, dict) else str(p)
            if not n:
                continue
            por_canal[canal].setdefault(n.strip(), {
                'nombre': n.strip(),
                'cargo': (p.get('cargo') or '') if isinstance(p, dict) else '',
                'correo': (p.get('correo') or '') if isinstance(p, dict) else '',
            })
    return por_canal


def fichas(n):
    return {t for t in clave(n).split() if len(t) >= 3}


def conciliar(salida):
    oficial = canonicos()
    mapa, sueltos = {}, defaultdict(set)
    for s in salida['sesiones']:
        for p in s['participantes']:
            if (s['canal'], p['nombre']) in mapa:
                continue
            if GENERICO.search(p['nombre'].strip()):
                sueltos[s['canal']].add(p['nombre']); continue
            tn = fichas(p['nombre'])
            mejor, punt = None, 0
            for cand in oficial.get(s['canal'], {}).values():
                comun = tn & fichas(cand['nombre'])
                if len(comun) > punt:
                    mejor, punt = cand, len(comun)
            if mejor and punt >= 1:
                mapa[(s['canal'], p['nombre'])] = mejor
                continue
            # segunda pasada: el acta de ese canal puede no listarlo, pero si
            # coinciden nombre Y apellido con alguien del listado, es esa persona
            mejor2, punt2 = None, 1
            for canal2 in oficial:
                for cand in oficial[canal2].values():
                    comun = tn & fichas(cand['nombre'])
                    if len(comun) > punt2:
                        mejor2, punt2 = cand, len(comun)
            if mejor2:
                mapa[(s['canal'], p['nombre'])] = mejor2
            else:
                sueltos[s['canal']].add(p['nombre'])

    # reconstruir las personas con el nombre oficial
    # El listado trae el mismo nombre en dos formas ("Rafael Solano" y "Rafael
    # José Solano Fernández"). Cuando una es subconjunto de la otra dentro del
    # mismo canal, es la misma persona: se queda la forma completa.
    porcanal = defaultdict(set)
    for (canal, _), c in mapa.items():
        porcanal[canal].add(c['nombre'])
    unifica = {}
    for canal, nombres in porcanal.items():
        for a in nombres:
            for b in nombres:
                if a != b and fichas(a) < fichas(b):
                    unifica[(canal, a)] = b
    for k, c in mapa.items():
        destino = unifica.get((k[0], c['nombre']))
        if destino:
            mapa[k] = dict(c, nombre=destino)

    personas = defaultdict(lambda: {'nombre': '', 'cargo': '', 'correo': '',
                                    'minutos': 0, 'sesiones': {}})
    for s in salida['sesiones']:
        for p in s['participantes']:
            c = mapa.get((s['canal'], p['nombre']))
            if not c:
                continue
            p['oficial'] = c['nombre']
            g = personas[c['nombre']]
            g['nombre'] = c['nombre']
            g['cargo'] = g['cargo'] or c['cargo']
            g['correo'] = g['correo'] or (p['correo'] or c['correo'])
            # una persona conectada desde dos aparatos aparece dos veces en el
            # mismo informe: es una sola asistencia, y vale el tramo más largo
            k = (s['canal'], s['fecha'])
            ya = g['sesiones'].get(k)
            if ya is None or p['minutos'] > ya['minutos']:
                g['sesiones'][k] = {'canal': s['canal'], 'sesion': s['sesion'],
                                    'fecha': s['fecha'], 'minutos': p['minutos'],
                                    'rol': p['rol']}
    for g in personas.values():
        g['sesiones'] = sorted(g['sesiones'].values(), key=lambda x: x['fecha'], reverse=True)
        g['minutos'] = sum(x['minutos'] for x in g['sesiones'])
        g['n'] = len(g['sesiones'])
        g['canales'] = sorted({x['canal'] for x in g['sesiones']})

    # la mentoría es por cargo, no por apellido: Juan Pablo Curvelo es de
    # Servicios Sociales, no de la mentoría
    def es_mentoria(g):
        return ('mentora iam' in (g['cargo'] or '').lower()
                or clave(g['nombre']) == 'sandra curvelo')

    mentoria = [g for g in personas.values() if es_mentoria(g)]
    equipo = [g for g in personas.values() if not es_mentoria(g)]
    salida['personas'] = sorted(equipo, key=lambda g: (-g['n'], -g['minutos']))
    salida['mentoria'] = sorted(mentoria, key=lambda g: -g['n'])
    salida['por_confirmar'] = {c: sorted(v) for c, v in sorted(sueltos.items()) if v}
    print('\n%d personas del listado · %d participaciones · %d horas de sala'
          % (len(equipo), sum(g['n'] for g in equipo),
             round(sum(g['minutos'] for g in equipo) / 60)))
    print('%d nombres sin casar con el listado, en %d canales'
          % (sum(len(v) for v in salida['por_confirmar'].values()),
             len(salida['por_confirmar'])))
