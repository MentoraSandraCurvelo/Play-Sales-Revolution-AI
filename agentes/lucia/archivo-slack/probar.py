# -*- coding: utf-8 -*-
"""Abre todas las vistas del entregable y avisa si alguna revienta.

Nace de un fallo real: un acta escrita a mano llevaba un campo como texto donde
la app esperaba una lista, y con eso **la app entera dejaba de verse** — no solo
esa acta. Se entregó tres veces sin detectarlo porque solo se probaba una vista.

    python3 probar.py                    sobre entregable/
    python3 probar.py otra/carpeta

No vale fiarse del código fuente: el HTML lleva dentro las librerías, y ahí
aparecen frases como «is not a function» que dan falso positivo. Por eso se mira
únicamente **el texto que se ve en pantalla**.
"""
import concurrent.futures as hilos
import json, os, re, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
CHROME = os.environ.get('CHROME_BIN', '/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
ROTO = re.compile(r'is not a function|renderVals\(\)|Cannot read propert')
MINIMO = 600   # una pestaña de fijados tiene ~950; por debajo de esto no hay vista


def visible(html, ruta):
    salida = subprocess.run(
        [CHROME, '--headless', '--disable-gpu', '--no-sandbox', '--enable-unsafe-swiftshader',
         '--virtual-time-budget=12000', '--dump-dom', 'file://' + html + ruta],
        capture_output=True, text=True, timeout=120).stdout
    cuerpo = re.search(r'<body[^>]*>(.*)</body>', salida, re.S)
    c = cuerpo.group(1) if cuerpo else ''
    c = re.sub(r'<script.*?</script>', '', c, flags=re.S)
    c = re.sub(r'<style.*?</style>', '', c, flags=re.S)
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', c)).strip()


def rutas(html):
    s = open(html, encoding='utf-8').read()
    i = s.index('window.ARCHIVO=')
    a = json.loads(s[s.index('{', i):s.rindex('}', i, s.index(';\n', i)) + 1])
    r = ['#/', '#/actas', '#/grabaciones', '#/asistencia', '#/personas', '#/archivos']
    for c in a['canales']:
        for p in ('mensajes', 'actas', 'grabaciones', 'fijados', 'archivos'):
            r.append('#/%s/%s' % (c['canal'], p))
        for acta in c['actas']:
            r.append('#/%s/actas/%s' % (c['canal'], acta['archivo']))
    return r


def main():
    carpeta = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, 'entregable')
    html = next(os.path.join(carpeta, f) for f in sorted(os.listdir(carpeta)) if f.endswith('.html'))
    todas = rutas(html)
    print('%s\n%d vistas por probar\n' % (html, len(todas)))

    def una(r):
        t = visible(html, r)
        if ROTO.search(t): return ('REVIENTA', r, len(t))
        if len(t) < MINIMO: return ('VACÍA', r, len(t))
        return ('ok', r, len(t))

    with hilos.ThreadPoolExecutor(max_workers=8) as ex:
        res = list(ex.map(una, todas))
    malas = [x for x in res if x[0] != 'ok']
    for estado, r, n in malas:
        print('  %-9s %-62s %d caracteres' % (estado, r, n))
    print('\n%d de %d correctas' % (len(res) - len(malas), len(res)))
    sys.exit(1 if malas else 0)


if __name__ == '__main__':
    main()
