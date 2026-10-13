# -*- coding: utf-8 -*-
"""Escribe filas de tarea en el .xlsx sin pasar por openpyxl.

openpyxl rehace el archivo y se lleva por delante los 23 dibujos que el tablero
trae en cada hoja. Esto edita el XML de la hoja y deja todo lo demas intacto.
"""
import re, sys, html

def esc(t):
    return html.escape(str(t), quote=True).replace('\n', '&#10;')

def celda(ref, s, clase, valor):
    if clase == 's':
        return f'<c r="{ref}" s="{s}" t="inlineStr"><is><t xml:space="preserve">{esc(valor)}</t></is></c>'
    if clase == 'n':
        return f'<c r="{ref}" s="{s}"><v>{valor}</v></c>'
    if clase == 'f':
        return f'<c r="{ref}" s="{s}"><f>{esc(valor)}</f></c>'
    return f'<c r="{ref}" s="{s}"/>'

def escribir_fila(x, fila, cols, alto=None):
    """cols: {'B': ('s','texto', estilo_o_None), ...}  estilo None = conserva el que ya tiene."""
    m = re.search(r'<row r="%d"(?P<attrs>[^>]*)>(?P<cuerpo>.*?)</row>' % fila, x, re.S)
    if not m:
        raise SystemExit('no encuentro la fila %d' % fila)
    attrs, cuerpo = m.group('attrs'), m.group('cuerpo')

    # estilo actual de cada celda de la fila
    est = dict(re.findall(r'<c r="([A-Z]+)%d" s="(\d+)"' % fila, cuerpo))

    nuevas = {}
    for col, (clase, valor, s_forzado) in cols.items():
        s = s_forzado if s_forzado is not None else est.get(col, '0')
        nuevas[col] = celda(f'{col}{fila}', s, clase, valor)

    # sustituye o inserta, manteniendo el orden de columnas
    # una celda es <c .../> o <c ...>...</c>; el no-avido hasta el primer '/>'
    # partia por la mitad las celdas con <f .../> dentro y rompia el XML
    trozos = re.findall(r'<c\b[^>]*/>|<c\b[^>]*>.*?</c>', cuerpo, re.S)
    sal, puestas = [], set()
    for t in trozos:
        col = re.match(r'<c r="([A-Z]+)', t).group(1)
        if col in nuevas:
            sal.append(nuevas[col]); puestas.add(col)
        else:
            # quita el valor cacheado de las formulas compartidas para que recalculen
            sal.append(re.sub(r'<v>[^<]*</v>', '', t))
    for col in sorted(set(nuevas) - puestas):
        pos = next((i for i, t in enumerate(sal)
                    if re.match(r'<c r="([A-Z]+)', t).group(1) > col), len(sal))
        sal.insert(pos, nuevas[col])

    nattrs = attrs
    if alto is not None:
        # con \s* el patron tambien casaba dentro de customHeight y dejaba 'customHeig'
        nattrs = re.sub(r'\s+ht="[^"]*"', '', nattrs)
        nattrs = re.sub(r'\s*customHeight="[^"]*"', '', nattrs)
        nattrs += f' ht="{alto}" customHeight="1"'
    return x[:m.start()] + f'<row r="{fila}"{nattrs}>' + ''.join(sal) + '</row>' + x[m.end():]

def cambiar_formula(x, ref, nueva):
    m = re.search(r'<c r="%s"([^>]*)>(.*?)</c>' % ref, x, re.S)
    if not m: raise SystemExit('no encuentro '+ref)
    return x[:m.start()] + f'<c r="{ref}"{m.group(1)}><f>{esc(nueva)}</f></c>' + x[m.end():]
