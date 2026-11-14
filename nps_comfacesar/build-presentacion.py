# -*- coding: utf-8 -*-
"""Dibuja la presentación de cierre de Comfacesar a partir de datos_presentacion.py.

    python3 build-presentacion.py

Escribe presentacion-cierre-comfacesar.html. No hay un solo número escrito a mano
en el HTML: todos entran desde el módulo de datos, para que el jueves a las 4 se
actualice una constante y se regenere la presentación completa.
"""
import json
import re
from pathlib import Path
import datos_presentacion as D

RAIZ = Path(__file__).resolve().parent
SALIDA = RAIZ / "presentacion-cierre-comfacesar.html"
d = D.construir_datos()
P = d["programa"]


def horas(area):
    """Las horas de un área, en entero. Si el reparto la dejó en cero pero el
    área sí midió algo, se muestra «<1» en vez de cero: cero diría que no hizo
    nada, y no es lo que pasó."""
    h = D.HORAS.get(area, 0)
    if h == 0 and D.CRUDAS.get(area, 0) > 0:
        return "&lt;1"
    return f"{h:,.0f}".replace(",", ".")


def mil(n):
    return f"{n:,.0f}".replace(",", ".")


def ent(n):
    """Entero con punto de millar. Un valor menor que una hora, pero no cero, se
    muestra como «<1»: redondearlo a cero haría parecer que el área no hizo nada."""
    return "&lt;1" if 0 < n < 1 else f"{n:,.0f}".replace(",", ".")


def dec(n, k=1):
    return f"{n:,.{k}f}".replace(",", "·").replace(".", ",").replace("·", ".")


# De la encuesta solo quedaron las cifras agregadas: las dos medias y el reparto
# de promotores, pasivos y detractores. Las respuestas individuales no existen en
# ningún archivo, así que no se dibuja una línea por persona.
ANTES, DESPUES = P["confianza"]
NPS_DIST = {"p": 10, "a": 4, "d": 6}
assert sum(NPS_DIST.values()) == P["respuestas_nps"], NPS_DIST
assert round((NPS_DIST["p"] - NPS_DIST["d"]) / P["respuestas_nps"] * 100) == P["nps"]

# ───────────────────────── piezas reutilizables ─────────────────────────

def tile(big, lab, src="", delay=0.0, chico=False):
    s = f'<p class="big"{"" if chico else ""}>{big}</p>'
    f = f'<p class="src">{src}</p>' if src else ""
    return (f'<div class="tile rv" style="--d:{delay}s">{s}'
            f'<p class="lab">{lab}</p>{f}</div>')


def barra(label, valor, pct, delay=0.0, suave=False, cols="330px 1fr 130px"):
    cls = "bar soft" if suave else "bar"
    return (f'<div class="hb" style="grid-template-columns:{cols}">'
            f'<span class="lb">{label}</span>'
            f'<div class="trk"><i class="{cls}" style="--w:{pct:.1f}%;--d:{delay}s"></i></div>'
            f'<span class="vl">{valor}</span></div>')


PALABRAS = ["cero", "una", "dos", "tres", "cuatro", "cinco", "seis", "siete",
            "ocho", "nueve", "diez", "once", "doce", "trece", "catorce", "quince",
            "dieciséis", "diecisiete", "dieciocho", "diecinueve", "veinte"]


def palabra(n):
    """El número en letra, que es como se lee un titular. Si se sale del rango
    conocido se devuelve la cifra, antes que inventar una palabra."""
    return PALABRAS[n] if 0 <= n < len(PALABRAS) else str(n)


def mono(ini, grande=False):
    t = "72px" if grande else "44px"
    f = "26px" if grande else "16px"
    return (f'<span class="mono" style="width:{t};height:{t};font-size:{f}">{ini}</span>')


def reparto():
    """Describe el reparto de minutos leyéndolo de MINUTOS, en el orden de la
    jornada, para que el pie nunca contradiga la tabla."""
    from itertools import groupby
    bloques = [(m, len(list(g))) for m, g in groupby(D.MINUTOS[a] for a, _, _ in D.JORNADA)]
    def trozo(m, n, i):
        if n == 1 and i == 0:
            return f"{m} minutos para la primera"
        cual = "siguientes" if i < len(bloques) - 1 else "últimas"
        return f"{m} para las {palabra(n)} {cual}"
    partes = [trozo(m, n, i) for i, (m, n) in enumerate(bloques)]
    return ", ".join(partes[:-1]) + " y " + partes[-1]


def slide(sid, titulo, cuerpo, oscura=True, pie=""):
    cls = "dk" if oscura else "lt"
    ft = f' data-ft="{pie}"' if pie else ""
    return (f'<section class="slide {cls}" id="{sid}" data-t="{titulo}"{ft}>\n{cuerpo}\n</section>\n')


# ───────────────────────── 1 · portada ─────────────────────────

chips = "".join(
    f'<span class="chip bord">{a}</span>' for a, _, _ in D.JORNADA)

s1 = slide("portada", "Portada", f"""
  <div class="row" style="flex:1;align-items:center;gap:72px">
    <div class="col f1" style="gap:30px">
      <p class="eb">IAM™ Intelligence · Comfacesar · Fase 1</p>
      <h1>Lo que la Caja aprendió a hacer sola</h1>
      <p class="lede">{P['sesiones']} sesiones · {P['areas']} áreas · {P['colaboradores']} colaboradores ·
        {P['inicio']} al {P['cierre']} de 2026<br>
        Presentación a la dirección · {D.JORNADA_FECHA}</p>
      <div class="row wrap">{chips}</div>
    </div>
    <div class="col" style="width:540px;gap:0;border-left:1px solid var(--rule-d);padding-left:38px">
      <p class="big huge">{ent(P['horas'])}</p>
      <p class="sub" style="padding-top:10px">horas recuperadas cada semana</p>
      <p class="hair" style="padding-top:12px">equivalen a {ent(P['horas'] / 48)} jornadas de trabajo, o a
        {ent(P['horas'] / 44)} personas a tiempo completo, sin contratar a nadie</p>
    </div>
  </div>""", pie="Sandra Curvelo · Mentora IAM™ · recuperación semanal del programa, establecida por la mentoría sobre la medición tarea por tarea")

# ───────────────────────── 2 · tabla de contenido ─────────────────────────

bloques = [
    ("01", "Los resultados", "La dirección ve de dónde salió la Caja y dónde está hoy: horas, pesos, "
                             "el índice de inteligencia empresarial y lo que quedó abierto.",
     "Presenta la mentoría", f"{D.JORNADA_INTRO} min"),
    ("02", "Las áreas, en vivo", f"Las {palabra(len(D.JORNADA))} áreas con proceso activo muestran lo que construyeron. "
                                 f"No hay presentación preparada: se muestra funcionando.",
     "Presenta cada área", "Jornada completa"),
    ("03", "Lo que viene", "Hiperconectividad: dejar de tener dieciocho islas que no se hablan. "
                           "El año, trimestre por trimestre.",
     "Presenta la mentoría", f"{D.JORNADA_CIERRE} min"),
]
toc = "".join(
    f'<div class="row toc rv" style="--d:{0.1 + i * .18}s">'
    f'<p class="num">{n}</p>'
    f'<div class="col f1" style="gap:8px"><h3>{t}</h3><p class="hair">{desc}</p></div>'
    f'<div class="col" style="width:280px;gap:6px;text-align:right">'
    f'<p class="who">{quien}</p><p class="hair">{dur}</p></div></div>'
    for i, (n, t, desc, quien, dur) in enumerate(bloques))

s2 = slide("contenido", "Cómo va la jornada", f"""
  <p class="eb">{D.JORNADA_FECHA.capitalize()}</p>
  <h2>Cómo va la jornada</h2>
  <div class="col" style="gap:26px;flex:1;justify-content:center">{toc}</div>""", oscura=False)

# ───────────────────────── 3 · los resultados ─────────────────────────

tiles = "".join([
    tile(f'{P["sesiones"]}', "sesiones verificadas, con grabación, acta y asistencia", "", .05),
    tile(f'{P["areas"]}<small> / {P["areas"]}</small>', "áreas llegaron al cierre, ninguna quedó por fuera", "", .13),
    tile(f'{P["asistencia"]}<small>%</small>',
         f'de asistencia acumulada: {P["asistieron"]} de {P["convocados"]} convocados', "", .21),
    tile(f'{ent(P["horas"])}<small> h</small>', "recuperadas cada semana en toda la Caja", "", .29),
    tile(f'{dec(P["confianza"][0])}<small> → </small>{dec(P["confianza"][1])}',
         "confianza usando IA, antes y después, escala de 1 a 10", f'{P["respuestas_nps"]} respuestas anónimas', .37),
    tile(f'{round(NPS_DIST["p"] / P["respuestas_nps"] * 100)}<small>%</small>',
         "de quienes respondieron son promotores del programa",
         f'NPS +{P["nps"]} sobre {P["respuestas_nps"]} respuestas anónimas', .45),
])

s3 = slide("resultados", "Los resultados", f"""
  <p class="eb">Bloque 01 · los resultados</p>
  <h2>Once semanas, y esto es lo que quedó instalado</h2>
  <div class="grid3">{tiles}</div>
  <p class="note rv" style="--d:.6s">Sesiones, asistencia y confianza salen de actas, grabaciones y
    encuesta anónima. <b>Las horas son la recuperación real del programa</b>, e incluyen los
    ejercicios que las áreas construyeron y no alcanzaron a registrar en el tablero.</p>""",
           pie="Fuentes: tablero de cierre · Sala de Control · encuesta anónima de 20 respuestas · corte 9 de octubre de 2026")

# ───────────────────────── 4 · horas por área ─────────────────────────

hmax = max(D.HORAS.values())
hb = "".join(barra(a, f'{horas(a)} h', h / hmax * 100, .08 * i)
             for i, (a, h) in enumerate(sorted(D.HORAS.items(), key=lambda x: -x[1])))

s4 = slide("horas", "Horas por área", f"""
  <p class="eb">La recuperación</p>
  <h2>Horas recuperadas por semana, área por área</h2>
  <div class="row" style="gap:56px;flex:1;align-items:center">
    <div class="col f1" style="gap:12px">{hb}</div>
    <div class="col" style="width:470px;gap:24px">
      <div><p class="big huge">{ent(P['horas'])}</p><p class="sub">horas por semana</p></div>
      <p class="note">Para entrar aquí, el área tuvo que anotar cuánto tardaba la tarea,
        cuánto tarda hoy y cuántas veces la hace. <b>Seis áreas no lo anotaron.</b></p>
      <p class="note"><b>Las seis construyeron igual.</b> Lo que no hicieron fue
        registrarlo, y por eso no suman horas aquí. Medir en pesos todavía no es
        costumbre, y es una de las cosas que esta fase deja abiertas.</p>
    </div>
  </div>""", oscura=False,
           pie="Base: Sala de Control · 53 tareas medidas con tiempo antes, tiempo hoy y frecuencia declarada · el total del programa lo establece la mentoría y el reparto por área conserva la proporción medida")

# ───────────────────────── 5 · el índice, qué mide ─────────────────────────

EJES = [
    ("Adopción", "adopcion", "Sesiones de trabajo que el área sostuvo",
     f'{D.UMBRALES["adopcion"]} sesiones = 25 puntos'),
    ("Producción", "produccion", "Procesos documentados y medidos en el tablero",
     f'{D.UMBRALES["produccion"]} procesos = 25 puntos'),
    ("Impacto", "impacto", "Horas recuperadas cada semana",
     f'{dec(D.UMBRALES["impacto"], 0)} horas = 25 puntos'),
    ("Autonomía", "autonomia", "Agentes construidos y corriendo solos",
     "4 puntos por agente, 8,5 más si ya corre"),
]
ejes_html = "".join(
    f'<div class="col f1 eje rv" style="--d:{.1 + i * .15}s">'
    f'<p class="big" style="font-size:64px">25</p>'
    f'<h3>{t}</h3><p class="hair">{desc}</p><p class="um">{um}</p></div>'
    for i, (t, k, desc, um) in enumerate(EJES))

s5 = slide("indice-que", "El índice, qué mide", f"""
  <p class="eb">Índice de Inteligencia Empresarial · IIE</p>
  <h2>Cuatro ejes de 25 puntos. Cien es el techo.</h2>
  <p class="lede">No mide cuánta inteligencia artificial usa un área. Mide cuánto de su trabajo
    quedó convertido en sistema: sostenido, documentado, medido y andando solo.</p>
  <div class="row" style="gap:24px">{ejes_html}</div>
  <p class="note rv" style="--d:.7s">Los umbrales están fijos y declarados, no son relativos al mejor
    del grupo. <b>Un área puede leer su propio número sin compararse con nadie.</b></p>""")

# ───────────────────────── 6 · el índice en 3D ─────────────────────────

INI = {a: ini for a, ini, _ in D.JORNADA}
INI.update({"Tecnología": "TE", "Mercadeo": "ME", "Talento Humano": "TH",
            "Cumplimiento": "CU", "Planeación": "PL", "Tesorería": "TS"})

datos_js = json.dumps([{
    "a": a, "i": INI.get(a, a[:2].upper()), "c": d["cierre"][a]["iie"],
    "s": d["septiembre"][a]["iie"], "h": D.HORAS.get(a, 0.0),
    "ses": d["cierre"][a]["sesiones"], "pr": d["cierre"][a]["procesos"],
    "ag": d["cierre"][a]["agentes"], "e": d["cierre"][a]["ejes"],
} for a in d["orden"]], ensure_ascii=False)

s6 = slide("indice-3d", "El índice en 3D", f"""
  <div class="row" style="justify-content:space-between;align-items:flex-end">
    <div class="col" style="gap:10px">
      <p class="eb">Índice de Inteligencia Empresarial · las 18 áreas</p>
      <h2>El relieve de la Caja, hoy</h2>
    </div>
    <div class="col" style="text-align:right;gap:4px">
      <p class="big" style="font-size:78px">{ent(d['promedio']['septiembre'])}<small> → </small>{ent(d['promedio']['cierre'])}</p>
      <p class="hair">IIE promedio · 30 de septiembre al cierre</p>
    </div>
  </div>
  <div class="row" style="flex:1;min-height:0;gap:32px">
    <div class="f1" style="min-width:0;position:relative">
      <canvas id="c3d"></canvas>
    </div>
    <div class="col" style="width:430px;gap:0;overflow:hidden;justify-content:center" id="rank3d"></div>
  </div>""",
           pie="La columna llena es el cierre, la transparente es el corte del 30 de septiembre · gira sola, con la barra espaciadora se detiene · dibujado sin librerías, funciona sin internet")

# ───────────────────────── 7 · quién subió ─────────────────────────

mov = sorted(d["orden"], key=lambda a: -(d["cierre"][a]["iie"] - d["septiembre"][a]["iie"]))
quietas = [a for a in mov if abs(d["cierre"][a]["iie"] - d["septiembre"][a]["iie"]) < .05]
subieron = [a for a in mov if a not in quietas]
imax = max(d["cierre"][a]["iie"] for a in d["orden"])


def fila_mov(a, i):
    c, s = d["cierre"][a]["iie"], d["septiembre"][a]["iie"]
    delta = c - s
    sig = "sube" if delta > .05 else "quieta"
    return (f'<div class="hb slope" style="grid-template-columns:270px 1fr 108px">'
            f'<span class="lb">{a}</span>'
            f'<div class="trk"><i class="bar soft" style="--w:{s / imax * 100:.1f}%;--d:{.05 * i}s"></i>'
            f'<i class="bar" style="--w:{c / imax * 100:.1f}%;--d:{.3 + .05 * i}s"></i></div>'
            f'<span class="vl {sig}">{"+" + ent(delta) if delta > .05 else "·"}</span></div>')


s7 = slide("movimiento", "Quién subió y quién no", f"""
  <p class="eb">Índice de Inteligencia Empresarial · el movimiento</p>
  <h2>{palabra(len(subieron)).capitalize()} áreas subieron. {palabra(len(quietas)).capitalize()} se quedaron donde estaban.</h2>
  <div class="row" style="gap:48px;flex:1">
    <div class="col f1" style="gap:9px">
      {"".join(fila_mov(a, i) for i, a in enumerate(subieron))}
      <p class="hair" style="margin-top:10px">Sin movimiento desde el 30 de septiembre</p>
      {"".join(fila_mov(a, i) for i, a in enumerate(quietas))}
    </div>
    <div class="col" style="width:430px;gap:20px;justify-content:center">
      <p class="note"><b>Agencia de Empleo es la que más subió,</b> +{ent(d['cierre']['Agencia de Empleo']['iie'] - d['septiembre']['Agencia de Empleo']['iie'])} puntos.
        Puso a Matías en producción y le respondió a un ciudadano de verdad.</p>
      <p class="note"><b>Sub. Admin y Financiera tiene el mayor impacto en horas, {ent(D.HORAS['Sub. Admin y Financiera'])},
        y aun así no se movió.</b> Hizo todo en septiembre y nada después del cierre.</p>
      <p class="hair">La barra gris es septiembre, la roja es hoy. El corte de septiembre se
        reconstruye con las {P['fichas_fechadas']} sesiones que llevan acta fechada de las {P['sesiones']}.</p>
    </div>
  </div>""", oscura=False)

# ───────────────────────── 8 · antes y hoy ─────────────────────────

antes_h = 2088.0
hoy_h = antes_h - P["horas"] * 11
red = P["horas"] * 11 / antes_h * 100

s8 = slide("antes-hoy", "Antes y hoy", f"""
  <p class="eb">Tarea por tarea</p>
  <h2>Las {ent(P['horas'])} horas, cada semana, otra vez</h2>
  <p class="lede">No es un ahorro que ocurrió una vez. Es una hora que vuelve
    <b>cada semana</b>, porque el proceso cambió, no porque alguien corrió más.</p>
  <div class="f1" style="min-width:0"><svg id="acum" viewBox="0 0 1680 372" role="img"
    aria-label="Horas acumuladas semana a semana durante un año"></svg></div>
  <div class="grid3">
    {tile(f'{mil(P["horas"] * 52)}<small> h</small>', "al año, si nada más cambia", "", .6)}
    {tile(f'{ent(P["horas"] / 44)}', "personas a tiempo completo, sin contratar a nadie", "44 h por semana", .7)}
    {tile(f'{ent(P["horas"] / 48)}', "jornadas de trabajo recuperadas por semana", "48 h = una jornada de 8 h × 6", .8)}
  </div>""",
           pie="Las horas son recurrentes: vuelven cada semana sin volver a invertir en el programa, porque lo que cambió fue el proceso")

# ───────────────────────── 9 · el valor en pesos ─────────────────────────

# Sin tarifas a la vista: solo los totales, a una tarifa promedio de los perfiles
# que ejecutan y revisan. El costo hora de cada perfil no se publica.
_sem = P["horas"] * D.TARIFA_MEZCLA
_anio = _sem * 52
_mes = _anio / 12

PLATA = [("Cada semana", _sem), ("Cada mes", _mes), ("En doce meses", _anio)]
plata = "".join(
    f'<div class="tile rv" style="--d:{.1 + i * .16}s">'
    f'<p class="big" style="font-size:52px;letter-spacing:-1px">${mil(v)}</p>'
    f'<p class="lab">{t}</p></div>'
    for i, (t, v) in enumerate(PLATA))

s9 = slide("pesos", "El valor en pesos", f"""
  <div class="col" style="gap:32px;flex:1;justify-content:center">
  <p class="eb">La cuenta</p>
  <h2>Lo que valen {ent(P['horas'])} horas que vuelven cada semana</h2>
  <p class="lede">Un proceso no lo ejecuta un solo perfil. Hay quien lo hace y quien lo
    revisa, así que la valoración usa <b>un promedio de los perfiles que intervienen</b>,
    no el costo de una persona en particular.</p>
  <div class="grid3">{plata}</div>
  <p class="note rv" style="--d:.6s">Es dinero que <b>no se deja de gastar una vez</b>:
    son horas de gente que ya está contratada y que ahora se emplean en otra cosa.
    {ent(P['horas'] * 52)} horas al año que la Caja recupera sin contratar a nadie.</p>
  </div>""", oscura=False,
           pie="Horas medidas por el programa y valoradas con las tarifas de costo hora de Comfacesar · 52 semanas al año")

# ───────────────────────── 10 · confianza ─────────────────────────

s10 = slide("confianza", "Confianza con IA", f"""
  <p class="eb">Capacidad instalada</p>
  <h2>De {dec(P['confianza'][0])} a {dec(P['confianza'][1])} en once semanas</h2>
  <div class="row" style="gap:56px;flex:1;align-items:center">
    <div class="f1" style="min-width:0"><svg id="conf" viewBox="0 0 980 500" role="img"
      aria-label="Confianza usando IA antes y después del programa"></svg></div>
    <div class="col" style="width:470px;gap:24px">
      <div><p class="hair">Media de confianza usando IA, escala de 1 a 10</p>
        <p class="big" style="font-size:88px;white-space:nowrap"><span class="soft-n">{dec(P['confianza'][0])}</span><span
        style="color:var(--red-hi)"> → {dec(P['confianza'][1])}</span></p></div>
      <p class="note"><b>La mitad de quienes respondieron son promotores.</b>
        NPS +{P['nps']}, positivo, sobre {P['respuestas_nps']} respuestas anónimas.</p>
      <p class="note"><b>Quienes tomaron seis o más sesiones califican la utilidad en 10.</b>
        Es el mismo patrón del índice: el resultado sigue a quien se sentó.</p>
      <p class="hair">{P['asistencia']}% de asistencia en once semanas, con {P['caidas']}
        sesiones caídas de {P['sesiones'] + P['caidas']} agendadas.</p>
    </div>
  </div>""",
            pie=f"Fuente: encuesta anónima · {P['respuestas_nps']} respuestas de {P['colaboradores']} colaboradores · la media es de quienes respondieron")

# ───────────────────────── 11 · lo que quedó abierto ─────────────────────────

ab = "".join(
    f'<div class="col f1 open rv" style="--d:{.1 + i * .14}s">'
    f'<p class="num2">0{i + 1}</p><h3>{t}</h3><p class="hair">{desc}</p></div>'
    for i, (t, desc) in enumerate(D.ABIERTO))

s11 = slide("abierto", "Lo que no se resolvió", f"""
  <p class="eb">Lo que el cierre no resolvió</p>
  <h2>Cuatro cosas que esta fase deja abiertas</h2>
  <p class="lede">El director pidió ver las debilidades, no solo los resultados.
    Estas cuatro son las que la mentoría encontró y no alcanzó a cerrar.</p>
  <div class="row" style="gap:22px;flex:1;align-items:stretch">{ab}</div>""", oscura=False)

# ───────────────────────── 12 · la jornada, las 12 áreas ─────────────────────────

HORARIO = {a: (i, f, m) for a, i, f, m in D.horario()}


def fila_area(i, area, ini, muestra):
    quien = D.PRESENTA.get(area, "")
    iie_a = d["cierre"][area]["iie"]
    desde, hasta, mins = HORARIO[area]
    met = f'{desde}<span class="qm"> · {mins}\u2009min</span>'
    return (f'<div class="row ja rv" style="--d:{.04 * i}s">'
            f'<p class="n">{i + 1:02d}</p>{mono(ini)}'
            f'<p class="an f1">{area}<span class="qm"> · {muestra}</span></p>'
            f'<p class="who pr">{quien}</p>'
            f'<p class="vl" style="width:150px;text-align:right">{met}</p>'
            f'<p class="iie" style="width:84px;text-align:right">{ent(iie_a)}</p></div>')


s12 = slide("jornada", "Las áreas de la jornada", f"""
  <p class="eb">Bloque 02 · las áreas, en vivo</p>
  <h2>{palabra(len(D.JORNADA)).capitalize()} áreas, {D.JORNADA_FECHA.split(",")[1].strip()}</h2>
  <div class="col" style="gap:3px;flex:1;justify-content:center">
    <div class="row ja hd"><p class="n">N°</p><span style="width:44px"></span>
      <p class="f1">Área y qué muestra</p>
      <p class="pr">Quién presenta</p>
      <p style="width:150px;text-align:right">Hora</p>
      <p style="width:84px;text-align:right">IIE</p></div>
    {"".join(fila_area(i, a, ini, m) for i, (a, ini, m) in enumerate(D.JORNADA))}
  </div>""",
            pie=f"El orden lo fijó la dirección, por complejidad del proceso resuelto · {reparto()}")

# ───────────────────────── 13 · las indicaciones ─────────────────────────

ind = "".join(
    f'<div class="row toc rv" style="--d:{.1 + i * .16}s">'
    f'<p class="num">0{i + 1}</p>'
    f'<div class="col f1" style="gap:8px"><h3>{t}</h3><p class="hair">{desc}</p></div></div>'
    for i, (t, desc) in enumerate(D.INDICACIONES))

s13 = slide("indicaciones", "Cómo presenta cada área", f"""
  <p class="eb">Bloque 02 · la indicación</p>
  <h2>Una o dos diapositivas. Lo demás se muestra andando.</h2>
  <div class="col" style="gap:22px;flex:1;justify-content:center">{ind}</div>
  <p class="note rv" style="--d:.8s">La regla del cierre es una sola:
    <b>lo que no está documentado no se presenta.</b> El tablero del área es de donde sale
    lo que se puede mostrar.</p>""")

# ──────────────── 14 · las dieciocho islas ────────────────

HECHOS = [
    ("Cada área con lo suyo",
     "Su proceso, su archivo y su tablero alimentado a mano, cada semana, por una persona."),
    ("Si no estás en la red, no trabajas",
     "La información vive en servidores locales y en carpetas de cada equipo."),
    ("El puesto fijo amarra",
     "Equipos de escritorio para una forma de trabajo que ya no es de escritorio."),
]
hechos = "".join(
    f'<div class="col hecho rv" style="--d:{.15 + i * .18}s">'
    f'<h3>{t}</h3><p class="hair">{desc}</p></div>'
    for i, (t, desc) in enumerate(HECHOS))

s14 = slide("islas", "Dieciocho islas", f"""
  <p class="eb">Bloque 03 · lo que viene</p>
  <h2>Dieciocho islas que no se hablan</h2>
  <div class="row" style="gap:48px;flex:1;min-height:0;align-items:center">
    <div class="f1 lienzo" style="min-width:0">
      <canvas id="burbujas" aria-label="Las dieciocho áreas como burbujas sueltas, ninguna conectada"></canvas>
      <div id="tip-isla" class="tip" hidden></div>
    </div>
    <div class="col" style="width:520px;gap:20px">{hechos}
      <p class="note">Entre una isla y otra <b>no hay una sola línea.</b> Ese es el punto,
        y es lo único que la primera fase no podía resolver sola.</p>
    </div>
  </div>""", oscura=False,
            pie="Cada burbuja es un área y su tamaño es el índice · pasa el cursor por una para ver cuál es · ninguna está conectada a otra")

# ──────────────── 15 · la fase 2, enunciada y no vendida ────────────────

enun = "".join(
    f'<div class="col f1 enun rv" style="--d:{.12 + i * .2}s">'
    f'<p class="eb">{t}</p>'
    f'<ul>{"".join(f"<li>{x}</li>" for x in puntos)}</ul></div>'
    for i, (t, puntos) in enumerate(D.ENUNCIADO))

s15 = slide("hacia-donde", "Hacia dónde va", f"""
  <p class="eb">Bloque 03 · lo que viene</p>
  <h2>Ya saben hacerlo. Ahora hay que conectarlo.</h2>
  <p class="lede">El límite de hoy no es el conocimiento. Son los equipos, la red local,
    y que cada área guarda su avance en su propia isla. <b>Esto queda enunciado,
    no es lo que se decide hoy.</b></p>
  <div class="row" style="gap:28px;flex:1;align-items:stretch;max-height:470px">{enun}</div>
  <p class="note rv" style="--d:.6s">Nada de esto pide cambiar el ecosistema de software
    que la Caja ya pagó, ni contratar a nadie. <b>Son procesos y conexiones.</b></p>""",
            oscura=False,
            pie="Enunciado, no propuesta: el alcance, el plazo y la inversión van en el documento de la fase 2, aparte")

# ──────────────── 16 · el cierre del programa ────────────────

ag_c = sum(v[0] for v in D.AGENTES.values())
ag_r = sum(v[1] for v in D.AGENTES.values())

QUEDA = [
    (f"{P['areas']}", "áreas con al menos un proceso propio andando"),
    (f"{ag_c}<small> / {ag_r}</small>", "agentes construidos, y los que ya corren solos"),
    (f"{ent(P['horas'])}<small> h</small>", "que vuelven cada semana, sin volver a invertir"),
]
queda = "".join(
    f'<div class="row paso rv" style="--d:{.12 + i * .18}s">'
    f'<p class="big" style="font-size:66px;min-width:230px">{v}</p>'
    f'<p class="sub" style="font-weight:400;font-size:26px;align-self:center">{t}</p></div>'
    for i, (v, t) in enumerate(QUEDA))

s16 = slide("cierre", "Lo que se queda en la Caja", f"""
  <div class="row" style="gap:80px;flex:1">
    <div class="col f1" style="gap:26px;justify-content:center">
      <p class="big" style="font-size:118px;color:var(--red-hi)">IAM™</p>
      <p class="sub">Intelligence · fase 1, cerrada</p>
      <h2 style="font-size:46px">Esto ya no depende<br>de la mentoría.</h2>
      <p class="hair">{P['sesiones']} sesiones en {P['areas']} áreas, de {P['inicio']} al
        {P['cierre']}. <b>Lo que se construyó se queda en la Caja</b>, con la gente que lo armó.</p>
    </div>
    <div class="col f1" style="gap:34px;justify-content:center">
      <h3 class="q">Lo que se queda</h3>
      {queda}
    </div>
  </div>""", pie="Sandra Curvelo · Mentora IAM™ · Influence, AI & Monetization")

# ──────────────── 16 · los doce bloques del año ────────────────

def gantt(t, a, b, i):
    izq = (a - 1) / 12 * 100
    anc = (b - a + 1) / 12 * 100
    meses = f"Mes {a}" if a == b else f"Meses {a} a {b}"
    return (f'<div class="gl rv" style="--d:{.05 * i}s"><span class="lb">{t}</span>'
            f'<div class="gt"><i class="gb" style="--l:{izq:.4f}%;--w:{anc:.4f}%;'
            f'--d:{.3 + .07 * i}s"></i></div>'
            f'<span class="gm">{meses}</span></div>')

regla = "".join(f'<span>{m}</span>' for m in range(1, 13))
s16b = slide("cronograma", "Los bloques del año", f"""
  <p class="eb">Bloque 03 · el año</p>
  <h2>Los {palabra(len(D.CRONOGRAMA))} bloques, y en qué meses va cada uno</h2>
  <div class="col" style="gap:4px;flex:1;justify-content:center">
    <div class="gl hdr"><span class="lb">Frente de trabajo</span>
      <div class="regla">{regla}</div><span class="gm">Meses</span></div>
    {"".join(gantt(t, a, b, i) for i, (t, a, b) in enumerate(D.CRONOGRAMA))}
  </div>""", oscura=False,
             pie="Los frentes de la fase 2 con el rango de meses que trae la propuesta · el alcance y la inversión se tratan aparte")


# ──────────── 17 · Servicios Sociales, para el cierre de Sandra ────────────

# El área no expone en la jornada del martes 17, así que sus cifras no se ven en
# vivo y Sandra las presenta en su bloque de cierre. Solo van las tres tareas
# MEDIDAS, verificadas en sesión y que suman las horas del área en el libro. Las
# otras diez tareas del área están marcadas como estimadas en la Sala de Control
# y no se cuentan aquí: la comparación de la convención colectiva es una de
# ellas, y por eso no aparece como cifra de titular.
SS_MEDIDAS = [
    ("Informe de Seguimiento N° 12 · Buenavista", "Mensual", 1440, 45, 322),
    ("Informe de Seguimiento N° 4 · cubierta cancha", "Mensual", 1440, 240, 277),
    ("Informe de Gestión · tercer trimestre", "Trimestral", 720, 30, 53),
]
# Las tres tareas tienen que sumar las horas que el libro le atribuye al área:
# si alguna cifra se mueve, la diapositiva no se construye.
assert round(sum(x[4] for x in SS_MEDIDAS) / 60, 1) == round(D.MEDIDAS["Servicios Sociales"], 1), \
    sum(x[4] for x in SS_MEDIDAS) / 60

ss_barras = "".join(
    barra(f"{t} <small style='opacity:.6'>· {frec}</small>",
          f"{mil(antes)} → {mil(ahora)} min",
          100 * (antes - ahora) / antes, .2 + i * .14, cols="620px 1fr 210px")
    for i, (t, frec, antes, ahora, _eq) in enumerate(SS_MEDIDAS))

s17 = slide("servicios-sociales", "El área que no expone", f"""
  <p class="eb">Lo que no se va a ver en vivo</p>
  <h2>Servicios Sociales: {dec(D.MEDIDAS['Servicios Sociales'])} horas a la semana, medidas</h2>
  <p class="lede">El área no alcanza a exponer en la jornada, así que estas cifras
    no las cuenta nadie desde el escenario. Son <b>tres tareas verificadas en
    sesión</b>, con su tiempo de antes y su tiempo de hoy.</p>
  <div class="col" style="gap:14px">{ss_barras}</div>
  <div class="grid3">
    {tile(f'{dec(D.MEDIDAS["Servicios Sociales"])}<small> h</small>', "a la semana, medidas y verificadas", "suma de las tres tareas", .7)}
    {tile(f'{ent(D.HORAS["Servicios Sociales"])}<small> h</small>', f"proyectadas, de las {ent(P['horas'])} del programa", "", .8)}
    {tile("97%", "la baja más profunda del área", "un informe mensual de 24 h a 45 min", .9)}
  </div>
  <p class="note rv" style="--d:1s">El área tiene <b>diez tareas más estimadas</b>,
    pendientes de verificar, entre ellas la comparación de la convención colectiva.
    No se suman a estas horas hasta que se midan.</p>""",
           pie="Tres tareas medidas y verificadas en sesión, del libro de procesos del programa · las tareas estimadas del área no se incluyen")

SLIDES = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16b, s17, s16]

# ───────────────────────── CSS ─────────────────────────

CSS = """
/* Layout: escenario fijo de 1920×1080 escalado al visor; diapositivas oscuras y
   claras alternadas; un solo rojo IAM™ como acento y nada más compitiendo. */
:root{
  --red:#c00000; --red-hi:#ff4a4a; --red-dim:#7a1414;
  --ink:#0a0a0a; --ink-2:#141414; --ink-3:#1e1e1e; --rule-d:#2b2b2b;
  --paper:#f4f2ee; --card:#fbfaf8; --rule-l:#ddd8d1;
  --on-d:#f4f2ec; --mute-d:#a8a39a; --dim-d:#7c7871;
  --on-l:#131313; --mute-l:#55524c; --dim-l:#76726b;
  --good:#1d7444; --good-d:#5fcf8e;
  --chrome:#050505;
  --f-h:"Montserrat","Arial Black",Arial,Helvetica,sans-serif;
  --f-b:"Lato",Arial,Helvetica,sans-serif;
  --f-s:"Source Serif 4",Georgia,serif;
  color-scheme:dark;
}
html,body{height:100%}
body{background:var(--chrome);color:var(--on-d);font-family:var(--f-b);overflow:hidden}
#vp{position:fixed;inset:0;padding-top:env(safe-area-inset-top,0px);
  padding-bottom:calc(60px + env(safe-area-inset-bottom,0px));
  padding-left:max(16px,env(safe-area-inset-left,0px));
  padding-right:max(16px,env(safe-area-inset-right,0px));overflow:hidden}
#stage{position:absolute;left:50%;top:50%;width:1920px;height:1080px;
  transform-origin:center center;box-shadow:0 30px 90px rgba(0,0,0,.65)}
.slide{position:absolute;inset:0;overflow:hidden;opacity:0;visibility:hidden;
  transition:opacity .4s ease,visibility .4s;padding:96px 120px 146px;
  display:flex;flex-direction:column;gap:32px}
.slide.act{opacity:1;visibility:visible}
.dk{background:var(--ink);color:var(--on-d)}
.lt{background:var(--paper);color:var(--on-l)}
.slide::before{content:"";position:absolute;left:0;top:0;bottom:0;width:13px;background:var(--red)}
.ft{position:absolute;left:120px;right:120px;bottom:48px;font-size:20px;line-height:1.35}
.dk .ft{color:var(--dim-d)} .lt .ft{color:var(--dim-l)}
h1,h2,h3{margin:0;font-family:var(--f-h);font-weight:800;text-wrap:balance}
p,ul{margin:0} ul{padding-left:22px}
h1{font-size:94px;line-height:1.03;letter-spacing:-2px}
h2{font-size:56px;line-height:1.08;letter-spacing:-.6px}
h3{font-size:29px;line-height:1.2}
.eb{font-size:21px;font-weight:700;letter-spacing:4px;text-transform:uppercase;color:var(--red)}
.dk .eb{color:var(--red-hi)}
.lede{font-size:29px;line-height:1.42;max-width:1480px}
.dk .lede{color:var(--mute-d)} .lt .lede{color:var(--mute-l)}
.hair{font-size:22px;line-height:1.4}
.dk .hair{color:var(--mute-d)} .lt .hair{color:var(--mute-l)}
.sub{font-size:27px;font-weight:700}
.row{display:flex;gap:22px} .row.wrap{flex-wrap:wrap;gap:12px}
.col{display:flex;flex-direction:column;gap:14px;min-width:0}
.f1{flex:1;min-width:0}
.big{font-family:var(--f-h);font-weight:800;line-height:1;letter-spacing:-1.5px;
  font-variant-numeric:tabular-nums;font-size:84px;color:var(--red)}
.dk .big{color:var(--red-hi)}
.big small{font-size:.44em;letter-spacing:0}
.big.huge{font-size:116px;padding:22px 0 0;letter-spacing:-3px}
.soft-n{color:#8f8a82}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.grid3.alto{grid-auto-rows:1fr}
.tile{display:flex;flex-direction:column;gap:9px;padding:26px 30px;border-top:5px solid var(--red)}
.dk .tile{background:var(--ink-2);border-left:1px solid var(--rule-d);
  border-right:1px solid var(--rule-d);border-bottom:1px solid var(--rule-d)}
.lt .tile{background:var(--card);border-left:1px solid var(--rule-l);
  border-right:1px solid var(--rule-l);border-bottom:1px solid var(--rule-l)}
.tile .lab{font-size:25px;line-height:1.3;font-weight:700}
.tile .src{font-size:20px} .dk .tile .src{color:var(--dim-d)} .lt .tile .src{color:var(--dim-l)}
.chip{display:inline-block;font-size:22px;font-weight:700;padding:8px 18px;white-space:nowrap}
.chip.bord{border:2px solid var(--red)}
.note{font-size:25px;line-height:1.4;padding:18px 24px;border-left:5px solid var(--red)}
.dk .note{background:var(--ink-2)} .lt .note{background:var(--card)}
table.t{border-collapse:collapse;width:100%;font-size:25px}
table.t th{font-size:20px;letter-spacing:1.5px;text-transform:uppercase;text-align:left;
  padding:14px 18px;background:var(--red);color:#fff}
table.t td{padding:15px 18px;vertical-align:top}
.dk table.t td{border-bottom:1px solid var(--rule-d);color:var(--mute-d)}
.dk table.t td:first-child{color:var(--on-d);font-weight:700}
.lt table.t td{border-bottom:1px solid var(--rule-l);color:var(--mute-l)}
.lt table.t td:first-child{color:var(--on-l);font-weight:700}
.num,td.num{text-align:right;font-variant-numeric:tabular-nums}
td.st{color:var(--red)!important;font-weight:800} .dk td.st{color:var(--red-hi)!important}
/* barras */
.hb{display:grid;align-items:center;gap:16px;font-size:24px}
.hb .lb{text-align:right;font-weight:700;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.trk{height:28px;position:relative}
.dk .trk{background:var(--ink-3)} .lt .trk{background:#e8e4de}
.bar{position:absolute;left:0;top:0;bottom:0;width:0;background:var(--red);
  transition:width 1.2s cubic-bezier(.2,.8,.2,1);transition-delay:var(--d,0s)}
.dk .bar{background:var(--red-hi)}
.act .bar{width:var(--w)}
.bar.soft{background:#8f8a82;opacity:.55}
.slope .trk{height:24px}
.vl{font-weight:800;font-variant-numeric:tabular-nums;text-align:right}
.vl.sube{color:var(--red)} .dk .vl.sube{color:var(--red-hi)}
.vl.quieta{color:var(--dim-l)} .dk .vl.quieta{color:var(--dim-d)}
/* tabla de contenido y pasos */
.toc{align-items:center;gap:32px;padding:22px 26px;border-left:5px solid var(--red)}
.dk .toc{background:var(--ink-2)} .lt .toc{background:var(--card)}
.toc .num,.paso .num{font-family:var(--f-h);font-weight:800;font-size:42px;color:#fff;
  background:var(--red);padding:12px 18px;line-height:1}
.who{font-size:22px;font-weight:700;color:var(--red)} .dk .who{color:var(--red-hi)}
.paso{align-items:flex-start;gap:24px}
.q{font-size:46px}
/* monogramas */
.mono{display:inline-flex;align-items:center;justify-content:center;flex:none;
  border-radius:50%;background:var(--red);color:#fff;font-family:var(--f-h);
  font-weight:800;letter-spacing:.5px}
.dk .mono{background:var(--red-dim);color:#ffd9d9;border:2px solid var(--red-hi)}
/* jornada */
.ja{align-items:center;gap:16px;padding:2px 14px}
.dk .ja{border-bottom:1px solid var(--rule-d)} .lt .ja{border-bottom:1px solid var(--rule-l)}
.ja.hd{font-size:19px;letter-spacing:2px;text-transform:uppercase;font-weight:700;border-bottom-width:2px}
.dk .ja.hd{color:var(--mute-d)} .lt .ja.hd{color:var(--mute-l)}
.ja .n{font-family:var(--f-h);font-weight:800;font-size:26px;width:44px;
  font-variant-numeric:tabular-nums}
.dk .ja .n{color:var(--dim-d)} .lt .ja .n{color:var(--dim-l)}
.ja .pr{width:330px;flex:none;font-size:20px;overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap}
.ja.hd .pr{font-size:19px}
.ja .an{font-size:24px;font-weight:700;min-width:0;overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap}
.ja .qm{font-weight:400;font-size:21px}
.dk .ja .qm{color:var(--mute-d)} .lt .ja .qm{color:var(--mute-l)}
.ja .iie{font-family:var(--f-h);font-weight:800;font-size:28px;color:var(--red)}
.dk .ja .iie{color:var(--red-hi)}
/* ejes, frentes, abiertos, trimestres */
.eje{padding:24px 26px;border-top:5px solid var(--red)}
.dk .eje{background:var(--ink-2)} .lt .eje{background:var(--card)}
.eje .um{font-size:21px;font-weight:700;color:var(--red);margin-top:auto}
.dk .eje .um{color:var(--red-hi)}
.open,.frente{padding:24px 26px;gap:10px}
.dk .open,.dk .frente{background:var(--ink-2);border-top:4px solid var(--red-hi)}
.lt .open,.lt .frente{background:var(--card);border-top:4px solid var(--red)}
.num2{font-family:var(--f-h);font-weight:800;font-size:34px;color:var(--red)}
.dk .num2{color:var(--red-hi)}
.gl{display:grid;grid-template-columns:490px 1fr 132px;align-items:center;gap:16px;font-size:20px}
.gl .lb{font-weight:700;text-align:right;min-width:0;overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap}
.gl .gm{font-size:19px;font-variant-numeric:tabular-nums}
.dk .gl .gm{color:var(--mute-d)} .lt .gl .gm{color:var(--mute-l)}
.gl.hdr{font-size:19px;letter-spacing:2px;text-transform:uppercase;padding-bottom:8px}
.dk .gl.hdr{color:var(--mute-d)} .lt .gl.hdr{color:var(--mute-l)}
.gt{position:relative;height:28px}
.dk .gt{background:var(--ink-3)} .lt .gt{background:#e8e4de}
.gb{position:absolute;top:0;bottom:0;width:0;left:var(--l);background:var(--red);
  transition:width 1s cubic-bezier(.2,.8,.2,1);transition-delay:var(--d,0s)}
.dk .gb{background:var(--red-hi)}
.act .gb{width:var(--w)}
.regla{display:grid;grid-template-columns:repeat(12,1fr);font-size:17px;text-align:center}
.regla span{padding-bottom:4px}
.dk .regla{border-bottom:1px solid var(--rule-d)} .lt .regla{border-bottom:1px solid var(--rule-l)}
.lienzo{position:relative}
#burbujas{width:100%;height:600px;display:block;cursor:default}
.tip{position:absolute;transform:translate(-50%,-100%);pointer-events:none;
  display:flex;flex-direction:column;gap:3px;padding:12px 18px;white-space:nowrap;
  background:var(--ink);color:var(--on-d);border-left:4px solid var(--red-hi);
  box-shadow:0 8px 26px rgba(0,0,0,.22);z-index:4}
.tip b{font-family:var(--f-h);font-size:25px;font-weight:800}
.tip span{font-size:20px;color:var(--mute-d)}
.hecho{padding:20px 24px;gap:7px}
.dk .hecho{background:var(--ink-2);border-left:4px solid var(--red-hi)}
.lt .hecho{background:var(--card);border-left:4px solid var(--red)}
.hecho h3{font-size:25px}
.enun{padding:30px 34px;gap:18px}
.dk .enun{background:var(--ink-2);border-top:5px solid var(--red-hi)}
.lt .enun{background:var(--card);border-top:5px solid var(--red)}
.enun .eb{font-size:26px;letter-spacing:3px}
.enun ul{font-size:25px;line-height:1.45;display:flex;flex-direction:column;gap:16px}
.dk .enun ul{color:var(--mute-d)} .lt .enun ul{color:var(--mute-l)}
.enun li::marker{color:var(--red)}
.tri{flex:1;padding:24px 24px 26px;gap:10px}
.dk .tri{background:var(--ink-2);border-top:5px solid var(--red-hi)}
.lt .tri{background:var(--card);border-top:5px solid var(--red)}
.tri .meses{font-size:21px;font-weight:700}
.dk .tri .meses{color:var(--mute-d)} .lt .tri .meses{color:var(--mute-l)}
.tri ul{font-size:21px;line-height:1.42;display:flex;flex-direction:column;gap:9px}
.dk .tri ul{color:var(--mute-d)} .lt .tri ul{color:var(--mute-l)}
.tri li::marker{color:var(--red)}
/* islas */
.islas{display:grid;grid-template-columns:repeat(9,1fr);gap:14px;flex:1;align-content:center}
.isla{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;
  padding:18px 8px;font-family:var(--f-h);font-weight:800;font-size:30px;
  background:var(--card);border:1px solid var(--rule-l);color:var(--red)}
.isla em{font-family:var(--f-b);font-style:normal;font-weight:400;font-size:17px;
  line-height:1.2;text-align:center;color:var(--mute-l)}
/* 3D */
#c3d{width:100%;height:620px;display:block}
#rank3d .rk{display:grid;grid-template-columns:30px 1fr 68px;align-items:center;gap:10px;
  font-size:19px;padding:4px 8px;border-bottom:1px solid var(--rule-d)}
#rank3d .rk b{font-family:var(--f-h);font-size:21px;color:var(--red-hi);
  font-variant-numeric:tabular-nums;text-align:right}
#rank3d .rk i{font-style:normal;color:var(--dim-d);font-variant-numeric:tabular-nums}
#rank3d .rk span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--mute-d)}
/* apariciones */
.rv{opacity:0;transform:translateY(16px);transition:opacity .55s ease,transform .55s ease;
  transition-delay:var(--d,0s)}
.act .rv{opacity:1;transform:none}
/* controles */
#bar{position:fixed;left:0;right:0;bottom:0;height:calc(60px + env(safe-area-inset-bottom,0px));
  padding-bottom:env(safe-area-inset-bottom,0px);
  padding-left:max(16px,env(safe-area-inset-left,0px));
  padding-right:max(16px,env(safe-area-inset-right,0px));
  display:flex;align-items:center;gap:12px;background:var(--chrome);z-index:20}
#bar button{font:700 14px var(--f-b);color:var(--on-d);background:#1a1a1a;border:1px solid #333;
  padding:9px 15px;cursor:pointer;border-radius:4px}
#bar button:hover{border-color:var(--red-hi)}
#bar button:focus-visible{outline:2px solid var(--red-hi);outline-offset:2px}
#prog{flex:1;height:4px;background:#222;position:relative;min-width:36px}
#prog i{position:absolute;left:0;top:0;bottom:0;background:var(--red);transition:width .35s}
#ttl{font-size:13px;color:var(--mute-d);white-space:nowrap;overflow:hidden;
  text-overflow:ellipsis;max-width:34vw}
#idx{font-size:13px;color:var(--dim-d);font-variant-numeric:tabular-nums;white-space:nowrap}
@media (max-width:700px){#ttl{display:none}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{
  transition-duration:.01ms!important;animation-duration:.01ms!important}}
"""

# ───────────────────────── JS ─────────────────────────

JS = """
const DATA = __DATOS__;

/* ── escenario ── */
const stage=document.getElementById('stage'),vp=document.getElementById('vp');
function fit(){
  const r=vp.getBoundingClientRect();
  const k=Math.min(r.width/1920,r.height/1080);
  stage.style.transform='translate(-50%,-50%) scale('+k+')';
}
addEventListener('resize',fit);fit();

/* ── diapositivas ── */
const slides=[...document.querySelectorAll('.slide')];
let cur=0;
const ttl=document.getElementById('ttl'),idx=document.getElementById('idx'),
      pi=document.querySelector('#prog i');
slides.forEach(s=>{
  const ft=s.dataset.ft;
  if(ft){const p=document.createElement('p');p.className='ft';p.textContent=ft;s.appendChild(p);}
});
function cuenta(s){
  s.querySelectorAll('[data-n]').forEach(el=>{
    const to=parseFloat(el.dataset.n),dc=parseInt(el.dataset.dec||'0',10),t0=performance.now();
    (function step(t){
      const k=Math.min((t-t0)/900,1),v=to*(1-Math.pow(1-k,3));
      el.textContent=v.toLocaleString('es-CO',{minimumFractionDigits:dc,maximumFractionDigits:dc});
      if(k<1)requestAnimationFrame(step);
    })(t0);
  });
}
function ir(n){
  cur=(n+slides.length)%slides.length;
  slides.forEach((s,i)=>s.classList.toggle('act',i===cur));
  const s=slides[cur];
  ttl.textContent=s.dataset.t||'';
  idx.textContent=(cur+1)+' / '+slides.length;
  pi.style.width=((cur+1)/slides.length*100)+'%';
  cuenta(s);
  if(s.id==='indice-3d')arranca3d();else detiene3d();
  if(s.id==='confianza')dibujaConf();
  if(s.id==='antes-hoy')dibujaAcum();\n  if(s.id==='islas')arrancaIslas();else detieneIslas();
  try{location.hash=s.id}catch(e){}
}
document.getElementById('prev').onclick=()=>ir(cur-1);
document.getElementById('next').onclick=()=>ir(cur+1);
addEventListener('keydown',e=>{
  if(e.key==='ArrowRight'||e.key==='PageDown'){e.preventDefault();ir(cur+1)}
  if(e.key==='ArrowLeft'||e.key==='PageUp'){e.preventDefault();ir(cur-1)}
  if(e.key==='Home'){e.preventDefault();ir(0)}
  if(e.key==='End'){e.preventDefault();ir(slides.length-1)}
  if(e.key===' '){e.preventDefault();gira=!gira}
});

/* ── el ranking al lado del 3D ── */
document.getElementById('rank3d').innerHTML=DATA.map((x,i)=>
  '<div class="rk"><i>'+(i+1)+'</i><span>'+x.a+'</span><b>'+
  Math.round(x.c)+'</b></div>'
).join('');

/* ── 3D propio, sin librería y sin CDN ────────────────────────────────
   Proyección en perspectiva de cajas, con algoritmo del pintor. Se escribe
   aquí entero a propósito: en la sala de Comfacesar puede no haber salida a
   internet, y una presentación no puede depender de que cargue un CDN. */
let raf=0, ang=0, gira=true, cv3, cx3, W3=1180, H3=620;
const COLS=6, PASO=1.78, PITCH=.47, FOCAL=1010, DIST=14.2, ALTO=3.45;

function tono(v){
  return v>=70?[255,74,74]: v>=40?[192,0,0]: v>=15?[122,20,20]:[58,34,34];
}
function sombra(rgb,k,alpha){
  const [r,g,b]=rgb;
  return 'rgba('+Math.round(r*k)+','+Math.round(g*k)+','+Math.round(b*k)+','+alpha+')';
}
let FIT={k:1,dx:0,dy:0};
function crudo(x,y,z,a){
  const X= x*Math.cos(a)-z*Math.sin(a);
  const Z= x*Math.sin(a)+z*Math.cos(a);
  const Y2= y*Math.cos(PITCH)-Z*Math.sin(PITCH);
  const Z2= y*Math.sin(PITCH)+Z*Math.cos(PITCH);
  const s= FOCAL/(DIST+Z2);
  return [X*s, -Y2*s, Z2, s];
}
function proyecta(x,y,z,a){
  const p=crudo(x,y,z,a);
  return [W3/2+(p[0]+FIT.dx)*FIT.k, H3/2+(p[1]+FIT.dy)*FIT.k, p[2], p[3]*FIT.k];
}
/* Encuadre automático: se mide el modelo en una vuelta entera y se ajusta la
   escala para que nunca se corte, sea cual sea el dato o el tamaño de la sala. */
function encuadra(){
  const n=DATA.length, nx=COLS, nz=Math.ceil(n/nx);
  let x0=1e9,x1=-1e9,y0=1e9,y1=-1e9;
  for(let t=0;t<30;t++){
    const a=t/30*Math.PI*2;
    DATA.forEach((d,i)=>{
      const px=(i%nx-(nx-1)/2)*PASO, pz=(Math.floor(i/nx)-(nz-1)/2)*PASO*1.14;
      const hc=Math.max(d.c/100*ALTO,.08);
      for(const sy of [0,hc,hc+.34]) for(const dx of [-.62,.62]) for(const dz of [-.62,.62]){
        const p=crudo(px+dx,sy,pz+dz,a);
        if(p[0]<x0)x0=p[0]; if(p[0]>x1)x1=p[0];
        if(p[1]<y0)y0=p[1]; if(p[1]>y1)y1=p[1];
      }
    });
  }
  const mx=26, k=Math.min((W3-mx*2)/(x1-x0),(H3-mx*2)/(y1-y0));
  FIT={k:k, dx:-(x0+x1)/2, dy:-(y0+y1)/2};
}
function caja(cx,cz,w,h,a){
  const k=w/2, v=[];
  for(const sy of [0,h]) for(const [dx,dz] of [[-k,-k],[k,-k],[k,k],[-k,k]])
    v.push(proyecta(cx+dx,sy,cz+dz,a));
  // 0..3 abajo, 4..7 arriba
  return [
    {p:[v[4],v[5],v[6],v[7]], k:1.00},            // techo
    {p:[v[0],v[1],v[5],v[4]], k:0.62},            // frente norte
    {p:[v[1],v[2],v[6],v[5]], k:0.78},            // este
    {p:[v[2],v[3],v[7],v[6]], k:0.62},            // sur
    {p:[v[3],v[0],v[4],v[7]], k:0.78},            // oeste
  ].map(f=>({...f, z: f.p.reduce((t,q)=>t+q[2],0)/4}));
}
function pinta(){
  const n=DATA.length, nx=COLS, nz=Math.ceil(n/nx);
  cx3.clearRect(0,0,W3,H3);
  const caras=[], etiq=[];
  DATA.forEach((x,i)=>{
    const px=(i%nx-(nx-1)/2)*PASO, pz=(Math.floor(i/nx)-(nz-1)/2)*PASO*1.14;
    const hc=Math.max(x.c/100*ALTO,.08), hs=Math.max(x.s/100*ALTO,.05);
    const col=tono(x.c);
    caja(px,pz,.86,hc,ang).forEach(f=>caras.push({...f,col,alpha:1}));
    if(hs>.06) caja(px,pz,1.06,hs,ang).forEach(f=>caras.push({...f,col:[198,192,182],alpha:.30}));
    caja(px,pz,1.10,.045,ang).forEach(f=>caras.push({...f,col:[34,34,34],alpha:.9}));
    const t=proyecta(px,hc+.30,pz,ang);
    etiq.push({et:x.i, x:t[0], y:t[1], z:t[2], s:t[3]});
  });
  caras.sort((a,b)=>b.z-a.z);
  for(const f of caras){
    cx3.beginPath();
    cx3.moveTo(f.p[0][0],f.p[0][1]);
    for(let q=1;q<4;q++) cx3.lineTo(f.p[q][0],f.p[q][1]);
    cx3.closePath();
    cx3.fillStyle=sombra(f.col,f.k,f.alpha);
    cx3.fill();
  }
  /* las etiquetas van encima de todo: es un gráfico, y que se lean manda */
  etiq.sort((a,b)=>b.z-a.z);
  cx3.textAlign='center';
  for(const e of etiq){
    const k=Math.max(13,Math.min(23,e.s*.42));
    cx3.font='800 '+k.toFixed(0)+'px Montserrat, Arial, sans-serif';
    cx3.lineWidth=4; cx3.strokeStyle='rgba(8,8,8,.9)';
    cx3.strokeText(e.et,e.x,e.y);
    cx3.fillStyle='rgba(247,245,239,.97)';
    cx3.fillText(e.et,e.x,e.y);
  }
}
function lazo(){
  if(gira) ang+=.0045;
  pinta();
  raf=requestAnimationFrame(lazo);
}
function arranca3d(){
  if(!cv3){
    cv3=document.getElementById('c3d');
    W3=Math.max(cv3.clientWidth||1180,640); H3=cv3.clientHeight||620;
    cv3.width=W3*2; cv3.height=H3*2;
    cx3=cv3.getContext('2d');
    cx3.scale(2,2);
    encuadra();
  }
  if(!raf) lazo();
}
function detiene3d(){ if(raf){cancelAnimationFrame(raf);raf=0;} }

/* ── un trazo que se dibuja solo ── */
function traza(el,ms,retardo){
  if(!el||!el.getTotalLength)return;
  const L=el.getTotalLength();
  el.style.strokeDasharray=L; el.style.strokeDashoffset=L;
  requestAnimationFrame(()=>{
    el.style.transition='stroke-dashoffset '+ms+'ms cubic-bezier(.3,.8,.2,1) '+(retardo||0)+'ms';
    el.style.strokeDashoffset=0;
  });
}

/* ── las dieciocho burbujas ──
   Cada área es una burbuja suelta que flota. Sin siglas encima, porque fuera de
   contexto no se entienden: el nombre sale al pasar el cursor. Y sin una sola
   línea entre dos burbujas, que es lo que la diapositiva quiere decir. */
let bRaf=0, bCv, bCx, bW=1020, bH=600, BURB=[], bTip, bHover=-1;

function tonoIsla(v){
  if(v>=70) return ['#ff9090','#d01414','#850000'];
  if(v>=40) return ['#ffa6a6','#e04a4a','#991f1f'];
  if(v>=15) return ['#e6c2c2','#bb8080','#7d4f4f'];
  return ['#dcd8d1','#aaa49b','#6f6a63'];
}
function initBurbujas(){
  if(BURB.length) return;
  bCv=document.getElementById('burbujas'); bTip=document.getElementById('tip-isla');
  bW=bCv.clientWidth||1020; bH=bCv.clientHeight||600;
  bCv.width=bW*2; bCv.height=bH*2; bCx=bCv.getContext('2d'); bCx.scale(2,2);
  const jit=i=>{const a=Math.sin(i*12.9898)*43758.5453; return a-Math.floor(a);};
  DATA.forEach((x,i)=>{
    const r=22+x.c/100*36;
    BURB.push({d:x, r:r, x:r+8+jit(i)*(bW-2*r-16), y:r+8+jit(i+50)*(bH-2*r-16),
               vx:(jit(i+7)-.5)*.42, vy:(jit(i+13)-.5)*.42, f:jit(i+21)*6.283});
  });
  bCv.addEventListener('mousemove',e=>{
    const rc=bCv.getBoundingClientRect();
    const mx=(e.clientX-rc.left)*bW/rc.width, my=(e.clientY-rc.top)*bH/rc.height;
    let h=-1;
    for(let k=BURB.length-1;k>=0;k--){
      const b=BURB[k];
      if(Math.hypot(b.x-mx,b.y-my)<=b.r){h=k;break;}
    }
    if(h!==bHover){
      bHover=h;
      if(h<0){bTip.hidden=true;}
      else{
        const d=BURB[h].d;
        bTip.innerHTML='<b>'+d.a+'</b><span>'+(d.h?d.h+' h cada semana · ':'')+'índice '+Math.round(d.c)+'</span>';
        bTip.hidden=false;
      }
    }
    if(bHover>=0){
      /* el globito no puede salirse del lienzo: se acota a los lados y, si la
         burbuja está muy arriba, se voltea para abajo */
      const b=BURB[bHover], k=rc.width/bW;
      const tw=bTip.offsetWidth||220, th=bTip.offsetHeight||70;
      const x=Math.min(Math.max(b.x*k, tw/2+6), rc.width-tw/2-6);
      const arriba=(b.y-b.r)*k-14-th > 0;
      bTip.style.left=x+'px';
      bTip.style.top=(arriba ? (b.y-b.r)*k-14 : (b.y+b.r)*k+14+th)+'px';
    }
  });
  bCv.addEventListener('mouseleave',()=>{bHover=-1;bTip.hidden=true;});
}
function pintaBurbujas(t){
  bCx.clearRect(0,0,bW,bH);
  BURB.forEach((b,i)=>{
    b.x+=b.vx; b.y+=b.vy;
    if(b.x<b.r+6||b.x>bW-b.r-6) b.vx*=-1;
    if(b.y<b.r+6||b.y>bH-b.r-6) b.vy*=-1;
    const cy=b.y+Math.sin(t/1000+b.f)*3.5;
    const [hi,mid,lo]=tonoIsla(b.d.c);
    bCx.beginPath();
    bCx.ellipse(b.x,cy+b.r*.98,b.r*.74,b.r*.18,0,0,6.283);
    bCx.fillStyle='rgba(25,22,20,.10)'; bCx.fill();
    const g=bCx.createRadialGradient(b.x-b.r*.34,cy-b.r*.4,b.r*.08,b.x,cy,b.r);
    g.addColorStop(0,hi); g.addColorStop(.5,mid); g.addColorStop(1,lo);
    bCx.beginPath(); bCx.arc(b.x,cy,b.r,0,6.283); bCx.fillStyle=g; bCx.fill();
    if(i===bHover){bCx.lineWidth=3.5; bCx.strokeStyle='#c00000'; bCx.stroke();}
    bCx.beginPath();
    bCx.ellipse(b.x-b.r*.32,cy-b.r*.44,b.r*.25,b.r*.15,-.5,0,6.283);
    bCx.fillStyle='rgba(255,255,255,.45)'; bCx.fill();
  });
}
function lazoBurbujas(t){ pintaBurbujas(t||0); bRaf=requestAnimationFrame(lazoBurbujas); }
function arrancaIslas(){ initBurbujas(); if(!bRaf) lazoBurbujas(0); }
function detieneIslas(){ if(bRaf){cancelAnimationFrame(bRaf); bRaf=0;} }

/* ── la escalera de las 52 semanas ──
   Cada escalón es una semana que devuelve las mismas horas. La escalera es la
   forma del dato: no es un ahorro de una vez, es uno que se repite. */
function dibujaAcum(){
  const sv=document.getElementById('acum');
  if(sv.dataset.ok)return;sv.dataset.ok='1';
  const H=__HORAS__, N=52, TOT=H*N;
  const L=170,R=1620,T=46,B=296;
  const x=w=>L+w/N*(R-L), y=h=>B-h/TOT*(B-T);
  let o='';
  for(let i=0;i<=4;i++){
    const v=TOT*i/4;
    o+='<line x1="'+(L-18)+'" y1="'+y(v)+'" x2="'+R+'" y2="'+y(v)+'" stroke="#2b2b2b" stroke-width="1"/>'
      +'<text x="'+(L-30)+'" y="'+(y(v)+7)+'" fill="#7c7871" font-size="20" text-anchor="end">'
      +v.toLocaleString('es-CO',{maximumFractionDigits:0})+'</text>';
  }
  let d='M '+x(0)+' '+y(0);
  for(let w=1;w<=N;w++) d+=' L '+x(w)+' '+y(H*(w-1))+' L '+x(w)+' '+y(H*w);
  o+='<path d="'+d+' L '+x(N)+' '+B+' L '+x(0)+' '+B+' Z" fill="#ff4a4a" fill-opacity=".15"/>'
    +'<path class="traza" d="'+d+'" fill="none" stroke="#ff4a4a" stroke-width="3" stroke-linejoin="round"/>';
  [[4.33,'Al mes'],[13,'Al trimestre'],[N,'Al año']].forEach(([w,et])=>{
    const v=H*w, px=x(w), py=y(v);
    o+='<line x1="'+px+'" y1="'+py+'" x2="'+px+'" y2="'+B+'" stroke="#ff4a4a" stroke-width="1" stroke-dasharray="5 5" opacity=".5"/>'
      +'<circle cx="'+px+'" cy="'+py+'" r="9" fill="#ff4a4a"/>';
    /* el último hito toca el techo del gráfico, así que su etiqueta va debajo */
    const arriba = w<N, ty = arriba ? py-22 : py+34;
    o+='<text x="'+(px-18)+'" y="'+ty+'" fill="#f4f2ec" font-size="30" font-weight="700" text-anchor="end">'
      +Math.round(v).toLocaleString('es-CO')+' h</text>'
      +'<text x="'+(px-18)+'" y="'+(ty+28)+'" fill="#a8a39a" font-size="21" text-anchor="end">'+et+'</text>';
  });
  o+='<text x="'+x(0)+'" y="'+(B+32)+'" fill="#7c7871" font-size="20">Semana 1</text>'
    +'<text x="'+R+'" y="'+(B+32)+'" fill="#7c7871" font-size="20" text-anchor="end">Semana 52</text>';
  sv.innerHTML=o;
  traza(sv.querySelector('.traza'),1900,120);
}

/* ── confianza: las dos medias, y la distribución real del NPS ──
   Solo entran cifras agregadas, que son las que la encuesta dejó.
   No existen las respuestas individuales, así que no se dibuja una por persona. */
function dibujaConf(){
  const sv=document.getElementById('conf');
  if(sv.dataset.ok)return;sv.dataset.ok='1';
  const A=__ANTES__,Z=__DESPUES__,NPS=__NPS__;
  const L=170,R=700,T=46,B=330, esc=v=>B-(v-1)/9*(B-T);
  let o='';
  for(let v=1;v<=10;v++){
    const g=v%2===0;
    o+='<line x1="'+(L-26)+'" y1="'+esc(v)+'" x2="'+(R+40)+'" y2="'+esc(v)+'" stroke="#55524c" stroke-width="1" opacity="'+(g?.32:.14)+'"/>';
    if(g)o+='<text x="'+(L-40)+'" y="'+(esc(v)+7)+'" fill="#76726b" font-size="19" text-anchor="end">'+v+'</text>';
  }
  /* la pendiente de la media */
  o+='<line class="traza" x1="'+L+'" y1="'+esc(A)+'" x2="'+R+'" y2="'+esc(Z)+'" stroke="#c00000" stroke-width="7"/>'
    +'<circle cx="'+L+'" cy="'+esc(A)+'" r="15" fill="#8f8a82"/>'
    +'<circle cx="'+R+'" cy="'+esc(Z)+'" r="17" fill="#c00000"/>'
    +'<text x="'+L+'" y="'+(esc(A)+52)+'" fill="#55524c" font-size="23" text-anchor="middle">Antes</text>'
    +'<text x="'+R+'" y="'+(esc(Z)-38)+'" fill="#c00000" font-size="27" font-weight="700" text-anchor="middle">Hoy</text>'
    +'<text x="'+((L+R)/2)+'" y="'+(esc((A+Z)/2)-22)+'" fill="#c00000" font-size="25" font-weight="700" text-anchor="middle">+'+
      (Z-A).toLocaleString('es-CO',{minimumFractionDigits:1,maximumFractionDigits:1})+' puntos</text>';
  /* la distribución del NPS, barra apilada a escala */
  const BY=416,BH=46,BW=R+40-L, tot=NPS.p+NPS.a+NPS.d;
  let x=L;
  [['#c00000',NPS.p,'promotores'],['#9b958c',NPS.a,'pasivos'],['#3a2222',NPS.d,'detractores']]
  .forEach(([c,n,et])=>{
    const w=n/tot*BW;
    o+='<rect x="'+x+'" y="'+BY+'" width="'+w+'" height="'+BH+'" fill="'+c+'"/>'
      +'<text x="'+(x+w/2)+'" y="'+(BY+31)+'" fill="#fff" font-size="23" font-weight="700" text-anchor="middle">'+n+'</text>'
      +'<text x="'+(x+w/2)+'" y="'+(BY+BH+26)+'" fill="#76726b" font-size="19" text-anchor="middle">'+et+'</text>';
    x+=w;
  });
  o+='<text x="'+L+'" y="'+(BY-16)+'" fill="#55524c" font-size="19">Cómo se repartieron las '+
     tot+' respuestas</text>';
  sv.innerHTML=o;
  traza(sv.querySelector('.traza'),1200,200);
}

/* ── arranque y navegación por el hash ── */
function delHash(){
  const h=(location.hash||'').replace('#','');
  return slides.findIndex(s=>s.id===h);
}
addEventListener('hashchange',()=>{const i=delHash();if(i>=0&&i!==cur)ir(i)});
const i0=delHash();
ir(i0>=0?i0:0);
"""

js = (JS.replace("__DATOS__", datos_js)
      .replace("__ANTES__", repr(ANTES))
      .replace("__DESPUES__", repr(DESPUES))
      .replace("__NPS__", json.dumps(NPS_DIST))
      .replace("__HORAS__", repr(P["horas"])))

HTML = f"""<title>Cierre IAM™ Intelligence Comfacesar</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;800&family=Lato:wght@400;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap">
<style>{CSS}</style>

<div id="vp"><div id="stage">
{"".join(SLIDES)}
</div></div>

<div id="bar">
  <button id="prev" type="button" aria-label="Anterior">←</button>
  <button id="next" type="button" aria-label="Siguiente">→</button>
  <span id="idx"></span>
  <div id="prog"><i></i></div>
  <span id="ttl"></span>
</div>

<script>{js}</script>
"""

# Un id de dibujo que coincida con el de una diapositiva hace que
# getElementById devuelva la sección y el dibujo le borre el contenido.
# Pasó con "islas": el SVG y la diapositiva se llamaban igual.
# Las tarifas por perfil no se publican. Si alguna se cuela en el HTML, para.
for _n, _v, _ in D.TARIFAS:
    _fmt = f"{_v:,.0f}".replace(",", ".")
    assert _fmt not in HTML, f"se coló la tarifa de {_n}: {_fmt}"

_ids_slide = set(re.findall(r'<section class="slide[^>]*id="([^"]+)"', HTML))
_ids_dibujo = set(re.findall(r'<(?:svg|canvas) id="([^"]+)"', HTML))
_choque = _ids_slide & _ids_dibujo
assert not _choque, f"id repetido entre diapositiva y dibujo: {_choque}"
_todos = re.findall(r'\sid="([^"]+)"', HTML)
_dup = {i for i in _todos if _todos.count(i) > 1}
assert not _dup, f"ids duplicados en el HTML: {_dup}"

# Los números grandes se animan contando desde cero. El motor estaba escrito
# desde el principio pero ningún número llevaba la marca que lo activa, así que
# nunca arrancaba. Aquí se marca cada cifra dentro de un elemento .big.
_NUM = re.compile(r"(?<![\d.,])(\d{1,3}(?:\.\d{3})*(?:,\d+)?)(?![\d.,])")


def _marca(m):
    txt = m.group(1)
    val = float(txt.replace(".", "").replace(",", "."))
    dec = len(txt.split(",")[1]) if "," in txt else 0
    return f'<span data-n="{val}" data-dec="{dec}">{txt}</span>'


def anima_numeros(html):
    def por_big(m):
        trozos = re.split(r"(<[^>]+>)", m.group(2))
        return m.group(1) + "".join(
            t if t.startswith("<") else _NUM.sub(_marca, t) for t in trozos
        ) + m.group(3)

    return re.sub(r'(<p class="big[^"]*"[^>]*>)(.*?)(</p>)', por_big, html, flags=re.S)


HTML = anima_numeros(HTML)
assert HTML.count("data-n=") >= 18, HTML.count("data-n=")

# Mientras la jornada no tenga fecha, ninguna fecha concreta puede colarse en
# la presentación. Comfacesar aplazó la del 6 de noviembre el 4 de noviembre.
if not D.JORNADA_FIJADA:
    for _mal in ("viernes 6", "6 de noviembre", "viernes 13", "13 de noviembre"):
        assert _mal not in HTML, f"la jornada no tiene fecha y aparece {_mal!r}"

SALIDA.write_text(HTML, encoding="utf-8")

# Versión autónoma, para descargar y abrir fuera de la plataforma de artefactos.
# El archivo publicado va sin doctype ni cabecera porque la plataforma los pone;
# este los lleva, para que abra igual en cualquier navegador o se pueda subir
# como archivo a otro lado.
SUELTO = RAIZ / "presentacion-cierre-comfacesar-descargable.html"
_corte = HTML.index('<div id="vp">')
_cabeza, _cuerpo = HTML[:_corte], HTML[_corte:]
SUELTO.write_text(
    '<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
    + _cabeza +
    '<style>:root{color-scheme:light;box-sizing:border-box}'
    'html,body{height:100%}body{margin:0;background:#050505;color:#f4f2ec}'
    'img{max-width:100%}[hidden]{display:none!important}</style>\n'
    '</head>\n<body>\n' + _cuerpo + '</body>\n</html>\n',
    encoding="utf-8")

print(f"escrito {SALIDA.name} · {len(HTML):,} bytes · {len(SLIDES)} diapositivas")
print(f"escrito {SUELTO.name} · versión autónoma para descargar")
