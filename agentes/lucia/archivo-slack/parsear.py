# -*- coding: utf-8 -*-
"""Convierte los volcados de raw/*.json en un archivo normalizado.

Salida: datos/archivo.json  — un solo objeto con canales, mensajes y personas.
"""
import json, os, re, glob, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(AQUI, 'raw')
DATOS = os.path.join(AQUI, 'datos')

CABECERA = re.compile(r'Channel: #([^\s(]+) \(([A-Z0-9]+)\)')
MSG = re.compile(
    r'=== Message from (?P<autor>.+?) at '
    r'(?P<fecha>\d{4}-\d{2}-\d{2}) (?P<hora>\d{2}:\d{2}:\d{2}) '
    r'(?P<tz>[+-]\d{2}) ===\s*\n'
    r'Message TS: (?P<ts>[\d.]+)\n'
)
AUTOR = re.compile(
    r'^(?P<nombre>.*?)(?: <(?P<correo>[^>]+)>)? '
    r'\((?P<uid>[A-Z0-9]+)(?:,[^)]*)?\)$')
ARCHIVOS = re.compile(r'^Files: (.+)$', re.M)
UN_ARCHIVO = re.compile(r'([^,(]+?) \(ID: (F[A-Z0-9]+), ([^,]+), ([^)]+)\)')
HILO = re.compile(r'^Thread: (\d+) repl\w+ \(latest: ([^)]+)\)$', re.M)
REACC = re.compile(r'^Reactions: (.+)$', re.M)
UNA_REACC = re.compile(r'([a-z0-9_+\-]+) \((\d+)\)')

MESES = ['enero','febrero','marzo','abril','mayo','junio',
         'julio','agosto','septiembre','octubre','noviembre','diciembre']


def limpiar_slack(t):
    """Deja el texto listo para mostrar, conservando el marcado de Slack."""
    return t.strip()


def parsear_archivo(ruta):
    bruto = open(ruta, encoding='utf-8').read()
    # el volcado viene envuelto en {"messages": "...", "pagination_info": "..."}
    try:
        obj = json.loads(bruto)
        texto = obj.get('messages', '')
    except json.JSONDecodeError:
        texto = bruto

    m = CABECERA.search(texto)
    if not m:
        return None
    canal, cid = m.group(1), m.group(2)

    cortes = list(MSG.finditer(texto))
    mensajes = []
    for i, c in enumerate(cortes):
        ini = c.end()
        fin = cortes[i + 1].start() if i + 1 < len(cortes) else len(texto)
        cuerpo = texto[ini:fin]

        adjuntos = []
        for fm in ARCHIVOS.finditer(cuerpo):
            for a in UN_ARCHIVO.finditer(fm.group(1)):
                adjuntos.append({
                    'nombre': a.group(1).strip(),
                    'id': a.group(2),
                    'tipo': a.group(3).strip(),
                    'peso': a.group(4).strip(),
                })
        cuerpo = ARCHIVOS.sub('', cuerpo)

        hilo = None
        hm = HILO.search(cuerpo)
        if hm:
            hilo = {'respuestas': int(hm.group(1)), 'ultima': hm.group(2)}
            cuerpo = HILO.sub('', cuerpo)

        reacciones = []
        rm = REACC.search(cuerpo)
        if rm:
            reacciones = [{'emoji': r.group(1), 'cuenta': int(r.group(2))}
                          for r in UNA_REACC.finditer(rm.group(1))]
            cuerpo = REACC.sub('', cuerpo)

        # Adjuntos de bot ("Attachment: Botón Continuar")
        cuerpo = re.sub(r'^Attachment: .+$', '', cuerpo, flags=re.M)

        am = AUTOR.match(c.group('autor').strip())
        if am:
            nombre, correo, uid = am.group('nombre'), am.group('correo'), am.group('uid')
        else:
            nombre, correo, uid = c.group('autor').strip(), None, ''

        mensajes.append({
            'ts': c.group('ts'),
            'fecha': c.group('fecha'),
            'hora': c.group('hora')[:5],
            'autor': nombre.strip(),
            'correo': correo,
            'uid': uid,
            'texto': limpiar_slack(cuerpo),
            'adjuntos': adjuntos,
            'hilo': hilo,
            'reacciones': reacciones,
        })

    mensajes.sort(key=lambda x: float(x['ts']))
    return {'canal': canal, 'id': cid, 'mensajes': mensajes}


def es_sistema(m):
    t = m['texto']
    patrones = (
        r'^<@[A-Z0-9]+\|[^>]+> (se uni\u00f3 al canal|abandon\u00f3 el canal|sali\u00f3 del canal)$',
        r'^<@[A-Z0-9]+\|[^>]+> se ha unido al canal$',
        r'^.{0,60} se ha unido al canal$',
        r'^.{0,80} agreg\u00f3 a este canal a ',
        r'^Bienvenido <@',
        r'^se cambiaron los permisos de publicaci\u00f3n del canal$',
        r'^cambi\u00f3 el nombre del canal',
        r'^defini\u00f3 el tema del canal',
        r'^estableci\u00f3 la descripci\u00f3n del canal',
        r'^(a\u00f1adi\u00f3|quit\u00f3|fij\u00f3|dej\u00f3 de fijar) ',
        r'^This message was deleted\.$',
        r"^:wave: \*Hello! I'm Claude",
    )
    return any(re.search(p, t) for p in patrones)


def main():
    os.makedirs(DATOS, exist_ok=True)
    canales, personas = [], {}
    for ruta in sorted(glob.glob(os.path.join(RAW, '*.json'))):
        c = parsear_archivo(ruta)
        if not c:
            print('  omitido:', os.path.basename(ruta))
            continue
        reales = [m for m in c['mensajes'] if not es_sistema(m)]
        c['conteo'] = len(reales)
        c['conteo_total'] = len(c['mensajes'])
        c['desde'] = c['mensajes'][0]['fecha'] if c['mensajes'] else None
        c['hasta'] = c['mensajes'][-1]['fecha'] if c['mensajes'] else None
        c['adjuntos'] = sum(len(m['adjuntos']) for m in c['mensajes'])
        for m in c['mensajes']:
            m['sistema'] = es_sistema(m)
            if m['uid'] and not m['uid'].startswith('B'):
                p = personas.setdefault(m['uid'], {
                    'uid': m['uid'], 'nombre': m['autor'],
                    'correo': m['correo'], 'mensajes': 0, 'canales': []})
                if not m['sistema']:
                    p['mensajes'] += 1
                if c['canal'] not in p['canales']:
                    p['canales'].append(c['canal'])
        canales.append(c)
        print('  %-40s %4d mensajes  %3d adjuntos  %s → %s'
              % (c['canal'], c['conteo'], c['adjuntos'], c['desde'], c['hasta']))

    canales.sort(key=lambda c: -c['conteo'])
    salida = {
        'espacio': 'IAM™Team',
        'cliente': 'Comfacesar',
        'programa': 'IAM™ Intelligence',
        'canales': canales,
        'personas': sorted(personas.values(), key=lambda p: -p['mensajes']),
    }
    ruta = os.path.join(DATOS, 'archivo.json')
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(salida, f, ensure_ascii=False, separators=(',', ':'))
    print('\n%d canales · %d mensajes · %d personas · %d adjuntos'
          % (len(canales), sum(c['conteo'] for c in canales),
             len(personas), sum(c['adjuntos'] for c in canales)))
    print('  %s  (%.0f KB)' % (ruta, os.path.getsize(ruta) / 1024))


if __name__ == '__main__':
    main()
