# -*- coding: utf-8 -*-
"""Arma app/datos.js: mensajes + actas + fijados en un solo paquete."""
import json, os, glob, re
from datetime import date, timedelta

AQUI = os.path.dirname(os.path.abspath(__file__))
LUCIA = os.path.dirname(AQUI)

# prefijo del nombre de archivo del acta  ->  canal de Slack
CANAL_DE = {
    'agencia-empleo': 'agencia-de-empleo',
    'comunicaciones': 'comunicaciones',
    'contabilidad': 'contabilidad',
    'cumplimiento': 'cumplimiento',
    'educacion': 'educacion',
    'gerencia-financiera': 'gerencia-financiera',
    'ips': 'ips',
    'juridica': 'juridica',
    'mercadeo': 'mercadeo',
    'planeacion': 'planeacion',
    'servicios-sociales': 'serivcios-sociales',
    'sub-financiera': 'sub-admin-y-financiera-infraestructura',
    'sub-operativa': 'sub-operativa',
    'subsidio': 'subsidio',
    'talento-humano': 'talento-humano',
    'tecnologia': 'tecnologia',
    'tesoreria': 'tesoreriaa',
    'vivienda': 'vivienda',
}

NOMBRE = {
    'agencia-de-empleo': 'Agencia de Empleo',
    'comunicaciones': 'Comunicaciones',
    'contabilidad': 'Contabilidad',
    'cumplimiento': 'Cumplimiento',
    'educacion': 'Educación',
    'gerencia-financiera': 'Gerencia Financiera',
    'ips': 'IPS',
    'juridica': 'Jurídica',
    'mercadeo': 'Mercadeo',
    'planeacion': 'Planeación',
    'serivcios-sociales': 'Servicios Sociales',
    'sub-admin-y-financiera-infraestructura': 'Sub. Administrativa y Financiera',
    'sub-operativa': 'Sub. Operativa y Comercial',
    'subsidio': 'Subsidio',
    'talento-humano': 'Talento Humano',
    'tecnologia': 'Tecnología',
    'tesoreriaa': 'Tesorería',
    'todo-iamteam': 'Todo IAM™Team',
    'vivienda': 'Vivienda',
}

CAMPOS_ACTA = ('area', 'area_completa', 'sesion_num', 'fase', 'fecha', 'fecha_corta',
               'subtitulo_meta', 'datos_sesion', 'kpis', 'participantes', 'riesgos',
               'alertas', 'ejercicios', 'oportunidades', 'tareas_intro', 'tareas',
               'observaciones', 'proxima_sesion')

PATRON = re.compile(r'(.+?)-s(\d+)(-prevista)?-(\d{4}-\d{2}-\d{2})\.json$')


def cargar_actas():
    por_canal = {}
    for ruta in sorted(glob.glob(os.path.join(LUCIA, 'sesiones', '*.json'))):
        m = PATRON.search(os.path.basename(ruta))
        if not m:
            print('  sin patrón:', os.path.basename(ruta)); continue
        canal = CANAL_DE.get(m.group(1))
        if not canal:
            print('  sin canal:', m.group(1)); continue
        d = json.load(open(ruta, encoding='utf-8'))
        a = {k: d[k] for k in CAMPOS_ACTA if k in d}
        a['archivo'] = os.path.basename(ruta)
        a['prevista'] = bool(m.group(3))
        a['iso'] = m.group(4)
        por_canal.setdefault(canal, []).append(a)
    for canal in por_canal:
        por_canal[canal].sort(key=lambda a: (a['iso'], a.get('sesion_num', 0)))
    return por_canal



def lunes(iso):
    y, m, d = map(int, iso.split('-'))
    f = date(y, m, d)
    return (f - timedelta(days=f.weekday())).isoformat()


def pulso(archivo):
    """Mensajes por semana: uno global y uno por canal, alineados al mismo eje."""
    semanas = sorted({lunes(m['fecha'])
                      for c in archivo['canales'] for m in c['mensajes'] if not m['sistema']})
    indice = {s: i for i, s in enumerate(semanas)}
    global_ = [0] * len(semanas)
    for c in archivo['canales']:
        serie = [0] * len(semanas)
        for m in c['mensajes']:
            if m['sistema']:
                continue
            i = indice[lunes(m['fecha'])]
            serie[i] += 1
            global_[i] += 1
        c['pulso'] = serie
    archivo['semanas'] = semanas
    archivo['pulso'] = global_
    # actas por semana, sobre el mismo eje
    act = [0] * len(semanas)
    for c in archivo['canales']:
        for a in c['actas']:
            k = lunes(a['iso'])
            if k in indice:
                act[indice[k]] += 1
    archivo['pulso_actas'] = act



RX_VIDEO = re.compile(
    r'<(?P<url>https://(?:netorg\d+-my\.sharepoint\.com|docs\.google\.com/videos)/[^>|\s]+)'
    r'(?:\|(?P<etq>[^>]*))?>')
RX_SESION = re.compile(r'[Ss]esi[\u00f3o]n\s*(\d{1,2})\b')


def grabaciones(archivo):
    """Saca los enlaces de grabaci\u00f3n de los mensajes y los amarra a su sesi\u00f3n.

    Primero por el n\u00famero de sesi\u00f3n escrito en el mensaje; si no aparece,
    por la fecha m\u00e1s cercana dentro de dos d\u00edas.
    """
    total = con_acta = 0
    for c in archivo['canales']:
        vistas, lista = set(), []
        for m in c['mensajes']:
            if m['sistema']:
                continue
            for g in RX_VIDEO.finditer(m['texto']):
                url = g.group('url')
                # el mismo video aparece con distintos par\u00e1metros: la identidad
                # est\u00e1 en la ruta del documento, no en la cadena completa
                clave = url.split('?')[0]
                if clave in vistas:
                    continue
                vistas.add(clave)
                ses = RX_SESION.search(m['texto'])
                etq = (g.group('etq') or '').strip()
                lista.append({
                    'url': url,
                    'fecha': m['fecha'],
                    'sesion': int(ses.group(1)) if ses else None,
                    'titulo': etq if etq and not etq.startswith('netorg') else '',
                    'acta': None,
                })
        # amarrar a las actas del canal
        por_num = {a['sesion_num']: a for a in c['actas'] if a.get('sesion_num') is not None}
        for g in lista:
            a = por_num.get(g['sesion'])
            if a is None:
                cerca = sorted(c['actas'],
                               key=lambda x: abs((date(*map(int, x['iso'].split('-')))
                                                  - date(*map(int, g['fecha'].split('-')))).days))
                if cerca and abs((date(*map(int, cerca[0]['iso'].split('-')))
                                  - date(*map(int, g['fecha'].split('-')))).days) <= 2:
                    a = cerca[0]
            if a is not None:
                g['acta'] = a['archivo']
                g['sesion'] = a['sesion_num']
                a['grabacion'] = g['url']
                con_acta += 1
        lista.sort(key=lambda g: g['fecha'])
        c['grabaciones'] = lista
        total += len(lista)
    archivo['n_grabaciones'] = total
    print('  %d grabaciones \u00b7 %d amarradas a su acta' % (total, con_acta))



def pdfs(archivo):
    """Cada acta apunta al PDF que se publica junto a la p\u00e1gina."""
    mapa = json.load(open(os.path.join(AQUI, 'datos', 'pdf-mapa.json'), encoding='utf-8'))
    n = 0
    for c in archivo['canales']:
        for a in c['actas']:
            pdf = mapa.get(a['archivo'])
            if pdf:
                a['pdf'] = 'actas/' + pdf
                n += 1
    print('  %d actas con PDF publicado' % n)


def asistencia(archivo):
    """Qui\u00e9n asisti\u00f3 a qu\u00e9.

    Los informes de asistencia de Teams, bajados de Dropbox, son la fuente:
    traen entrada, salida y minutos reales. Las actas quedan de respaldo para
    las sesiones que no tienen informe.
    """
    ruta = os.path.join(AQUI, 'datos', 'asistencia-teams.json')
    if os.path.exists(ruta):
        t = json.load(open(ruta, encoding='utf-8'))
        archivo['asistencia'] = t['personas']
        archivo['mentoria'] = t['mentoria']
        archivo['sesiones_informe'] = t['sesiones']
        # amarrar el informe a su acta, por canal y fecha
        por_fecha = {(s['canal'], s['fecha']): s for s in t['sesiones']}
        n = 0
        for c in archivo['canales']:
            c['informes'] = [s for s in t['sesiones'] if s['canal'] == c['canal']]
            for a in c['actas']:
                inf = por_fecha.get((c['canal'], a['iso']))
                if inf:
                    a['informe'] = {'duracion_min': inf['duracion_min'],
                                    'media_min': inf['media_min'],
                                    'participantes': inf['participantes']}
                    n += 1
        print('  %d personas \u00b7 %d participaciones \u00b7 %d sesiones con informe '
              '\u00b7 %d actas con asistencia medida'
              % (len(t['personas']), sum(g['n'] for g in t['personas']),
                 len(t['sesiones']), n))
        return
    _asistencia_de_actas(archivo)


def _asistencia_de_actas(archivo):
    """Respaldo: la asistencia sacada de los participantes de cada acta."""
    gente = {}
    for c in archivo['canales']:
        for a in c['actas']:
            for pa in (a.get('participantes') or []):
                nombre = pa.get('nombre') if isinstance(pa, dict) else str(pa)
                if not nombre:
                    continue
                clave = nombre.strip()
                g = gente.setdefault(clave, {
                    'nombre': clave,
                    'cargo': (pa.get('cargo') or '') if isinstance(pa, dict) else '',
                    'correo': (pa.get('correo') or '') if isinstance(pa, dict) else '',
                    'nivel': (pa.get('nivel') or '') if isinstance(pa, dict) else '',
                    'sesiones': [], 'canales': [],
                })
                if isinstance(pa, dict):
                    if pa.get('cargo') and not g['cargo']: g['cargo'] = pa['cargo']
                    if pa.get('correo') and pa['correo'] != '\u2014' and (not g['correo'] or g['correo'] == '\u2014'):
                        g['correo'] = pa['correo']
                    if pa.get('nivel'): g['nivel'] = pa['nivel']
                g['sesiones'].append({'canal': c['canal'], 'nombre_canal': c['nombre'],
                                      'sesion': a.get('sesion_num'), 'iso': a['iso'],
                                      'acta': a['archivo'],
                                      'modalidad': (pa.get('modalidad') or '') if isinstance(pa, dict) else ''})
                if c['canal'] not in g['canales']:
                    g['canales'].append(c['canal'])
    for g in gente.values():
        g['sesiones'].sort(key=lambda x: x['iso'], reverse=True)
        g['n'] = len(g['sesiones'])
    def es_mentoria(g):
        return 'mentora iam' in (g['cargo'] or '').lower()

    equipo = [g for g in gente.values() if not es_mentoria(g)]
    archivo['asistencia'] = sorted(equipo, key=lambda g: (-g['n'], g['nombre']))
    archivo['mentoria'] = sorted((g for g in gente.values() if es_mentoria(g)),
                                 key=lambda g: -g['n'])
    print('  %d personas del \u00e1rea \u00b7 %d participaciones \u00b7 %d de la mentor\u00eda'
          % (len(equipo), sum(g['n'] for g in equipo), len(archivo['mentoria'])))


def main():
    archivo = json.load(open(os.path.join(AQUI, 'datos', 'archivo.json'), encoding='utf-8'))
    actas = cargar_actas()
    fijados = json.load(open(os.path.join(AQUI, 'fijados.json'), encoding='utf-8'))

    for c in archivo['canales']:
        c['nombre'] = NOMBRE.get(c['canal'], c['canal'])
        c['actas'] = actas.get(c['canal'], [])
        c['fijados'] = fijados.get('canales', {}).get(c['canal'], {}).get('carpetas', [])
    pdfs(archivo)
    grabaciones(archivo)
    asistencia(archivo)
    pulso(archivo)
    archivo['generales'] = fijados.get('generales', [])
    archivo['nota_fijados'] = fijados.get('nota', '')

    total_actas = sum(len(c['actas']) for c in archivo['canales'])
    destino = os.path.join(AQUI, 'app', 'datos.js')
    with open(destino, 'w', encoding='utf-8') as f:
        f.write('window.ARCHIVO=')
        json.dump(archivo, f, ensure_ascii=False, separators=(',', ':'))
        f.write(';\n')
    print('%d canales · %d mensajes · %d actas · %d adjuntos · %d personas'
          % (len(archivo['canales']),
             sum(c['conteo'] for c in archivo['canales']),
             total_actas,
             sum(c['adjuntos'] for c in archivo['canales']),
             len(archivo['personas'])))
    print('  %s  (%.0f KB)' % (destino, os.path.getsize(destino) / 1024))


if __name__ == '__main__':
    main()
