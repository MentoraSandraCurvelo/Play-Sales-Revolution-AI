#!/usr/bin/env python3
"""Rescata las lecturas de canales de Slack: de los archivos que el conector
dejó en disco y del propio registro de la sesión, y las guarda por canal."""
import json, re, sys, glob, os

DEST = os.path.join(os.path.dirname(__file__), 'raw')
os.makedirs(DEST, exist_ok=True)

def guardar(texto):
    m = re.search(r'Channel: #([^\s(]+) \(([A-Z0-9]+)\)', texto)
    if not m: return None
    nombre, cid = m.group(1), m.group(2)
    ruta = os.path.join(DEST, f'{nombre}.json')
    if os.path.exists(ruta) and len(open(ruta, encoding='utf-8').read()) >= len(texto):
        return None
    open(ruta, 'w', encoding='utf-8').write(texto)
    return nombre

vistos = []

# 1. los .txt que dejó el conector cuando la respuesta no cupo
for f in glob.glob('/root/.claude/projects/-home-user-Play-Sales-Revolution-AI/*/tool-results/mcp-Slack-slack_read_channel-*.txt'):
    n = guardar(open(f, encoding='utf-8').read())
    if n: vistos.append((n, 'archivo'))

# 2. el registro de la sesión, para las respuestas que sí cupieron
for jl in glob.glob('/root/.claude/projects/-home-user-Play-Sales-Revolution-AI/*.jsonl'):
    for linea in open(jl, encoding='utf-8'):
        if 'Channel: #' not in linea: continue
        try: obj = json.loads(linea)
        except Exception: continue
        pila = [obj]
        while pila:
            x = pila.pop()
            if isinstance(x, dict): pila.extend(x.values())
            elif isinstance(x, list): pila.extend(x)
            elif isinstance(x, str) and x.startswith('{"messages":"Channel: #'):
                n = guardar(x)
                if n: vistos.append((n, 'registro'))

for n, o in sorted(set(vistos)): print(f'  {n:38} ({o})')
print(f'\ncanales guardados: {len(set(n for n,_ in vistos))}')
