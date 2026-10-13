# -*- coding: utf-8 -*-
"""Sala de Control Comfacesar · cierre del 13 de octubre de 2026.

Regenera el tablero sobre el archivo de assessment al cierre. El CSS, el bloque
de citas y el bloque de frecuencia estimada se toman tal cual de la version
publicada: lo que cambia son las cifras y las graficas, que se calculan aqui en
vez de quedar escritas a mano.
"""
import json, html

D = json.load(open('datos_cierre.json', encoding='utf-8'))
CSS = open('cabecera_css.html', encoding='utf-8').read()
EST = open('bloque_estimado.html', encoding='utf-8').read()
CITAS = open('bloque_citas.html', encoding='utf-8').read()

TARIFA = {'Profesional': 36351, 'Gerente o jefe': 62862, 'Directivo': 95941}
ACTA_VIV = {'area': 'Vivienda', 'tarea': 'Análisis de un informe de interventoría',
            'frec': 'Mensual · 11 proyectos', 'antes': 240, 'hoy': 30, 'sem_min': 512}

firmes = D['firmes']
SEM_MIN = sum(f['sem_min'] for f in firmes) + ACTA_VIV['sem_min']
H = SEM_MIN / 60
SEMANA = H * TARIFA['Profesional']
ANIO = SEMANA * 52

por_area = {}
for f in firmes:
    por_area[f['area']] = por_area.get(f['area'], 0) + f['sem_min']
por_area['Vivienda'] = por_area.get('Vivienda', 0) + ACTA_VIV['sem_min']
ranking = sorted(por_area.items(), key=lambda kv: -kv[1])

def n(x, d=1):
    """Numero a la colombiana: punto de miles, coma decimal."""
    s = f'{x:,.{d}f}'
    return s.replace(',', '\u0001').replace('.', ',').replace('\u0001', '.')

def e(s): return html.escape(str(s))

def pill(pct):
    c = 'good' if pct >= 75 else ('warn' if pct >= 50 else 'crit')
    return f'<span class="pill {c}">{pct:.0f}%</span>'

# ---- grafica de barras por area -------------------------------------------
def barras():
    alto_fila, y0 = 42, 33
    H_svg = y0 + alto_fila*len(ranking) + 60
    x0, ancho = 180, 390
    tope = 50.0
    esc = lambda v: v/tope*ancho
    o = [f'<svg viewBox="0 0 600 {H_svg}" role="img" aria-label="Horas recuperadas por semana en cada área, con la frecuencia de cada tarea aplicada. '
         + '; '.join(f'{a} {n(v/60)} horas' for a, v in ranking) + '.">']
    base = y0 + alto_fila*len(ranking) - 10
    for t in range(10, 51, 10):
        o.append(f'<line x1="{x0+esc(t):.1f}" y1="22" x2="{x0+esc(t):.1f}" y2="{base}" stroke="var(--grid)" stroke-width="1"></line>')
    o.append(f'<line x1="{x0}" y1="22" x2="{x0}" y2="{base}" stroke="var(--line-strong)" stroke-width="1"></line>')
    for i, (a, v) in enumerate(ranking):
        y = y0 + alto_fila*i
        w = max(esc(v/60), 0.8)
        suave = a == 'Vivienda'
        relleno = ('fill="var(--bar-soft)" stroke="var(--bar)" stroke-width="1.5"' if suave else 'fill="var(--bar)"')
        # el sufijo se salia del viewBox y quedaba cortado: lo dice la leyenda
        etiq = n(v/60) + ' h'
        o.append(f'<text class="s-lab" x="{x0-12}" y="{y+13}" text-anchor="end">{e(a)}</text>')
        o.append(f'<rect x="{x0}" y="{y}" width="{w:.1f}" height="18" rx="4" {relleno}></rect>')
        o.append(f'<text class="s-val" x="{x0+w+8:.1f}" y="{y+13}" text-anchor="start">{etiq}</text>')
    for t in range(0, 51, 10):
        o.append(f'<text class="s-tick" x="{x0+esc(t):.1f}" y="{base+22}" text-anchor="middle">{t}</text>')
    o.append(f'<text class="s-tick" x="{x0}" y="{base+36}" text-anchor="start">horas recuperadas por semana</text>')
    o.append('</svg>')
    return '\n        '.join(o)

# ---- grafica de proyeccion -------------------------------------------------
def proyeccion():
    y_base, y_top, x_i, x_f = 240, 40, 60, 580
    tope = 1000.0
    y = lambda m: y_base - (m/tope)*(y_base-y_top)
    o = [f'<svg viewBox="0 0 620 308" role="img" aria-label="Valor acumulado de las {n(H)} horas semanales recuperadas, con las tres tarifas de Comfacesar. A doce meses: '
         + ', '.join(f'{n(H*t*52/1e6)} millones a hora de {k.lower()}' for k, t in TARIFA.items()) + '.">']
    o.append(f'<line x1="{x_i}" y1="{y_base}" x2="{x_f}" y2="{y_base}" stroke="var(--line-strong)" stroke-width="1"></line>')
    for m in range(100, 1001, 100):
        o.append(f'<line x1="{x_i}" y1="{y(m):.1f}" x2="{x_f}" y2="{y(m):.1f}" stroke="var(--grid)" stroke-width="1"></line>')
    series = [('Directivo', TARIFA['Directivo'], 's3'),
              ('Gerente o jefe', TARIFA['Gerente o jefe'], 's2'),
              ('Profesional', TARIFA['Profesional'], 's1')]
    for nom, tar, cls in series:
        fin = H*tar*52/1e6
        o.append(f'<path d="M {x_i} {y_base} L {x_f} {y(fin):.1f}" fill="none" stroke="var(--{cls})" stroke-width="2.5" stroke-linecap="round"></path>')
    for nom, tar, cls in series:
        fin = H*tar*52/1e6
        o.append(f'<text class="s-end" x="{x_f-4}" y="{y(fin)-8:.1f}" text-anchor="end">{e(nom)} · ${n(fin)} M</text>')
        o.append(f'<circle cx="{x_f}" cy="{y(fin):.1f}" r="5" fill="var(--{cls})" stroke="var(--surface)" stroke-width="2"></circle>')
    for m in range(0, 1001, 100):
        o.append(f'<text class="s-tick" x="52" y="{y(m)+4:.1f}" text-anchor="end">{m if m else 0}{" M" if m else ""}</text>')
    for i, lab in enumerate(['cierre', '3 meses', '6 meses', '9 meses', '12 meses']):
        o.append(f'<text class="s-tick" x="{x_i+i*130}" y="258" text-anchor="middle">{lab}</text>')
    o.append(f'<text class="s-tick" x="{x_i}" y="276" text-anchor="start">pesos acumulados sobre las mismas {n(H)} horas semanales, valoradas a cada tarifa</text>')
    o.append('</svg>')
    return '\n        '.join(o)

# ---- tabla de detalle ------------------------------------------------------
def detalle():
    o = []
    for f in firmes:
        pct = (f['antes']-f['hoy'])/f['antes']*100
        o.append(f'<tr><td class="area">{e(f["area"])}</td><td class="tarea">{e(f["tarea"])}</td>'
                 f'<td class="frec">{e(f["frec"])}</td><td class="c">{n(f["antes"],0)}</td>'
                 f'<td class="c">{n(f["hoy"],0)}</td><td class="c">{pill(pct)}</td>'
                 f'<td class="c"><strong>{n(f["sem_min"],0)} min</strong></td></tr>')
    a = ACTA_VIV
    o.append(f'<tr><td class="area">{a["area"]}</td><td class="tarea">{e(a["tarea"])} <strong>medido en acta</strong></td>'
             f'<td class="frec">{e(a["frec"])}</td><td class="c">{a["antes"]}</td><td class="c">{a["hoy"]}</td>'
             f'<td class="c">{pill(87.5)}</td><td class="c"><strong>512 min</strong></td></tr>')
    o.append('<tr class="cero"><td colspan="7" style="text-align:left"><strong>A la espera de confirmar la frecuencia.</strong> '
             'Tres filas registran duraciones que, tomadas literalmente, no caben en una semana laboral: '
             '1.440 minutos son tres jornadas de ocho horas y 960 son dos. <strong>No entran a ninguna cifra de este tablero.</strong> '
             '<em>Eran dos y ahora son tres: la de Subsidio apareció al revisar el archivo al cierre.</em></td></tr>')
    for f in D['cuarentena']:
        pct = (f['antes']-f['hoy'])/f['antes']*100
        o.append(f'<tr class="cero"><td class="area">{e(f["area"])}</td><td class="tarea">{e(f["tarea"])}</td>'
                 f'<td class="frec">{e(f["frec"])}</td><td class="c">{n(f["antes"],0)}</td><td class="c">{n(f["hoy"],0)}</td>'
                 f'<td class="c">{pill(pct)}</td><td class="c">por confirmar</td></tr>')
    bloque = EST.replace(
        '<strong>Suman 18,0 horas por semana y se presentan aparte de las 133,9 verificadas.</strong>',
        '<strong>Al cierre son veintinueve y suman 24,9 horas por semana</strong>, y se presentan aparte de las '
        f'{n(H)} verificadas. Las siete que entraron al cierre son la campaña Sácale Provecho y la auditoría del logo '
        'de Comunicaciones, el informe de indicadores de Agencia de Empleo, el calendario tributario de Contabilidad, '
        'el infograma y la presentación institucional a entes de control de Jurídica, y las actas de liquidación de '
        'patrocinios de Servicios Sociales.')
    o.append(bloque.strip())
    antes_t = sum(f['antes'] for f in firmes) + a['antes']
    hoy_t = sum(f['hoy'] for f in firmes) + a['hoy']
    o.append(f'<tr class="suma"><td>52 tareas</td><td>Del archivo, con frecuencia declarada</td><td class="frec">52 frecuencias</td>'
             f'<td class="c">{n(sum(f["antes"] for f in firmes),0)}</td><td class="c">{n(sum(f["hoy"] for f in firmes),0)}</td>'
             f'<td class="c">90%</td><td class="c">{n(SEM_MIN-512,0)} min · {n((SEM_MIN-512)/60)} h</td></tr>')
    o.append('<tr class="suma"><td>+ 1 tarea</td><td>Medida en acta · Vivienda</td><td class="frec">Mensual</td>'
             '<td class="c">240</td><td class="c">30</td><td class="c">87%</td><td class="c">512 min · 8,5 h</td></tr>')
    o.append(f'<tr class="suma"><td><strong>53 tareas</strong></td><td><strong>Total que sostiene la cifra</strong></td>'
             f'<td class="frec">53 frecuencias</td><td class="c"><strong>{n(antes_t,0)}</strong></td>'
             f'<td class="c"><strong>{n(hoy_t,0)}</strong></td><td class="c"><strong>90%</strong></td>'
             f'<td class="c"><strong>{n(SEM_MIN,0)} min · {n(H)} h</strong></td></tr>')
    o.append('<tr class="suma est"><td>+ 29 tareas</td><td>Ocasionales, con frecuencia estimada por el agente Elia</td>'
             '<td class="frec">29 estimadas</td><td class="c">26.655</td><td class="c">1.457</td><td class="c">95%</td>'
             '<td class="c">1.494 min · 24,9 h</td></tr>')
    o.append(f'<tr class="suma"><td><strong>82 tareas</strong></td><td><strong>Verificado más estimado</strong></td>'
             f'<td class="frec">53 firmes · 29 est.</td><td class="c"><strong>{n(antes_t+26655,0)}</strong></td>'
             f'<td class="c"><strong>{n(hoy_t+1457,0)}</strong></td><td class="c"><strong>94%</strong></td>'
             f'<td class="c"><strong>{n(SEM_MIN+1494,0)} min · {n(H+24.9)} h</strong></td></tr>')
    return '\n          '.join(o)

def tarifas_tabla():
    o = []
    for nom, tar in TARIFA.items():
        base = ' <span class="pill base">Base del tablero</span>' if nom == 'Profesional' else ''
        cls = ' class="base"' if nom == 'Profesional' else ''
        o.append(f'<tr{cls}><td class="area">{e(nom)}{base}</td><td class="c">${n(tar,0)}</td>'
                 f'<td class="c">${n(H*tar,0)}</td><td class="c">${n(H*tar*52/1e6)} M</td></tr>')
    return '\n          '.join(o)

def equilibrio():
    o = []
    for inv in (20, 40, 60, 80):
        sem = inv*1e6/SEMANA
        vec = ANIO/(inv*1e6)
        o.append(f'<tr><td class="area">${inv} millones</td><td class="c">{n(sem)} semanas</td>'
                 f'<td class="c"><span class="pill good">{n(vec)} veces</span></td></tr>')
    return '\n          '.join(o)

HTML = f"""{CSS}
<div class="wrap">

  <header class="top">
    <p class="eyebrow">IAM™ Intelligence · Comfacesar · Sala de control</p>
    <h1>Horas recuperadas, y lo que valen</h1>
    <p class="lede">El cierre de la primera fase, en las dos monedas que importan: horas de trabajo y pesos. <strong>Cincuenta y tres tareas de doce áreas</strong>, cada una con su tiempo antes, su tiempo hoy y la frecuencia con que se ejecuta, más <strong>veintinueve con la frecuencia estimada</strong>, que se muestran aparte.</p>
    <div class="note crit" style="margin-top:.9rem"><strong>Este es el cierre, y la cifra sube de {n(133.9)} a {n(H)} horas por semana.</strong> No porque el programa haya hecho nada nuevo entre el 25 de septiembre y hoy, sino porque <em>el tablero estaba leyendo menos filas de las que las áreas habían escrito.</em>
      <br><br>
      <strong>Diecisiete filas del archivo nunca se habían visto.</strong> Casi todas son de áreas que escribieron después del 25 de septiembre, y no hay en ningún registro una decisión de dejarlas fuera: fue un hueco, no un criterio. Las que más pesan son el tablero de afiliaciones y la presentación al Consejo de Subsidio, el análisis de normas nuevas de Vivienda, la creación de piezas gráficas de Comunicaciones y los recobros de Agencia de Empleo.
      <br><br>
      <strong>Y hay dos filas que las propias áreas habían escrito y el archivo no estaba sumando</strong>, porque quedaron una línea por debajo del rango de la fórmula: la novena de Vivienda y la novena de Comunicaciones. <em>Eran datos suyos que no contaban para nada.</em>
      <br><br>
      <strong>Educación entra al tablero por primera vez.</strong> Llevaba cinco sesiones con cero filas. El consolidado mensual de subsidios de la Ley 115 pasó de dos horas a diez minutos y quedó medido en sesión sobre los datos reales del mes.
      <br><br>
      <strong>Qué se movió, dicho con precisión:</strong> las tareas que computan pasan de <strong>35 a 53</strong>, las horas de <strong>{n(133.9)} a {n(H)}</strong>, el valor a doce meses a tarifa de profesional de <strong>$253,0 a ${n(ANIO/1e6)} millones</strong>, las áreas que sostienen la cifra de <strong>diez a doce</strong>, y la capa estimada de <strong>18,0 a 24,9 horas</strong>. <em>La cifra anterior no estaba mal calculada: estaba calculada sobre menos datos.</em></div>
    <div class="note plain" style="margin-top:.9rem"><strong>Una fila más entró en cuarentena.</strong> Subsidio registró «Gestión correo» dos veces, una de 60 minutos diarios y otra de 1.440. <strong>1.440 minutos son tres jornadas de ocho horas, y eso no se hace todos los días</strong>, así que no suma, con el mismo criterio que ya se aplicaba a los dos agentes de Jurídica. <em>Si entrara tal como está escrita, esa sola fila valdría 105 horas por semana y se llevaría el tablero por delante.</em>
      <br><br>
      <strong>El cálculo lo hicieron por separado los dos agentes del programa</strong>, partiendo cada uno del archivo y sin ver el resultado del otro, y coincidieron en la misma cifra: {n(H)} horas. Es lo más parecido a una verificación que puede dar un tablero.</div>
    <span class="fuente">Archivo de assessment releído al cierre · 88 tareas registradas · actas de sesión · costo hora de Comfacesar · tres filas fuera del cálculo, a la espera de confirmar su frecuencia</span>
    <p class="stamp">Corte de las cifras: martes 13 de octubre de 2026 · la primera fase cerró el jueves 8 de octubre con la última sesión de Jurídica, Comunicaciones y Educación, y la caída de Agencia de Empleo del viernes 9</p>
  </header>

  <section>
    <div class="stats">
      <div class="stat hero"><b>{n(H)}<small> h</small></b><span>Recuperadas por semana, con la frecuencia aplicada</span></div>
      <div class="stat hero"><b>${n(ANIO/1e6,0)}<small> M</small></b><span>Valor a 12 meses, a costo hora de profesional</span></div>
      <div class="stat"><b>90%</b><span>Reducción sobre las tareas medidas</span></div>
      <div class="stat"><b>53<small> + 29</small></b><span>Tareas verificadas, más las estimadas por Elia</span></div>
      <div class="stat"><b style="color:var(--accent)">15<small> / 21</small></b><span>Áreas con al menos una medición</span></div>
    </div>

    <div class="note">
      <strong>Cómo se lee este tablero.</strong> Cada tarea trae su tiempo antes, su tiempo hoy y <strong>cada cuánto se hace</strong>. Esa frecuencia es la que convierte un ahorro puntual en un ahorro sostenido: una tarea diaria de veinte minutos pesa más al año que un informe trimestral de ocho horas.
      <br><br>
      <strong>Los minutos del archivo son el tiempo total que cuesta la tarea</strong>, no los minutos que se le dedican en un día. Una tarea de 1.440 minutos son tres jornadas de ocho horas repartidas en varios días. <em>Esa es la conversión del programa y es la que usa este tablero.</em>
      <br><br>
      <strong>Las cifras salen de dos fuentes y las dos se muestran por separado:</strong> lo que cada área registró en el archivo de assessment, y lo que quedó medido en acta durante la sesión. Las dos se verificaron con el equipo en el momento.
    </div>
  </section>

  <section>
    <div class="sec-head">
      <h3>El costo hora real</h3>
      <h2>Las tarifas de Comfacesar, aplicadas a las horas</h2>
    </div>
    <p>Una hora recuperada se vuelve dinero cuando se le pone precio. <strong>Estas son las tarifas de costo hora de Comfacesar.</strong> Todo el tablero está calculado sobre la de profesional, que es la más baja de las tres.</p>
    <div class="tablewrap">
      <table>
        <thead><tr><th>Perfil</th><th class="c">Costo hora</th><th class="c">{n(H)} h/semana valen</th><th class="c">A 12 meses</th></tr></thead>
        <tbody>
          {tarifas_tabla()}
        </tbody>
      </table>
    </div>
    <div class="note">
      <strong>Todo se valora a tarifa de profesional, y es una decisión deliberada.</strong> Parte de las tareas medidas las ejecuta una jefatura: el seguimiento a los asistentes jurídicos y el Informe Alta Gerencia, donde la hora vale ${n(TARIFA['Gerente o jefe'],0)}.
      <br><br>
      <strong>Valorarlas todas al perfil más bajo deja la cifra en su piso.</strong> Asignando a cada tarea el perfil que realmente la ejecuta, el resultado sube. <strong>${n(ANIO/1e6)} millones es el mínimo verificable, no la estimación optimista.</strong>
    </div>
  </section>

  <section>
    <div class="sec-head">
      <h3>La foto de nivel</h3>
      <h2>Tres cifras y una proporción</h2>
    </div>
    <div class="stats">
      <div class="stat hero"><b>${n(SEMANA/1e6,2)}<small> M</small></b><span>Recuperado cada semana, y sigue corriendo</span></div>
      <div class="stat hero"><b>${n(ANIO/1e6)}<small> M</small></b><span>A 12 meses, sin una sesión más</span></div>
      <div class="stat"><b>{n(20e6/SEMANA)}<small> sem</small></b><span>Para pagar una inversión de $20 M</span></div>
      <div class="stat"><b>{n(H/40,1)}</b><span>Personas a tiempo completo que esas horas liberan</span></div>
    </div>

    <div class="figs">
      <figure>
        <svg class="dona" viewBox="0 0 240 240" role="img" aria-label="Cobertura de la medición. Quince de las veintiún áreas tienen al menos una tarea medida; seis no tienen ninguna.">
          <circle cx="120" cy="120" r="70" fill="none" stroke="var(--track)" stroke-width="34"></circle>
          <g transform="rotate(-90 120 120)">
            <circle cx="120" cy="120" r="70" fill="none" stroke="var(--good)" stroke-width="34" stroke-dasharray="314.2 125.6" stroke-dashoffset="0"></circle>
          </g>
          <text class="s-big" x="120" y="118" text-anchor="middle">15/21</text>
          <text class="s-cap" x="120" y="138" text-anchor="middle">ÁREAS CON</text>
          <text class="s-cap" x="120" y="152" text-anchor="middle">MEDICIÓN</text>
        </svg>
        <p class="leyenda"><span class="lg"><i class="sw sA"></i> Con medición · 15 áreas</span><span class="lg"><i class="sw s4"></i> Sin ninguna · 6 áreas</span></p>
        <figcaption>Quince de veintiuna: catorce con filas en el archivo y Mercadeo con una medición en acta. Educación entra al cierre. Las seis restantes no es que no hayan producido: es que no se ha medido.</figcaption>
      </figure>
    </div>

    <figure>
      <svg viewBox="0 0 620 190" role="img" aria-label="Una vuelta completa de las 53 tareas que computan: antes tomaba 373 horas, hoy toma 38. La reducción es del 90 por ciento.">
        <text class="s-lab" x="14" y="46" text-anchor="start">Antes</text>
        <rect x="14" y="56" width="592" height="34" rx="4" fill="var(--s3)"></rect>
        <text class="s-val" x="28" y="78" text-anchor="start" fill="#fff">373 horas · 22.374 minutos</text>

        <text class="s-lab" x="14" y="126" text-anchor="start">Hoy</text>
        <rect x="14" y="136" width="61.1" height="34" rx="4" fill="var(--s1)"></rect>
        <text class="s-val" x="86" y="158" text-anchor="start">38 horas · 2.308 minutos</text>

        <text class="s-note" x="606" y="128" text-anchor="end">335 horas devueltas · 90%</text>
      </svg>
      <figcaption>Una vuelta completa de las 53 tareas que computan, sin aplicar frecuencia. Las dos barras están a la misma escala: la de abajo es el 10% de la de arriba.</figcaption>
    </figure>
  </section>

  <section>
    <div class="sec-head">
      <h3>Dónde están las horas</h3>
      <h2>Doce áreas sostienen las {n(H)} horas semanales</h2>
    </div>
    <figure>
      {barras()}
      <p class="leyenda"><span class="lg"><i class="sw full"></i> Registrado en el archivo de assessment</span><span class="lg"><i class="sw open"></i> Archivo más medición en acta</span></p>
      <figcaption>Vivienda pasa al segundo puesto: sus nueve tareas del archivo valen {n(por_area['Vivienda']/60 - 8.5)} horas y a eso se suman las 8,5 medidas en sesión. Subsidio entra cuarta con cuatro filas que el tablero no tenía. Educación aparece por primera vez, con {n(por_area.get('Educación',0)/60,1)} horas.</figcaption>
    </figure>
    <div class="note">
      <strong>El ahorro está concentrado, y el caso mayor sigue siendo la prevalidación precontractual.</strong> Rafael Solano la registró en 480 minutos diarios y la describió como «aproximadamente un día laboral»: con la automatización baja a 30. Esa línea sola devuelve <strong>37,5 horas a la semana</strong>, y con las otras cuatro automatizaciones diarias del área, Sub. Administrativa llega a <strong>{n(por_area['Sub. Admin y Financiera']/60)} horas</strong>.
      <br><br>
      <strong>Conviene mirar esa fila con la misma lupa que las tres que quedaron fuera.</strong> Las cinco tareas diarias de Rafael suman <strong>595 minutos al día</strong>, casi diez horas, es decir <em>49,6 horas a la semana</em> para una jornada de cuarenta. Es el mismo defecto que las otras tres, mucho más leve, y lo más probable es que signifique «por requerimiento» y no «cada día». <strong>Se deja dentro y se dice, en vez de sacarla en silencio.</strong>
      <br><br>
      <strong>El resto del programa, sin contar esa área, recupera {n(H-por_area['Sub. Admin y Financiera']/60)} horas semanales</strong>, equivalentes a <strong>${n((H-por_area['Sub. Admin y Financiera']/60)*TARIFA['Profesional']*52/1e6)} millones al año</strong>. Es decir que el resultado no depende de un solo caso: se sostiene con y sin él.
    </div>
  </section>

  <section>
    <div class="sec-head">
      <h3>La proyección</h3>
      <h2>Las mismas horas, valoradas a los tres perfiles</h2>
    </div>
    <figure>
      {proyeccion()}
      <p class="leyenda">{''.join(f'<span class="lg"><i class="sw {c}"></i> {k} · ${n(v,0)}</span>' for (k, v), c in zip(TARIFA.items(), ['s1','s2','s3']))}</p>
      <figcaption>Son las mismas horas en las tres líneas. Lo único que cambia es a qué tarifa se valoran. Las líneas son rectas porque el ahorro es recurrente: las mismas tareas se repiten cada semana, y la primera fase ya cerró.</figcaption>
    </figure>
    <div class="note plain">
      <strong>Lo que dice el gráfico, en una frase.</strong> A partir del cierre, el programa devuelve <strong>entre ${n(SEMANA/1e6,2)} y ${n(H*TARIFA['Directivo']/1e6,2)} millones cada semana</strong> según a qué perfil se le valore la hora, <strong>sin costo adicional</strong>, porque los procesos ya quedaron cambiados.
      <br><br>
      <strong>Las horas son las mismas en las tres líneas.</strong> Están medidas tarea por tarea, con su frecuencia. Lo único que cambia entre una línea y otra es el perfil al que se le valora esa hora.
      <br><br>
      <strong>El tablero se planta en la línea inferior:</strong> ${n(ANIO/1e6)} millones a doce meses, valorando todo a tarifa de profesional. El resultado real se ubica dentro de esa banda, siempre por encima del piso.
    </div>
  </section>

  <section>
    <div class="sec-head">
      <h3>La decisión de octubre</h3>
      <h2>Las licencias, en pesos</h2>
    </div>
    <p>Cinco áreas pidieron herramientas pagas por escrito. Puesto contra lo recuperado, deja de ser un gasto y pasa a ser una cuenta.</p>
    <div class="tablewrap">
      <table>
        <thead><tr><th>Escenario</th><th class="c">Personas</th><th class="c">Costo al año</th><th class="c">Recuperado al año</th><th class="c">Retorno</th></tr></thead>
        <tbody>
          <tr class="base"><td class="area">Solo las áreas que ya tienen medición</td><td class="c">25</td><td class="c">$24,0 M</td><td class="c">${n(ANIO/1e6)} M</td><td class="c"><span class="pill good">{n(ANIO/24e6)} veces</span></td></tr>
          <tr><td class="area">Todo el programa</td><td class="c">51</td><td class="c">$49,0 M</td><td class="c">${n(ANIO/1e6)} M</td><td class="c"><span class="pill good">{n(ANIO/49e6)} veces</span></td></tr>
        </tbody>
      </table>
    </div>
    <div class="note plain">
      <strong>La cuenta está hecha sobre una licencia profesional de US$20 al mes</strong>, a $4.000 por dólar, es decir $80.000 mensuales por persona. La cifra definitiva depende del plan que se elija.
      <br><br>
      <strong>Y compara contra el escenario más bajo</strong>: todas las horas valoradas a tarifa de profesional, con seis áreas todavía sin medir. El retorno real es mayor.
    </div>
    <div class="note">
      <strong>Hay capacidad instalada que hoy no se aprovecha.</strong> El acta de Tecnología del 11 de septiembre registra que <strong>la organización ya paga una herramienta de IA que prácticamente nadie utiliza</strong>. Antes de cualquier compra nueva vale inventariarla y decidir qué caso de uso cubre cada una.
      <br><br>
      La misma acta registra un segundo dato: <strong>el puesto asumió por su cuenta el costo de la herramienta</strong> con la que trabaja en el programa.
    </div>
  </section>

  <section>
    <div class="sec-head">
      <h3>El punto de equilibrio</h3>
      <h2>En cuántas semanas se paga la inversión</h2>
    </div>
    <p>A <strong>${n(SEMANA,0)} recuperados por semana</strong>, que es el escenario más bajo de los tres. <strong>El costo del programa no está en este tablero</strong>, así que aquí va la tabla para que se lea la cifra que corresponda.</p>
    <div class="tablewrap">
      <table>
        <thead><tr><th>Si la inversión fue</th><th class="c">Se paga en</th><th class="c">Y en 12 meses devuelve</th></tr></thead>
        <tbody>
          {equilibrio()}
        </tbody>
      </table>
    </div>
    <div class="note good">
      <strong>La cuenta está hecha con quince áreas de veintiuna, valoradas todas a la tarifa más baja.</strong> Las seis restantes no es que no hayan producido, es que no se ha medido. <strong>Cada área que se sienta a medir mueve el retorno hacia arriba</strong>, y no cuesta una sesión nueva: cuesta cuarenta minutos.
    </div>
  </section>

  <section>
    <div class="sec-head">
      <h3>El detalle que sostiene la cuenta</h3>
      <h2>Las cincuenta y tres tareas que computan, con su frecuencia</h2>
    </div>
    <p>Los nombres son los que escribió cada área, no una categoría nuestra. Esta es la tabla que hay que poder abrir si alguien pregunta de dónde sale el número.</p>
    <div class="tablewrap">
      <table>
        <thead>
          <tr><th>Área</th><th>Tarea</th><th>Frecuencia</th>
            <th class="c">Antes</th><th class="c">Hoy</th><th class="c">Reducción</th><th class="c">Ahorro semanal</th></tr>
        </thead>
        <tbody>
          {detalle()}
        </tbody>
      </table>
    </div>
    <div class="note">
      <strong>Las veintinueve tareas ocasionales entran a la cuenta con la frecuencia estimada, aparte de la cifra firme.</strong> Entre ellas está el mejor caso individual de todo el programa: cruzar la convención colectiva contra la propuesta de la administración pasó de <strong>quince días a cuarenta y cinco minutos</strong>, y responder una anotación de auditoría, de ocho días a cuatro horas. Juntas valen <strong>24,9 horas por semana</strong>.
      <br><br>
      <strong>Y las tres filas que siguen a la espera de confirmar frecuencia valen, juntas, más que todo el resto del tablero.</strong> Tomadas como están darían <strong>264,2 horas a la semana</strong>, más de seis jornadas por semana en una sola persona. <em>Por eso no se publican:</em> no porque se dude del trabajo, sino porque el dato de frecuencia no puede ser el que está escrito.
      <br><br>
      <strong>Lo más rentable que queda no es medir un área nueva: es confirmar esas tres frecuencias.</strong> Son datos que ya existen y hoy valen cero en la cuenta.
    </div>
  </section>

{CITAS}
  <section>
    <div class="sec-head">
      <h3>El margen por capturar</h3>
      <h2>Lo que queda sobre la mesa al cerrar</h2>
    </div>
    <p>Las cifras de este tablero salen de <strong>quince áreas</strong>. Educación entró al cierre con su primera tarea medida. Las seis restantes tienen trabajo en curso que aún no se ha traducido a tiempo antes y después, que es lo que convierte el avance en evidencia.</p>
    <ul class="faltan">
      <li><strong>Con sesiones en el programa, pendientes de medir:</strong> Planeación, Tesorería y Gerencia Financiera. <strong>Tres áreas.</strong></li>
      <li><strong>Sin sesiones en el programa:</strong> Presupuesto, Dirección Administrativa y Crédito. <strong>Tres áreas.</strong></li>
    </ul>
    <div class="note good">
      <strong>Medir es más rápido que sesionar, y mueve el resultado de inmediato.</strong> Tomar el tiempo antes y después de un proceso ya automatizado toma cuarenta minutos con el área, no una sesión nueva.
      <br><br>
      <strong>Y la fila más grande del programa sigue sin poder entrar.</strong> IPS trajo medido por el área que un proceso que les tomaba <strong>dos meses salió en cinco minutos</strong>, y el acta de su Sesión 2 pide expresamente registrarlo. Está escrita en el archivo y sin minutos, porque el acta no dice si esos dos meses son de calendario o de trabajo efectivo. <em>Una frase del área cierra la fila más valiosa que tiene el programa.</em>
    </div>
    <div class="note plain">
      <strong>Jurídica aporta 17 de las 53 tareas que sostienen la cifra</strong>, y tendría diecinueve si se confirmaran las dos de los agentes. No porque trabaje el doble, sino porque es el área que mapeó su operación completa en lugar de registrar el ejercicio del día. <strong>Ese es el estándar del programa</strong>, y se replica en una sesión de cuarenta minutos por área.
    </div>
    <div class="note plain">
      <strong>Siete áreas terminan la primera fase con agentes corriendo y sin una sola línea en el tablero por ellos.</strong> Las actas de las últimas sesiones lo dejan dicho en Comunicaciones, Agencia de Empleo, Educación, Subsidio y Jurídica: <em>la dirección lee el tablero, no las grabaciones ni las actas.</em> <strong>Lo que no esté cargado ahí, al efecto del reporte, no existe.</strong>
    </div>
  </section>

  <footer>
    <span>IAM™ Intelligence · Comfacesar</span>
    <span>Cierre de la primera fase · 13 de octubre de 2026</span>
    <span>Fuentes: archivo de assessment de productividad y actas de sesión</span>
    <span>Cálculo tarea por tarea, con la frecuencia de cada una aplicada</span>
    <span>Costo hora: tarifas de Comfacesar · horas valoradas al perfil profesional</span>
    <span>Sandra Curvelo · Founder &amp; CSO, IAM™ LATAM</span>
  </footer>

</div>

</body></html>"""

open('sala-de-control-cierre.html', 'w', encoding='utf-8').write(HTML)
print('escrito sala-de-control-cierre.html ·', len(HTML), 'bytes')
print('guiones medios:', HTML.count('—'))
print(f'{n(H)} h/sem · ${n(ANIO/1e6)} M a 12 meses · ${n(SEMANA,0)}/semana')
