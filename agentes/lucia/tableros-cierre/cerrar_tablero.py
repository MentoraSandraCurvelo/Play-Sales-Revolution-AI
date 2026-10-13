# -*- coding: utf-8 -*-
"""Cierre del tablero de assessment · 13 de octubre de 2026

Dos cosas distintas:

1. Las cinco filas que salieron de las actas el 9 de octubre, que nunca llegaron
   al archivo de Drive porque la version quedo sin subir.
2. Las filas que las propias areas escribieron fuera del rango del resumen y por
   eso no se estaban contando: Vivienda y Comunicaciones.

Las hojas se resuelven por nombre. El orden de los sheetN.xml cambia cada vez que
alguien edita desde Sheets.
"""
import re, sys, xml.etree.ElementTree as ET
sys.path.insert(0, '.')
from patch_tablero import escribir_fila, cambiar_formula

def leer(p): return open(p, encoding='utf-8').read()
def guardar(p, x):
    ET.fromstring(x)
    open(p, 'w', encoding='utf-8').write(x)

def mapa_hojas():
    w, r = leer('xl/workbook.xml'), leer('xl/_rels/workbook.xml.rels')
    rel = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="(worksheets/sheet\d+\.xml)"', r))
    return {m.group(1): 'xl/' + rel[m.group(2)]
            for m in re.finditer(r'<sheet [^>]*name="([^"]+)"[^>]*r:id="(rId\d+)"', w)}

HOJA = mapa_hojas()

def resumen(hoja):
    """Devuelve (fila_resumen, primera, ultima) leyendo el COUNTA de la hoja."""
    x = leer(HOJA[hoja])
    m = re.search(r'<c r="B(\d+)"[^>]*><f>COUNTA\(B(\d+):B(\d+)\)</f>', x)
    if not m: raise SystemExit('no encuentro el COUNTA de ' + hoja)
    return int(m.group(1)), int(m.group(2)), int(m.group(3))

def ampliar(hoja, hasta):
    """Lleva el rango del resumen hasta la fila `hasta`, sin mover nada mas."""
    fr, ini, fin = resumen(hoja)
    if fin >= hasta:
        print(f'  {hoja}: el rango ya llega a la {fin}, no se toca'); return
    p = HOJA[hoja]; x = leer(p)
    for col, plantilla in [('B', 'COUNTA(B{i}:B{h})'),
                           ('D', 'IFERROR(SUM(D{i}:D{h})/60,0)'),
                           ('F', 'IFERROR(SUM(F{i}:F{h})/60,0)'),
                           ('H', 'IFERROR((SUM(D{i}:D{h})-SUM(F{i}:F{h}))/60,0)')]:
        x = cambiar_formula(x, f'{col}{fr}', plantilla.format(i=ini, h=hasta))
    guardar(p, x)
    print(f'  {hoja}: resumen de B{ini}:B{fin} a B{ini}:B{hasta}')

def fila(hoja, n, cols, alto):
    p = HOJA[hoja]; x = leer(p)
    x = escribir_fila(x, n, cols, alto=alto)
    guardar(p, x)
    print(f'  {hoja}!{n}')

F = 'Lo registró Lucía el 9 de octubre de 2026'
OBS = {
 'edu1': F+' a partir del acta de la Sesión 4 del 28 de septiembre de 2026, donde quedó medido en sesión sobre los datos reales del mes: antes dos horas, ahora diez minutos. Se conservaron las estructuras que debían conservarse, se incorporó la circular que rige el reporte a la Superintendencia y el valor consolidado cuadró. El área no lo había pasado al tablero. Si el tiempo no corresponde, el área lo corrige.',
 'edu2': F+' a partir del acta de la Sesión 5 del 8 de octubre de 2026. En la reunión de docentes cada uno metió los datos de su propia área y recibió de vuelta las acciones de mejora por grado. La cifra la puso el profesorado, no la mentoría: dijeron que les quitaba prácticamente cuatro días de trabajo, que son 1.920 minutos contando jornadas de ocho horas. Los dos tiempos quedan en blanco a propósito, porque lo que el profesorado declaró es el ahorro y no el antes ni el ahora, y el ejercicio en sesión no se cronometró. Con una frase del área esta fila queda con número.',
 'ips':  F+' a partir del acta de la Sesión 2 del 9 de septiembre de 2026. El área trajo la medición hecha por ellos mismos: lo que les tomaba dos meses salió en cinco minutos. Antes se revisaba caso por caso para identificar qué personal viene con recomendaciones, cuál genera alerta y a qué sistema de vigilancia pertenece. El acta pide expresamente registrarlo en el tablero del programa. Los minutos quedan en blanco porque el acta dice dos meses y no dice si son dos meses de calendario o de trabajo efectivo, y esa diferencia cambia la cifra por completo. Lo tiene que decir el área.',
 'sub':  F+' a partir del acta de la Sesión 3 del 8 de septiembre de 2026. Medición tomada en sesión: el archivo que devuelve la Registraduría se pasaba a Excel y se filtraba causal por causal a mano, con las anotaciones, y tomaba dos horas cada vez. Con el proceso montado queda en unos diez minutos y el resultado ya sale con la información necesaria para notificar. La frecuencia la tiene que poner el área: el acta dice cada vez que llega el archivo y no dice cada cuánto llega.',
 'jur':  F+' a partir del acta de la Sesión 11 del 24 de septiembre de 2026. Hacerla a mano toma una jornada de trabajo completa, 480 minutos. Se subió la presentación que la oficina viene usando desde hace años, se pidió actualizarla y salió en unos diez minutos, explicando además qué había cambiado. Se usó esa misma tarde en una reunión con varias áreas. Queda como Ocasional porque el acta no dice cada cuánto se presenta a los entes de control.',
}

print('Filas de las actas:')
fila('EDUCACION', 10, {
    'B': ('s', 'Consolidado mensual de subsidios de la Ley 115', None),
    'C': ('s', 'Mensual', '42'), 'D': ('n', 120, '43'), 'E': ('s', 'Claude', None),
    'F': ('n', 10, None), 'I': ('f', 'IFERROR(G10/60,"")', '36'),
    'J': ('s', OBS['edu1'], '37')}, 126)
fila('EDUCACION', 11, {
    'B': ('s', 'Acciones de mejora por grado a partir de la planilla de notas', None),
    'C': ('s', 'Ocasional', '42'), 'E': ('s', 'Claude', None),
    'I': ('f', 'IFERROR(G11/60,"")', '36'),
    'J': ('s', OBS['edu2'], '37')}, 165)
fila('IPS', 11, {
    'B': ('s', 'Conceptos de aptitud del examen médico ocupacional: recomendaciones, alertas y sistema de vigilancia', None),
    'C': ('s', 'Por confirmar', '42'), 'E': ('s', 'Claude', None),
    'I': ('f', 'IFERROR(G11/60,"")', '36'),
    'J': ('s', OBS['ips'], '37')}, 165)
fila('SUBSIDIO', 14, {
    'B': ('s', 'Cruce con la Registraduría: filtrado por causal y anotaciones', None),
    'C': ('s', 'Por confirmar', '42'), 'D': ('n', 120, '43'), 'E': ('s', 'Claude', None),
    'F': ('n', 10, None), 'I': ('f', 'IFERROR(G14/60,"")', '36'),
    'J': ('s', OBS['sub'], '37')}, 150)

# Juridica no tiene fila libre: su tabla son las 11 a 29 y estan las diecinueve.
# La 30 era una banda vacia combinada.
print('Jurídica, que tenía la tabla llena:')
p = HOJA['JURIDICA']; x = leer(p)
x = x.replace('<mergeCell ref="B30:J30"/>', '')
x = re.sub(r'(<mergeCells count=")(\d+)(")',
           lambda m: m.group(1) + str(int(m.group(2)) - 1) + m.group(3), x, count=1)
x = escribir_fila(x, 30, {
    'B': ('s', 'Presentación institucional de informes a entes de control', '29'),
    'C': ('s', 'Ocasional', '31'), 'D': ('n', 480, '32'), 'E': ('s', 'Claude', '33'),
    'F': ('n', 10, '34'),
    'G': ('f', 'IFERROR(D30-F30,"")', '35'),
    'H': ('f', 'IFERROR(IF(D30>0,(D30-F30)/D30,0),"")', '23'),
    'I': ('f', 'IFERROR(G30/60,"")', '36'),
    'J': ('s', OBS['jur'], '38')}, alto=145)
guardar(p, x); print('  JURIDICA!30')
ampliar('JURIDICA', 30)

print('Filas que las áreas escribieron y el resumen no contaba:')
ampliar('VIVIENDA', 18)        # su novena tarea, 120 a 15
ampliar('COMUNICACIONES', 22)  # su novena, 180 a 30, mas las cuatro filas que abrieron

p = 'xl/workbook.xml'; x = leer(p)
x = x.replace('<calcPr/>', '<calcPr calcId="191029" fullCalcOnLoad="1"/>')
guardar(p, x); print('workbook: recalcula al abrir')
