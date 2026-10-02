# Handoff: IAM™ Intelligence · Archivo Comfacesar (v2, 3D)

## Qué es
Nueva interfaz del archivo mensual del espacio de Slack IAM™Team (cliente Comfacesar). Sustituye la plantilla anterior (`IAM-archivo-comfacesar.html`). **Los datos no cambian**: la app lee el mismo objeto `window.ARCHIVO` que ya genera el agente.

## Cómo conectarlo con el agente de Claude Code
1. Copia esta carpeta dentro del repo del agente, por ejemplo en `plantilla_v2/`.
2. Abre Claude Code en ese repo y pídele:
   > Lee `plantilla_v2/README.md`. Actualiza el agente para que, al generar el archivo mensual, use esta plantilla en lugar de la anterior: escribe el JSON en `data/archivo.js` como `window.ARCHIVO = {...};` y produce un único HTML autocontenido con todo inlined (support.js, lib/iam.js, data/archivo.js). Mantén three.js desde CDN.
3. El agente solo tiene que **reemplazar `data/archivo.js`** cada mes. El resto de archivos es fijo.

### Salida esperada: un solo HTML
El agente debe producir un HTML único con:
- El contenido de `support.js`, `lib/iam.js` y `data/archivo.js` en `<script>` inline (en ese orden, antes del componente).
- Fuentes Geist / Geist Mono (Google Fonts) y three.js 0.160 (`https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js`). Si debe funcionar sin internet, descargar e incrustar también estos dos recursos.

Alternativa sin cambiar nada de lógica: servir la carpeta tal cual (`IAM Archivo.dc.html` + `support.js` + `lib/` + `data/`) en SharePoint o cualquier hosting estático.

## Archivos
- `IAM Archivo.dc.html`: la app (plantilla + lógica). Abrible directo en el navegador.
- `support.js`: runtime del componente. No editar.
- `lib/iam.js`: utilidades (formato Slack→HTML, fechas en español, iniciales/colores de avatar, escena 3D del hero `hero3D`).
- `data/archivo.js`: **lo único que cambia cada mes.** Ejemplo real con los datos de septiembre 2026.

## Contrato de datos (`window.ARCHIVO`)
```
espacio, cliente, programa: string
semanas: ["2026-08-03", ...]            // inicio de cada semana (ISO)
pulso: [int]                           // mensajes por semana (mismo largo que semanas)
pulso_actas: [int]                     // actas por semana
n_grabaciones: int
generales: [{url, titulo, nota}]       // enlaces fijados del programa
personas: [{nombre, correo, mensajes, canales:[canal]}]
asistencia: [{nombre, cargo, correo, minutos, n, canales:[canal],
              sesiones:[{fecha, canal, sesion, minutos}]}]   // sesiones de más reciente a más antigua
mentoria: [mismo formato que asistencia]
sesiones_informe: [...]                // informes de Teams guardados (solo se cuenta su longitud)
canales: [{
  canal (slug), nombre, conteo, conteo_total, desde, hasta (ISO),
  pulso: [int],                        // por semana
  adjuntos: int,
  fijados: [{titulo, icono, enlaces:[{url, titulo, nota}]}],
  grabaciones: [{titulo, url, fecha, sesion, acta:bool}],
  mensajes: [{ts, fecha, hora, uid, autor, texto (mrkdwn de Slack), sistema:bool,
              adjuntos:[{nombre, tipo, peso}], hilo:{respuestas}|null,
              reacciones:[{emoji, cuenta}]}],
  actas: [{archivo (id único), area, area_completa, sesion_num, fase, iso, fecha,
           subtitulo_meta, prevista, pdf, grabacion,
           kpis:[{valor, etiqueta, detalle}],
           datos_sesion:[[campo, valor]] | [{campo, valor}],
           participantes:[string | {nombre, cargo, asistio}],
           informe:{duracion_min, media_min, participantes:[{nombre, rol, minutos}]},
           alertas / riesgos:[string | {num, nivel, titulo, descripcion}],
           ejercicios:[string | {titulo, duracion, modalidad, objetivo, pasos, resultado}],
           oportunidades:[string | {encabezado, titulo, descripcion, barras}],
           tareas_intro, tareas:[string | {tarea, responsable, plazo, prioridad}],
           observaciones:[string], proxima_sesion:{sesion, fecha, hora, condiciones, agenda, nota}}]
}]
```
Campos opcionales: si faltan, la sección no se muestra.

## Vistas
- **Resumen**: hero 3D (anillo IAM™ de partículas; cada canal es un satélite clicable), 4 KPIs con contador, ticker de últimos mensajes, gráfico de pulso semanal (línea + barras de actas), donut de actas por fase, mapa de calor canal × semana, top 7 de asistencia, tarjetas de canales con sparkline.
- **Canal** (`#/<canal>/<pestaña>`): Mensajes (agrupados por día) · Actas · Grabaciones · Fijados · Archivos. Acta individual: `#/<canal>/actas/<archivo>`.
- **Globales**: `#/actas` (filtro por fase), `#/grabaciones`, `#/asistencia`, `#/asistencia/<i>`, `#/personas`, `#/archivos`.
- **Búsqueda**: ⌘K / Ctrl+K o `/`. Canales, actas, personas y mensajes.
- Tema claro/oscuro (guardado en `localStorage` clave `iam-tema-v2`). Por debajo de 900 px el menú lateral pasa a cajón.

## Identidad (alta fidelidad)
- Rojo IAM `#C00000` (acentos `#E01010`, `#FF3B30`, `#7A0000`), negro `#060607`, blanco `#F5F5F7`.
- Tipografía Geist (300–800) y Geist Mono para etiquetas y cifras.
- Radios 14–26 px, bordes `rgba(255,255,255,.08)`, vidrio con `backdrop-filter: blur`.
- Animaciones: entrada `up` .5–.7 s `cubic-bezier(.32,.72,0,1)`, inclinación 3D de tarjetas con el cursor, View Transitions entre vistas.
