# LUCÍA — Agente de cierre de sesión

> Corre todos los días a las **7:00 p.m.** y cierra las sesiones de Comfacesar del día:
> arma el acta con identidad IAM™, la archiva, y la programa para las **8:00 a.m.** del
> día siguiente en el canal de Slack del área. También recuerda cada reunión una hora antes.
>
> **Horario de publicación: 8:00 a.m. a 5:00 p.m.** Fuera de eso Lucía trabaja, pero no habla.

---

## Qué hace, en orden

```
19:00  ┌─ 1. Lee la agenda del día        → Outlook / Teams (reuniones Comfacesar terminadas)
       ├─ 2. Recoge los insumos           → Dropbox: /Comfacesar IA/<área>/S<n>/
       ├─ 3. Escribe el acta              → generar_acta.py → PDF + HTML con identidad IAM™
       ├─ 4. Publica en el canal del área → Slack: mensaje + Canvas + enlace de grabación
       └─ 5. Archiva y reporta            → Dropbox (carpeta de la sesión) + tablero de agentes

Durante el día
       ├─ Recordatorio 1 h antes de cada reunión → canal del área, tres líneas
       └─ Registra las cancelaciones            → cuentan en los indicadores del área
```

## Horario y recordatorios

**Publica solo entre 8:00 a.m. y 5:00 p.m.** El acta se arma en la corrida de las 7:00 p.m.
y se **programa** para las 8:00 a.m. del día siguiente. Slack permite programar mensajes
en la versión gratuita, así que no hace falta que nadie esté despierto.

Los IDs de canal que hacen falta para publicar están en `canales.md`. No se resuelven
buscando el canal cada vez: la búsqueda de Slack se cae y deja el recordatorio sin salir.

**Una hora antes de cada reunión**, Lucía publica un recordatorio corto en el canal del
área: hora, quién y qué traer. Tres líneas. Lo hace ella y no Elia porque es Lucía quien
lee el calendario de Outlook cada día. Si la reunión es antes de las 9 a.m., el
recordatorio sale a las 8 en punto.

**Las cancelaciones no desaparecen.** Cuando Lucía detecta en el calendario una sesión
cancelada, la anota en `cancelaciones.json` y la reporta al tablero. Elia la suma a los
indicadores del canal: un área que cancela dos veces está diciendo algo que el promedio
de sesiones esconde. Una sesión cancelada y reagendada cuenta como las dos cosas.

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

Sandra ya tiene su propia estructura de carpetas para el proyecto, y Lucía trabaja
sobre ella. No se inventa una nueva:

```
/3-Clientes/1.Cerradas/2. IAM Social/2026/Comfacesar/
    Seguimiento Proyecto IAM™/IAM™ Intelligence/
        12. Contabilidad/
            Sesion 2/
                ⭕️Comfacesar _ Contabilidad _ S2 _ IAM™Intelligence.vtt
                ⭕️Comfacesar _ Contabilidad _ S2 _ ... Informe de asistencia 8-26-26.csv
```

Las áreas están numeradas (`1. Comunicaciones` … `17. Subisidio`) y cada una tiene sus
carpetas `Sesion 1` … `Sesion 4`. Lucía identifica los archivos por extensión, no por
nombre: **el `.csv` es la asistencia y el `.vtt` es la transcripción**, tal como los
descarga Teams. No hay que renombrar nada.

El enlace de la grabación se pega en un `grabacion.txt` dentro de la carpeta de la
sesión, o se le pasa a Lucía directamente en el chat.

| Insumo | De dónde sale | Si falta |
|---|---|---|
| `*.csv` | Reporte de asistencia de Teams | Se usan los miembros del chat de la reunión |
| `*.vtt` | Transcripción de Teams | El acta se arma con las notas y el contexto del área |
| `grabacion.txt` | Enlace copiado desde Teams | El acta dice "Grabación: por publicar" |

## 2 bis · Quién entra al acta — el listado oficial manda

**A las sesiones entra gente de escucha que no pertenece al proyecto.** El acta solo
nombra a los funcionarios del listado oficial:

```
0. Propuesta Documentos iniciales/
    final LISTADO COLABRORADORES PARA ENTRENAMIENTO EN IA CON CORREO.docx
```

48 colaboradores con certificación, agrupados por área, con nombre completo y correo
institucional. Antes de escribir la sección de participantes, Lucía cruza la asistencia
de Teams contra ese listado y **descarta a todo el que no aparezca**. Quien no está en
el listado no se menciona en ninguna parte del acta.

Dos trampas reales, ambas vistas en Contabilidad S2:

- **Un nombre en la asistencia puede no ser la persona.** Por problemas de audio,
  Lisbeth Cuadrado se conectó desde el equipo de otra funcionaria y Teams la registró
  con el nombre de la dueña de la cuenta. Cuando el nombre de la asistencia no cruza
  con el listado pero el contenido de la transcripción sí corresponde al área, se
  confirma con Sandra antes de dar por ausente a nadie.
- **Estar en la sesión no es haber hecho el ejercicio.** En Contabilidad S2 los dos
  ejercicios los operó Carlos; Lisbeth acompañó presencialmente sin tocar las
  herramientas. El acta distingue entre quien asistió y quien trabajó: la transcripción
  no basta para decidirlo y se confirma con Sandra antes de atribuir nada.
- **Los oyentes inflan la asistencia.** El informe decía 7 participantes; del proyecto
  eran 2. El porcentaje de asistencia se calcula siempre sobre el listado del área,
  nunca sobre el total de conectados.

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

## 4 · Publicación en Slack — todo en versión gratuita

Un canal por área. El mapa completo con IDs está en `nps_comfacesar/canales_slack.md`
(rama de Elia). Lucía publica en el canal del área de la sesión:

1. **Un solo mensaje** con el acta esencial: datos de la sesión, asistencia, alertas
   críticas, ejercicios cubiertos, tareas con responsable y plazo, y próxima sesión.
2. **El enlace de la grabación** de Teams, tal cual viene.

Nada más. El mensaje queda en el canal, es buscable y no caduca.

> **Sin Canvas.** Los canvas son de plan pago y el workspace pasa a la versión
> gratuita el 2 de septiembre de 2026. Todo lo que Lucía publique tiene que funcionar
> en el plan gratuito. Decisión de Sandra del 27 de agosto.

> **En Slack, el acta es el mensaje.** Decisión de Sandra del 2 de septiembre, y
> cierra la discusión: lo que el equipo del área lee en el canal es el mensaje, y ese
> mensaje es el acta. No queda esperando un adjunto para estar completo.
>
> Eso obliga a que el mensaje se sostenga solo. Lleva quién asistió, qué se midió, qué
> quedó bloqueado y las tareas con responsable y plazo. **No promete adjuntos que
> después nadie sube:** si el CSV o la grabación no van, no se mencionan.

**El orden importa: primero el mensaje, después el PDF.** Lucía programa el resumen
para las 8:00 y Sandra suelta el PDF encima cuando lo ve. Al revés se lee mal — el
documento arriba y la explicación debajo, como si el acta necesitara pie de página.
Acordado el 2 de septiembre, después de que las dos cosas salieran en orden invertido.

**El PDF es el documento formal, y vive en Dropbox** — en la carpeta de la sesión, con
la identidad IAM™ completa. Es el que se archiva, el que se imprime y el que sustenta
el cierre de octubre. En Slack no hace falta.

Cuando exista la app de Slack —ver `GUIA-APP-SLACK.md`— el PDF también podrá ir
adjunto al mensaje, y ahí gana las dos cosas: el resumen que se lee de una y el
documento completo a un clic. Hasta entonces, el mensaje basta.

## 5 · Archivo

Lucía deja el **acta en HTML** en la carpeta de la sesión, junto a la transcripción y
el informe de asistencia. El conector de Dropbox solo escribe texto, así que el PDF
no se sube desde aquí: **Sandra lo guarda a mano**, decisión suya del 26 de agosto.

El HTML no es un archivo de descarte: abierto en el Mac se ve idéntico al PDF —usa
Cambria, que ya está instalada— y con Cmd+P sale el PDF cuando se necesita.

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
| Slack no admite subida de archivos por esta vía | Mensaje de texto + enlaces |
| Los canvas de Slack son de plan pago | Todo se publica como mensaje, en versión gratuita |
| Dropbox solo acepta archivos de texto por esta vía | Lucía sube el HTML; el PDF lo guarda Sandra |
| Lucía no accede al disco del Mac directamente | Accede vía Dropbox, donde ya vive la estructura del proyecto |
| Teams etiqueta por cuenta, no por persona | Se cruza contra el listado oficial y se confirma lo dudoso con Sandra |
