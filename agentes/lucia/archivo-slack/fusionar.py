# -*- coding: utf-8 -*-
"""Mezcla las lecturas nuevas de Slack dentro de raw/<canal>.json.

extraer.py solo guarda cuando el texto nuevo es mas largo que el guardado,
y una lectura parcial (desde una fecha) siempre es mas corta. Esto parte
los dos textos en mensajes, los junta por marca de tiempo y vuelve a
escribir el canal entero en orden descendente, que es como lo deja Slack.
"""
import json, re, os, sys, glob

RAW = '/home/user/Play-Sales-Revolution-AI/agentes/lucia/archivo-slack/raw'
LOGS = '/root/.claude/projects/-home-user-Play-Sales-Revolution-AI'

CAB = re.compile(r'^Channel: #([^\s(]+) \(([A-Z0-9]+)\)')
TS = re.compile(r'^Message TS: ([0-9.]+)\s*$', re.M)


def partir(texto):
    """Devuelve (cabecera, {ts: bloque}) a partir del volcado de un canal."""
    trozos = re.split(r'(?m)^(?==== Message from )', texto)
    cab = trozos[0]
    por_ts = {}
    for t in trozos[1:]:
        m = TS.search(t)
        if m:
            por_ts[m.group(1)] = t.rstrip('\n')
    return cab, por_ts


def volcados():
    """Todo texto 'Channel: #...' que aparezca en el registro de la sesion."""
    vistos = []
    # Por antiguedad: cuando el mismo mensaje aparece en dos lecturas, manda la
    # ultima. Importa cuando Slack pierde un adjunto, porque la lectura nueva
    # trae el bloque con el archivo ya marcado como no disponible.
    for f in sorted(glob.glob(os.path.join(LOGS, '*', 'tool-results',
                                           'mcp-Slack-slack_read_channel-*.txt')),
                    key=os.path.getmtime):
        vistos.append(open(f, encoding='utf-8').read())
    for jl in glob.glob(os.path.join(LOGS, '*.jsonl')):
        for linea in open(jl, encoding='utf-8'):
            if 'Channel: #' not in linea:
                continue
            try:
                obj = json.loads(linea)
            except Exception:
                continue
            pila = [obj]
            while pila:
                x = pila.pop()
                if isinstance(x, dict):
                    pila.extend(x.values())
                elif isinstance(x, list):
                    pila.extend(x)
                elif isinstance(x, str) and x.startswith('{"messages":"Channel: #'):
                    try:
                        vistos.append(json.loads(x)['messages'])
                    except Exception:
                        pass
    return vistos


def main():
    nuevos = {}   # canal -> {ts: bloque}
    cabs = {}
    for texto in volcados():
        m = CAB.match(texto)
        if not m:
            continue
        canal = m.group(1)
        cab, por_ts = partir(texto)
        cabs.setdefault(canal, cab)
        nuevos.setdefault(canal, {}).update(por_ts)

    cambios = []
    for canal, bloques in sorted(nuevos.items()):
        ruta = os.path.join(RAW, canal + '.json')
        antes = {}
        cab = cabs[canal]
        if os.path.exists(ruta):
            d = json.load(open(ruta, encoding='utf-8'))
            cab0, antes = partir(d['messages'])
            cab = cab0 or cab
        total = dict(antes)
        total.update(bloques)
        añadidos = len(total) - len(antes)
        orden = sorted(total, key=lambda t: float(t), reverse=True)
        texto = cab.rstrip('\n') + '\n\n' + '\n\n'.join(total[t] for t in orden)
        json.dump({'messages': texto,
                   'pagination_info': 'There are no more messages available.\n'},
                  open(ruta, 'w', encoding='utf-8'), ensure_ascii=False)
        cambios.append((canal, len(antes), añadidos, len(total)))

    print('%-40s %6s %6s %6s' % ('canal', 'antes', 'nuevos', 'total'))
    for c, a, n, t in cambios:
        marca = '  <-- ' if n else ''
        print('%-40s %6d %6d %6d%s' % (c, a, n, t, marca))
    print('\ncanales tocados: %d · mensajes nuevos: %d'
          % (sum(1 for _, _, n, _ in cambios if n), sum(n for _, _, n, _ in cambios)))


main()
