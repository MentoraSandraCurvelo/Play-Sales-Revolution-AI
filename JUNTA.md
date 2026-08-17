# ⭕ Junta Directiva Agéntica IAM™

Un sistema multi-agente que funciona como junta directiva del negocio de Sandra
Curvelo: ocho consejeros especializados deliberan sobre asuntos reales, consultan los
sistemas del negocio a través de conectores, discrepan entre ellos, y dejan la
decisión registrada con responsable, fecha y métrica.

No es un chatbot que responde preguntas. Es una junta: encuadra el asunto, convoca a
quien corresponde, confronta posiciones, pasa por un contradictor y decide.

---

## Los consejeros

| Consejero | Responsabilidad | Su criterio de decisión |
|---|---|---|
| `cfo-finanzas` | Márgenes, flujo de caja, pricing, ROI, viabilidad | Se defiende lo que mejora margen neto o ingreso recurrente |
| `cro-comercial` | Pipeline, prospección, conversión, propuestas | Convertir mejor antes que prospectar más |
| `cmo-marca` | Posicionamiento, contenido, narrativa IAM™ | Alcance sin conversación comercial es vanidad |
| `coo-operaciones` | Procesos, capacidad, entrega, herramientas | Eliminar > automatizar > delegar > optimizar |
| `legal-colombia` | Contratos, habeas data, PI, DIAN, riesgo legal | Riesgo cuantificado, no precaución genérica |
| `cdo-ia-datos` | IA aplicada, calidad de datos, instrumentación | La IA amplifica método, no lo reemplaza |
| `contradictor` | Buscar por qué la decisión puede fallar | Máximo 3 objeciones, cada una con qué la resolvería |
| `secretaria-junta` | Acta, acuerdos y memoria histórica | Un acuerdo sin responsable y fecha no es un acuerdo |

La **presidencia** (el agente principal) decide a quién convocar. Para preguntas
simples responde sola; no monta una junta de ocho personas para una pregunta de una
línea.

---

## Arranque rápido

```bash
# 1. Dependencias
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 2. Credenciales
cp .env.example .env      # y completa lo que tengas

# 3. Revisa qué quedó configurado
.venv/bin/python -m junta.cli --diagnostico

# 4. Úsala
.venv/bin/python -m junta.cli                       # sesión interactiva
.venv/bin/python -m junta.cli "¿Subo el precio?"    # una consulta
.venv/bin/streamlit run app_junta.py                # interfaz web
```

Lo único obligatorio es `ANTHROPIC_API_KEY` (o tener sesión iniciada en la CLI de
Claude Code, que el SDK reutiliza). **Todo conector que falte simplemente no se
monta**: la junta arranca igual y te dice qué le falta y qué no podrá sostener con
datos por esa carencia.

---

## Arquitectura

```
   Presidencia (claude-opus-5)
   │  encuadra · convoca · confronta · decide
   │
   ├── 8 consejeros como subagentes, cada uno con su propio
   │   prompt, modelo y acceso acotado a conectores
   │
   ├── contexto/*.md ──────────► prompt de sistema
   │
   ├── conectores MCP
   │     Airtable · Notion         (stdio, servidores externos)
   │     Gmail+Drive · WhatsApp    (in-process, este repo)
   │     Meta · memoria            (in-process, este repo)
   │
   └── Supabase ──────────────► decisiones, acuerdos, KPIs, transcripción
```

| Archivo | Qué hace |
|---|---|
| `junta/junta.py` | Orquestador: arma opciones, delibera, emite eventos |
| `junta/consejeros.py` | Los 8 consejeros y el prompt de la presidencia |
| `junta/contexto.py` | Carga `contexto/*.md` y detecta datos faltantes |
| `junta/config.py` | Configuración desde entorno; qué conectores hay |
| `junta/conectores/` | Servidores MCP y su ensamblado |
| `junta/memoria/` | Esquema SQL y repositorio de Supabase |
| `.claude/skills/` | Protocolos reutilizables (junta, tablero, pipeline, acta) |
| `app_junta.py` | Interfaz Streamlit |

---

## El contexto es lo que hace útil a la junta

`contexto/` es la fuente de verdad. Todos los `.md` de esa carpeta entran al prompt de
sistema; si añades un archivo nuevo, entra solo en la siguiente sesión.

Ya está sembrada con lo que se pudo extraer de tus skills (marca, oferta, audiencias,
benchmarks financieros), pero **31 datos están marcados como pendientes**:

```
> ⚠️ POR COMPLETAR: ingreso mensual promedio de los últimos 6 meses
```

Los consejeros están instruidos para **no inventar** ningún dato marcado así. Si
necesitan uno, lo buscan en los conectores y, si no aparece, lo piden. Completar esos
31 datos es lo que más sube la calidad de las decisiones — más que cualquier ajuste
técnico.

Ver `contexto/README.md` para el detalle.

---

## Memoria en Supabase

Antes de la primera sesión, ejecuta `junta/memoria/schema.sql` en el SQL Editor de
Supabase. Crea seis tablas:

| Tabla | Guarda |
|---|---|
| `junta_sesiones` | Cada sesión de junta |
| `junta_mensajes` | La transcripción completa |
| `junta_decisiones` | Decisiones formales, con sus desacuerdos |
| `junta_acuerdos` | Acuerdos con responsable, fecha y métrica |
| `junta_kpis` | Serie histórica de indicadores del negocio |
| `junta_datos_faltantes` | Lo que la junta necesitó y no tenía |

Con memoria activa, cada sesión abre consultando qué se acordó antes y **avisa si lo
que se propone hoy contradice una decisión anterior**.

Las tablas tienen RLS activado sin políticas permisivas: la clave `anon` no lee nada.
La junta se conecta con la **service role key**, que debe vivir solo en el `.env` del
servidor. Nunca en el navegador ni en el repositorio.

---

## Conectores

| Conector | Tipo | Qué puede hacer |
|---|---|---|
| **Airtable** | stdio (`airtable-mcp-server`) | Leer y escribir el pipeline, clientes, propuestas |
| **Notion** | stdio (`@notionhq/notion-mcp-server`) | Leer y escribir procesos y documentación |
| **Gmail** | in-process | Buscar, leer y enviar correo |
| **Drive** | in-process | Buscar, leer y crear documentos |
| **WhatsApp** | in-process | Enviar mensajes y plantillas, ver plantillas y perfil |
| **Meta** | in-process | Métricas de página, publicaciones, campañas; publicar |
| **Memoria** | in-process | Decisiones, acuerdos, KPIs, datos faltantes |

Los conectores de Airtable y Notion se descargan con `npx` al arrancar, así que hace
falta Node.js en el sistema.

**Nota sobre WhatsApp:** la Cloud API de Meta solo permite *enviar*. Los mensajes
entrantes llegan por webhook y no hay endpoint para leer el historial, así que el
conector no ofrece una herramienta de lectura de conversaciones — prometerla sería
engañar al agente. Si quieres que la junta lea entrantes, la vía es:
webhook → guardar en Supabase → consultarlo desde la memoria.

---

## Modo lectura y modo ejecución

Por defecto la junta está en **modo lectura**: lee de todos los conectores pero no
envía nada hacia afuera. Cuando una decisión implica un envío, redacta el contenido
propuesto y lo entrega para revisión.

```bash
.venv/bin/python -m junta.cli --ejecutar "..."   # habilita envíos
```

En modo ejecución puede enviar WhatsApp, enviar correos y publicar en Meta. En la
interfaz Streamlit es un interruptor en la barra lateral.

Este es el valor por defecto a propósito: una junta directiva delibera y recomienda;
ejecutar hacia el exterior es una decisión de Sandra.

---

## Skills

En `.claude/skills/` viven los protocolos que la junta carga cuando el asunto lo pide:

| Skill | Se activa cuando |
|---|---|
| `sesion-de-junta` | El asunto tiene consecuencias de dinero, tiempo o marca |
| `tablero-kpi` | Se piden los indicadores, el cierre del mes o el dashboard |
| `revision-pipeline` | Revisión semanal del embudo y seguimiento comercial |
| `acta-de-junta` | Levantar acta, registrar decisión, o recuperar una anterior |

Se cargan solas por su descripción. También puedes pedirlas por nombre.

---

## Coste y modelos

Todos los consejeros corren en `claude-opus-5` con esfuerzo `high`. Para abaratar:

```bash
JUNTA_MODELO_CONSEJEROS=claude-sonnet-5
JUNTA_ESFUERZO=medium
```

La presidencia conviene dejarla en Opus: es quien confronta posiciones y decide.

---

## La app del juego

`app.py` (el desafío *Sales Revolution AI*) sigue intacta y se ejecuta aparte con
`streamlit run app.py`. La junta vive en `app_junta.py`.
