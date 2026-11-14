# -*- coding: utf-8 -*-
"""Genera la presentación de cierre de Comfacesar para la jornada ante la dirección.

Todo número que aparece en la presentación sale de aquí. El jueves a las 4 de la
tarde se actualizan las constantes de este archivo, se corre y se publica.

    python3 build-presentacion.py && validar

Fuentes de cada bloque:
  SESIONES   tablero de cierre, columna "Sesiones" · 119 en 18 áreas
  HORAS      Sala de Control recalculada el 13 de octubre · 187,8 h/semana
  PROCESOS   bloque en firme de la Sala de Control · 53 tareas medidas
  AGENTES    tablero de cierre, columna "Con qué cierra"
  FECHAS     fichas de sesión de Lucía · 90 de las 119 llevan acta fechada
"""
import json, re, sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SALIDA = RAIZ / "presentacion-cierre-comfacesar.html"

# ───────────────────────── datos del programa ─────────────────────────

PROGRAMA = {
    "sesiones": 119, "areas": 18, "colaboradores": 51, "convocados": 223,
    "asistieron": 203, "asistencia": 91, "caidas": 26,
    "horas": 250.0, "horas_medidas": 187.8, "nps": 20, "confianza": (4.7, 8.6),
    "respuestas_nps": 20, "fichas_fechadas": 90,
    "semanas": 11, "inicio": "11 de agosto", "cierre": "9 de octubre",
}

# La fecha de la jornada ante la dirección. El 4 de noviembre Comfacesar aplazó
# la del viernes 6 sin dar fecha nueva, así que vive en una sola constante: en
# cuanto haya fecha se cambia aquí y se regenera toda la presentación.
#
#   JORNADA_FECHA   cómo se nombra en los titulares, p. ej. "viernes 6 de noviembre"
#   JORNADA_CORTA   la forma corta, p. ej. "viernes 6"
#   JORNADA_FIJADA  False mientras no haya fecha confirmada
JORNADA_FECHA = "martes 17 de noviembre, de 9:00 a 12:30"
JORNADA_CORTA = "martes 17"
JORNADA_FIJADA = True

# sesiones totales al cierre, del tablero de cierre
SESIONES = {
    "Jurídica": 13, "Comunicaciones": 12, "Servicios Sociales": 11,
    "Sub. Admin y Financiera": 11, "Subsidio y Aportes": 11, "Agencia de Empleo": 10,
    "Contabilidad": 8, "IPS": 6, "Tecnología": 6, "Vivienda": 6, "Educación": 5,
    "Mercadeo": 5, "Sub. Operativa": 4, "Talento Humano": 3, "Cumplimiento": 2,
    "Gerencia Financiera": 2, "Planeación": 2, "Tesorería": 2,
}

# Horas recuperadas por semana.
#
# La Sala de Control mide 187,8 h en 53 tareas en firme. Sandra fija el total real
# del programa en 250 h el 3 de noviembre: hay ejercicios que las áreas construyeron
# y no registraron, y ella los conoce por haber estado en las sesiones.
#
# Para que el total y el desglose por área cuadren en la misma diapositiva, lo
# medido se lleva a ese total con un factor único. El reparto entre áreas conserva
# la proporción de lo medido, y así queda dicho en la fuente de la diapositiva.
MEDIDAS = {
    "Sub. Admin y Financiera": 45.7, "Vivienda": 38.4, "Jurídica": 23.6,
    "Subsidio y Aportes": 23.0, "IPS": 22.8, "Comunicaciones": 13.7,
    "Servicios Sociales": 10.9, "Agencia de Empleo": 4.4, "Contabilidad": 2.4,
    "Sub. Operativa": 2.4, "Educación": 0.4, "Cumplimiento": 0.1,
}
# Educación va con una cifra fijada por la mentoría, no con su proporción
# medida. Sandra la estableció el 14 de noviembre: el área recuperó bastante más
# de lo que alcanzó a registrar, y lo único que quedó anotado es una tarea de
# 120 minutos. Su cifra se fija primero y el resto del total se reparte entre
# las demás áreas conservando la proporción que sí midieron, de modo que el
# total que se presenta no cambia.
FIJADAS = {"Educación": 25}

_resto = PROGRAMA["horas"] - sum(FIJADAS.values())
_medidas_resto = {a: h for a, h in MEDIDAS.items() if a not in FIJADAS}
FACTOR = _resto / sum(_medidas_resto.values())
CRUDAS = {a: h * FACTOR for a, h in _medidas_resto.items()}
CRUDAS.update({a: float(h) for a, h in FIJADAS.items()})

# Las horas se presentan en enteros. Redondear cada una por separado deja la
# suma en 249 o en 251, así que se reparte por resto mayor: cada área se lleva
# su parte entera y los puntos que sobran van a las de mayor fracción. Así el
# desglose suma exactamente el total que se presenta.
_piso = {a: int(h) for a, h in CRUDAS.items()}
_sobran = int(round(PROGRAMA["horas"] - sum(_piso.values())))
_cola = sorted(CRUDAS, key=lambda a: CRUDAS[a] - _piso[a], reverse=True)
HORAS = dict(_piso)
for a in _cola[:_sobran]:
    HORAS[a] += 1
assert sum(HORAS.values()) == PROGRAMA["horas"], sum(HORAS.values())

# procesos documentados en firme
PROCESOS = {
    "Jurídica": 11, "Servicios Sociales": 8, "Vivienda": 6, "Comunicaciones": 6,
    "Subsidio y Aportes": 5, "Agencia de Empleo": 4, "Sub. Admin y Financiera": 4,
    "Sub. Operativa": 3, "Contabilidad": 3, "Tecnología": 2, "Educación": 2,
    "IPS": 1, "Mercadeo": 1, "Cumplimiento": 1, "Talento Humano": 1,
}

# agentes, de la columna "Con qué cierra"
AGENTES = {
    "Jurídica": (4, 2), "Comunicaciones": (3, 0), "Servicios Sociales": (2, 1),
    "Agencia de Empleo": (1, 1), "IPS": (1, 1), "Tecnología": (1, 0),
    "Sub. Operativa": (1, 0),
}

# qué cierra cada área, del tablero de cierre
CIERRA = {
    "Jurídica": "Cuatro agentes, dos corriendo con el equipo en Slack",
    "Comunicaciones": "Tres agentes construidos",
    "Servicios Sociales": "Dos agentes, uno detectó errores de origen en los datos",
    "Sub. Admin y Financiera": "Tablero de la agenda directiva y el portal precontractual",
    "Subsidio y Aportes": "Circuito completo probado de principio a fin",
    "Agencia de Empleo": "Matías en producción, con su primera respuesta a un ciudadano",
    "Contabilidad": "Repuso la sesión caída y tomó una más",
    "IPS": "Circuito de inspecciones corriendo sobre 23 sedes",
    "Tecnología": "Primer agente programado por el área",
    "Vivienda": "Tablero del programa de mejoramiento rural",
    "Educación": "Dos tableros publicados y su primera cifra medida",
    "Mercadeo": "Primer tablero interactivo",
    "Sub. Operativa": "Retomada tras la caída del 9 de septiembre",
    "Talento Humano": "Las tres personas con ejercicio propio",
    "Cumplimiento": "La S2 se cayó tres veces y se recuperó el 22 de septiembre",
    "Gerencia Financiera": "Quedó sin la tercera sesión",
    "Planeación": "La primera habilidad construida del programa",
    "Tesorería": "Bloqueada: sus títulos siguen en papel",
}

# Tarifas de costo hora de Comfacesar. NO se publican: son dato sensible y
# Sandra pidió el 4 de noviembre que no aparezcan en la presentación.
# Quedan aquí para que la cifra sea trazable, y el generador comprueba que
# ninguna se cuele en el HTML.
TARIFAS = [("Profesional", 36351, "Base del reporte"),
           ("Gerente o jefe", 62862, ""),
           ("Directivo", 95941, "")]

# Un proceso no lo ejecuta un solo perfil: hay profesionales que lo hacen y
# jefes que lo revisan. La valoración usa el promedio de esos dos, no el de
# todos, porque el perfil directivo no ejecuta tareas.
TARIFA_MEZCLA = (TARIFAS[0][1] + TARIFAS[1][1]) / 2

# el orden de la jornada, fijado por Sandra
JORNADA = [
    ("IPS", "IPS", "La plataforma de capacitaciones, de la firma al certificado"),
    ("Jurídica", "JU", "Cuatro agentes, dos corriendo sobre el correo real"),
    ("Sub. Admin y Financiera", "SF", "La prevalidación precontractual y la agenda directiva"),
    ("Contabilidad", "CO", "El circuito de conciliaciones probado de punta a punta"),
    ("Agencia de Empleo", "AE", "Matías respondiendo a un ciudadano"),
    ("Vivienda", "VI", "El tablero del mejoramiento rural y el análisis de interventorías"),
    ("Subsidio y Aportes", "SA", "Cinco agentes, y Afilia contestando afiliaciones sola"),
    ("Comunicaciones", "CM", "Tres agentes y el libreto de evento usado en vivo"),
    ("Sub. Operativa", "SO", "Maia, el primer agente del área"),
    ("Educación", "ED", "Dos tableros publicados y su primera cifra medida"),
]
# Minutos por área. La jornada se redujo a 3 horas y media, y Servicios Sociales
# se cayó el 14 de noviembre porque Juan Pablo está incapacitado, así que quedan
# diez áreas. Servicios Sociales sigue en el resto del programa: solo sale de
# la jornada.
JORNADA_INICIO = 9 * 60 + 15        # tras quince minutos de introducción
JORNADA_CIERRE = 13                 # los minutos que dejó Servicios Sociales al caerse
# IPS abre con media hora, que fue decisión de Sandra el 14 de noviembre. Los
# diez minutos extra salieron de su bloque de cierre, y los 13 que dejó
# Servicios Sociales se lo devuelven con tres de más.
MINUTOS = {
    'IPS': 30,
    'Jurídica': 20,
    'Sub. Admin y Financiera': 20,
    'Contabilidad': 20,
    'Agencia de Empleo': 20,
    'Vivienda': 20,
    'Subsidio y Aportes': 13,
    'Comunicaciones': 13,
    'Sub. Operativa': 13,
    'Educación': 13,
}
JORNADA_INTRO = JORNADA_INICIO - 9 * 60   # lo que Sandra abre, antes de la primera área
assert sum(MINUTOS.values()) + JORNADA_INTRO + JORNADA_CIERRE == 210, sum(MINUTOS.values())


def horario():
    """Hora de inicio y fin de cada área, en el orden de la jornada."""
    t = JORNADA_INICIO
    for a, _, _ in JORNADA:
        m = MINUTOS[a]
        yield a, f"{t // 60}:{t % 60:02d}", f"{(t + m) // 60}:{(t + m) % 60:02d}", m
        t += m


# Quién presenta por cada área, en forma corta, que es la que cabe en la columna
# de la diapositiva. Los nombres completos están en el mensaje a María Elvira,
# whatsapp-maria-elvira-quien-presenta.md, cruzados contra Slack.
PRESENTA = {
    "Agencia de Empleo": "Lina Rincón y José Jaime Maya",
    "IPS": "Danilo Pozo y equipo",
    "Vivienda": "Cindy Silva",
    "Contabilidad": "Carlos Lozano",
    "Sub. Admin y Financiera": "Rafael Solano",
    "Educación": "Óscar Cotes y Julissa Pérez",
    "Jurídica": "Gamarra, Laino y Costa",
    "Subsidio y Aportes": "Cindy Rodríguez",
    "Comunicaciones": "por confirmar",
    "Sub. Operativa": "Jennifer",
}

INDICACIONES = [
    ("El flujo de trabajo", "Cómo lo hacían antes y cómo lo hacen ahora. Una o dos diapositivas."),
    ("El tiempo, y su destino", "Cuánto tardaba el proceso, cuánto tarda hoy, y en qué se está usando esa hora que volvió."),
    ("El inventario de lo que falta", "Lo que quedó por hacer, o lo que el área quisiera en una segunda fase."),
    ("La hiperconectividad", "Qué necesitaría el área para quedar conectada a los sistemas de información."),
]

# Fase 2, enunciada y no vendida. Decisión de Sandra del 3 de noviembre: esta es
# una presentación de cierre de proyecto, así que la fase 2 entra como inventario
# de hacia dónde va, sin detalle, sin cifras y sin pedirle una decisión a nadie.
# El lenguaje es el de la propuesta, propuesta-fase2-comfacesar.html.
ENUNCIADO = [
    ("Hiperconectividad", [
        "Saber qué sistemas de información hay y dónde está alojado cada uno",
        "Los tableros enganchados a la gestión, en vez de alimentados a mano",
        "La información fuera de la red local, y un solo lugar donde trabaja la Caja",
    ]),
    ("Hardware", [
        "La forma de trabajo que las áreas ya adoptaron no cabe en un equipo de escritorio",
        "Un sistema de computación portátil, con rotación de puestos y esquema híbrido",
        "Los equipos que hoy son el límite, levantados y priorizados",
    ]),
]

# Los doce bloques de la fase 2 con su rango de meses, tal como están en la
# propuesta. Es el cronograma que Sandra quiere al final: qué se hace y cuándo,
# sin precio y sin pedir una decisión.
CRONOGRAMA = [
    ('Inventario de sistemas: qué hay y dónde', 1, 1),
    ('Levantamiento de equipos', 1, 1),
    ('Cuántas licencias de Claude y para quién', 1, 1),
    ('IAM™ Hello, un solo lugar de trabajo', 1, 3),
    ('Cimentar lo que las áreas ya construyeron', 1, 4),
    ('El Tableau que ya está pagado', 1, 5),
    ('Volver a Vivienda y Mercadeo', 1, 6),
    ('Licencias de Claude y Office, que está viejo', 2, 4),
    ('Gobernanza, con Cumplimiento', 2, 7),
    ('IAM™ Commercial en Mercadeo', 2, 9),
    ('Digitalización y cultura de no papel', 2, 9),
    ('Tableros enganchados a la gestión', 3, 10),
    ('Salir de la red local', 5, 12),
]
assert len(CRONOGRAMA) == 13, len(CRONOGRAMA)
assert all(1 <= a <= b <= 12 for _, a, b in CRONOGRAMA)

# El detalle de los seis frentes y el año trimestre por trimestre quedan aquí,
# fuera de la presentación de cierre. Son material de la propuesta, no del cierre.
FRENTES = [
    ("Saber qué hay y dónde está",
     "El inventario de los sistemas de información de la Caja y dónde está alojado cada uno. Sin ese mapa no se conecta nada."),
    ("Un solo lugar donde trabaja la Caja",
     "IAM™ Hello: la puerta única por la que cada área entra a lo suyo, en vez de dieciocho entradas distintas."),
    ("El Tableau que ya está pagado",
     "Lleva ocho años comprado y subutilizado porque nadie lo alimenta. Es el activo más barato de activar."),
    ("Los tableros enganchados a la gestión",
     "Que el tablero del área lea del sistema en vez de que alguien le copie los datos a mano cada semana."),
    ("Salir de la red local",
     "Hoy la información vive en equipos y carpetas locales. Mientras siga ahí, no se puede conectar ni respaldar."),
    ("Una app de la Caja, por áreas",
     "Arranca por áreas y después se unen, el mismo camino que ya recorrieron los tableros."),
]

# el año, trimestre por trimestre, de la propuesta. Sin un solo peso.
TRIMESTRES = [
    ("Trimestre 1", "Meses 1 a 3", "Levantar y cerrar lo abierto", [
        "Levantamiento de equipos, con la lista priorizada de qué computadores se cambian y por qué",
        "Levantamiento de sistemas: qué hay y dónde está alojado cada uno",
        "Cimentación de los circuitos de las áreas que ya construyeron",
        "Primeras sesiones de trabajo cercano con Vivienda y Mercadeo",
        "Arranca la gobernanza con Cumplimiento y se gestiona la reunión de licenciamiento",
        "Diseño del plan de equipos portátiles, con Talento Humano",
    ]),
    ("Trimestre 2", "Meses 4 a 6", "Decidir y conectar", [
        "La propuesta de licenciamiento queda lista y el sponsor la presenta al director",
        "El plan de renovación de equipos entra en ejecución con lo que la dirección apruebe",
        "Primeras conexiones de tableros a los sistemas internos, con el recurso de la Caja",
        "Automatizaciones vivas en Vivienda, y Mercadeo con su base de datos conectada",
        "Entran las primeras áreas por activar, con circuito nuevo de principio a fin",
        "Arranca el esquema híbrido en las áreas que ya tengan portátil",
    ]),
    ("Trimestre 3", "Meses 7 a 9", "Infraestructura y reglas", [
        "Evaluación y selección del proveedor de migración a la nube",
        "Negociación del techo de integración con el proveedor de software",
        "El marco de gobernanza queda publicado y con responsable con nombre",
        "Mercadeo y Subsidio con los tableros hablándose",
        "Las áreas por activar, en construcción",
        "Primera medición de productividad del esquema híbrido",
    ]),
    ("Trimestre 4", "Meses 10 a 12", "Dejarlo andando sin la mentoría", [
        "Acompañamiento de la migración a la nube que ejecuta el proveedor",
        "Las 18 áreas con al menos un circuito cimentado y medido",
        "Traspaso formal al recurso interno que la Caja designe",
        "Balance del año en horas y en pesos, no en porcentaje de avance",
        "Cierre: cuarta revisión con el director y entrega",
    ]),
]

# lo que el cierre no resolvió, del tablero de cierre
ABIERTO = [
    ("Cada circuito vive en la cabeza de quien lo armó",
     "Si la persona sale, el proceso se va con ella. No hay respaldo ni documentación de operación."),
    ("Medir en dinero todavía no es costumbre",
     "Seis áreas de dieciocho no midieron ni una tarea. No es que no hicieran: es que no lo anotaron."),
    ("Dieciocho islas que no se hablan",
     "Cada área construyó lo suyo. Ningún tablero lee de otro ni de un sistema de la Caja."),
    ("Los equipos no dan para la forma de trabajo que se pide",
     "El hardware es hoy el límite, y el director lo viene diciendo desde el 14 de septiembre."),
]


# ───────────────────────── el índice (IIE) ─────────────────────────

UMBRALES = {"adopcion": 10, "produccion": 8, "impacto": 20.0}


def cargar_fechas():
    """Fechas de sesión por área, de las fichas de Lucía."""
    f = RAIZ / "fechas-sesiones.json"
    if not f.exists():
        sys.exit("falta fechas-sesiones.json: córrelo con extraer-fechas.sh")
    crudo = json.loads(f.read_text(encoding="utf-8"))
    d = defaultdict(list)
    for r in crudo:
        d[r["area"]].append(r["fecha"])
    return d


def ejes(ses, proc, horas, ag):
    construidos, corriendo = ag
    return {
        "adopcion": min(ses / UMBRALES["adopcion"], 1) * 25,
        "produccion": min(proc / UMBRALES["produccion"], 1) * 25,
        "impacto": min(horas / UMBRALES["impacto"], 1) * 25,
        "autonomia": min(construidos * 4 + corriendo * 8.5, 25.0),
    }


def iie(area, fechas, hasta=None):
    todas = fechas.get(area, [])
    if hasta is None:
        ses, esc = SESIONES[area], 1.0
    else:
        ses = sum(1 for f in todas if f <= hasta)
        esc = (ses / len(todas)) if todas else 0.0
        ses = round(SESIONES[area] * esc)
    proc = round(PROCESOS.get(area, 0) * esc)
    horas = HORAS.get(area, 0.0) * esc
    c, r = AGENTES.get(area, (0, 0))
    ag = (int(c * esc), int(r * esc))
    e = ejes(ses, proc, horas, ag)
    return {"area": area, "sesiones": ses, "procesos": proc, "horas": round(horas, 1),
            "agentes": ag[0], "corriendo": ag[1],
            "ejes": {k: round(v, 1) for k, v in e.items()},
            "iie": round(sum(e.values()), 1)}


# ─────────────── Las 53 tareas que computan, de la Sala de Control ───────────────
#
# Extraídas del tablero publicado de Lucía, de la tabla «Las cincuenta y tres
# tareas que computan, con su frecuencia». Son las filas verificadas: las
# estimadas y las de suma quedaron fuera. Es la base medida del programa, y las
# 250 horas de la presentación son esta medición proyectada para incluir lo que
# las áreas construyeron sin registrar.
import json as _json
import re as _re
import pathlib as _pl

TAREAS = _json.loads(
    (_pl.Path(__file__).parent / "tareas-sala-control.json").read_text("utf-8"))

# El tablero de Lucía abrevia un área. Se normaliza al nombre que usa el resto
# del programa, y se comprueba que no quede ninguna otra sin correspondencia.
_ALIAS = {"Subsidio": "Subsidio y Aportes"}
for _t in TAREAS:
    _t["area"] = _ALIAS.get(_t["area"], _t["area"])
_huerfanas = {_t["area"] for _t in TAREAS} - set(SESIONES)
assert not _huerfanas, _huerfanas

VUELTA_ANTES = sum(t["antes_min"] for t in TAREAS)
VUELTA_HOY = sum(t["ahora_min"] for t in TAREAS)

# Si alguno de estos números se mueve, es que el tablero cambió y hay que
# volver a extraer: la presentación no debe inventarse una base propia.
assert len(TAREAS) == 53, len(TAREAS)
assert (VUELTA_ANTES, VUELTA_HOY) == (22374, 2308), (VUELTA_ANTES, VUELTA_HOY)


def _min_sem(t):
    """Minutos recuperados por semana de una tarea. Las que el tablero dejó en
    «por confirmar» no suman: no se rellenan con una suposición."""
    m = _re.match(r"([\d.]+) min", t["ahorro_semanal"])
    return int(m.group(1).replace(".", "")) if m else 0


def por_area():
    """El tablero de ejercicios agrupado por área, de mayor a menor recuperación."""
    ag = {}
    for t in TAREAS:
        a = ag.setdefault(t["area"], {"tareas": 0, "antes": 0, "hoy": 0, "min_sem": 0})
        a["tareas"] += 1
        a["antes"] += t["antes_min"]
        a["hoy"] += t["ahora_min"]
        a["min_sem"] += _min_sem(t)
    return sorted(ag.items(), key=lambda x: -x[1]["min_sem"])


assert round(sum(v["min_sem"] for _, v in por_area()) / 60, 1) == PROGRAMA["horas_medidas"]


def construir_datos():
    fechas = cargar_fechas()
    cierre = {a: iie(a, fechas) for a in SESIONES}
    sept = {a: iie(a, fechas, "2026-09-30") for a in SESIONES}
    orden = sorted(SESIONES, key=lambda a: -cierre[a]["iie"])
    return {
        "programa": PROGRAMA, "umbrales": UMBRALES, "orden": orden,
        "cierre": cierre, "septiembre": sept, "cierra": CIERRA,
        "horas": HORAS, "jornada": JORNADA, "presenta": PRESENTA,
        "promedio": {
            "cierre": round(sum(cierre[a]["iie"] for a in SESIONES) / len(SESIONES), 1),
            "septiembre": round(sum(sept[a]["iie"] for a in SESIONES) / len(SESIONES), 1),
        },
    }


if __name__ == "__main__":
    d = construir_datos()
    print(f"{'ÁREA':26}{'IIE':>7}{'sep':>7}{'Δ':>7}")
    for a in d["orden"]:
        c, s = d["cierre"][a]["iie"], d["septiembre"][a]["iie"]
        print(f"{a:26}{c:>7.1f}{s:>7.1f}{c - s:>+7.1f}")
    print(f"\npromedio: {d['promedio']['septiembre']} → {d['promedio']['cierre']}")
    print(f"horas: {sum(HORAS.values()):.1f} · sesiones: {sum(SESIONES.values())}")
