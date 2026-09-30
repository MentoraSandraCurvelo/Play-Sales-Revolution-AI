# -*- coding: utf-8 -*-
"""Arma app/datos.js: mensajes + actas + fijados en un solo paquete."""
import json, os, glob, re

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


def main():
    archivo = json.load(open(os.path.join(AQUI, 'datos', 'archivo.json'), encoding='utf-8'))
    actas = cargar_actas()
    fijados = json.load(open(os.path.join(AQUI, 'fijados.json'), encoding='utf-8'))

    for c in archivo['canales']:
        c['nombre'] = NOMBRE.get(c['canal'], c['canal'])
        c['actas'] = actas.get(c['canal'], [])
        c['fijados'] = fijados.get('canales', {}).get(c['canal'], {}).get('carpetas', [])
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
