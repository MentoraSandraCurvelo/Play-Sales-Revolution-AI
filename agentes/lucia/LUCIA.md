# LUCÍA — Agente de cierre de sesión

> Corre todos los días a las **7:00 p.m.** y cierra las sesiones de Comfacesar del día:
> arma el acta con identidad IAM™, la publica en el canal de Slack del área y la archiva.

---

## Qué hace, en orden

```
19:00  ┌─ 1. Lee la agenda del día        → Outlook / Teams (reuniones Comfacesar terminadas)
       ├─ 2. Recoge los insumos           → Dropbox: /Comfacesar IA/<área>/S<n>/
       ├─ 3. Escribe el acta              → generar_acta.py → PDF + HTML con identidad IAM™
       ├─ 4. Publica en el canal del área → Slack: mensaje + Canvas + enlace de grabación
       └─ 5. Archiva y reporta            → Dropbox (carpeta de la sesión) + tablero de agentes
```

## 1 · Detección de sesiones

Fuente: `outlook_calendar_search` + `teams_list_chats`.

Las sesiones del programa siguen esta nomenclatura en el calendario, y de ahí sale todo:

```
⭕️Comfacesar | Vivienda S4 | IAM™Intelligence
⭕️Comfacesar | Subsidio | S1 IAM™Intelligence
⭕️Comfacesar | Mercadeo Manuel Jose | S3 IAM™Intelligence sesion individual
            └── área ──┘  └ sesión ┘              └── individual vs. grupal ──┘
```

De cada reunión se extrae: **área**, **número de sesión**, fecha, hora de inicio,
duración real, modalidad y lista de invitados.

## 2 · Insumos — la carpeta de Dropbox

Sandra deja en Dropbox lo que descarga de Teams al terminar cada reunión.
Dropbox tiene respaldado el Mac (`Mi Mac (MacBook-Air-de-Sandra.local)`), así que
**guardar en el escritorio es suficiente**: Lucía lo ve desde ahí.

```
/Mi Mac (MacBook-Air-de-Sandra.local)/Desktop/Comfacesar IA/
└── Subsidio/
    └── S1_2026-08-24/
        ├── asistencia.csv        ← Teams › Asistencia › Descargar
        ├── transcripcion.vtt     ← Teams › Grabación › Transcripción › Descargar
        ├── grabacion.txt         ← el enlace de la grabación, pegado tal cual
        └── notas.txt             ← (opcional) apuntes de Sandra
```

Ninguno es obligatorio. Con lo que haya, Lucía arma el acta y marca lo que falta
como `Por confirmar`, igual que en el acta de referencia.

| Insumo | De dónde sale | Si falta |
|---|---|---|
| `asistencia.csv` | Reporte de asistencia de Teams | Se usan los miembros del chat de la reunión |
| `transcripcion.vtt` | Transcripción de Teams | El acta se arma con las notas y el contexto del área |
| `grabacion.txt` | Enlace de la grabación | El acta dice "Grabación: por publicar" |

## 3 · El acta

`generar_acta.py` toma un JSON con los datos de la sesión y produce el HTML y el PDF
con la identidad IAM™ exacta, en 9 secciones:

| # | Sección | De dónde sale |
|---|---|---|
| 01 | Datos de la sesión | Calendario + duración real |
| 02 | Participantes y diagnóstico | `asistencia.csv` o miembros del chat |
| 03 | Mapa de calor — riesgos | Análisis de la transcripción |
| 04 | Alertas críticas | Bloqueadores detectados en sesión |
| 05 | Ejercicios cubiertos | Lo que se hizo, paso a paso |
| 06 | Oportunidad estratégica | Necesidades de negocio que aparecen en la conversación |
| 07 | Tareas para la próxima sesión | Compromisos con responsable y plazo |
| 08 | Observaciones | Contexto que no cabe en las tablas |
| 09 | Próxima sesión | Condición de entrada y agendamiento |

La franja de KPIs de la cabecera (participantes, asistencia, ejercicios, tareas,
alertas, oportunidad) se calcula sola a partir de las secciones.

```bash
python3 agentes/lucia/generar_acta.py agentes/lucia/sesiones/subsidio-s1-2026-08-24.json
```

**Identidad visual** — extraída del acta de referencia, no inventada:

| Elemento | Valor |
|---|---|
| Rojo institucional | `#B71C1C` |
| Nivel ALTO | `#BF360C` |
| Nivel MEDIO | `#E65100` |
| Nivel BAJO | `#2E7D32` |
| Fondo de tablas | `#F5F5F5` |
| Barras de oportunidad | `#1A1A1A` |
| Tipografía | Cambria (Caladea como equivalente libre, métricas idénticas) |

## 4 · Publicación en Slack

Un canal por área. El mapa completo con IDs está en `nps_comfacesar/canales_slack.md`
(rama de Elia). Lucía publica en el canal del área de la sesión:

1. **Mensaje** con el resumen ejecutivo: asistencia, alertas críticas, tareas y plazos.
2. **Canvas** con el acta completa, legible dentro de Slack sin descargar nada.
3. **Enlace de la grabación** de Teams, tal cual viene.
4. **Enlaces** al PDF y al `.docx` en Dropbox.

> La conexión de Slack envía mensajes y crea Canvas, pero **no sube archivos**.
> Por eso el acta va como Canvas + enlaces, no como adjunto.

## 5 · Archivo

El PDF, el HTML y el JSON vuelven a la carpeta de la sesión en Dropbox. Como Dropbox
sincroniza con el Mac, quedan en el escritorio de Sandra sin que ella haga nada.

## 6 · Reporte al tablero

Al terminar, Lucía escribe una línea en el registro de agentes: qué sesiones cerró,
cuáles quedaron pendientes de insumos y qué publicó. Es lo que alimenta el tablero.

---

## Límites conocidos

| Límite | Estado |
|---|---|
| No existe evento "la reunión terminó" | Se resuelve con la corrida de las 7:00 p.m. |
| El reporte de asistencia de Teams no se descarga por API | Sandra lo baja a Dropbox; automatizable con Microsoft Graph si TI aprueba |
| El recap de IA de Teams no es descargable | Lucía escribe el resumen desde la transcripción — sale mejor y no depende de licencia Copilot |
| Slack no admite subida de archivos por esta vía | Canvas + enlaces de Dropbox |
| Lucía no accede al disco del Mac directamente | Accede vía Dropbox, que respalda el escritorio |
