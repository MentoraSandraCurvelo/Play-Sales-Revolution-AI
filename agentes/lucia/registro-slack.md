# Registro de publicaciones — LUCÍA

> Lo que Lucía ha publicado o dejado programado en Slack. **Elia lee este archivo antes
> de escribir en cualquier canal**, porque Slack no permite consultar los mensajes
> programados por API: leer el canal muestra lo publicado, nunca lo que viene en camino.
>
> Se anota **al momento de programar**, no cuando sale.

## Mensajes

| Fecha | Canal | Qué | Estado |
|---|---|---|---|
| 27 ago · 12:14 | `#contabilidad` | Acta Sesión 2 | **Publicada por Sandra a mano** |
| 27 ago · 11:31 | `#cumplimiento` | Acta Sesión 1 | **Publicada por Sandra a mano** |
| 27 ago · 11:30 | `#cumplimiento` | CSV de asistencia adjunto | **Adjuntado por Sandra** |
| 28 ago · 08:00 | `#contabilidad` | Acta Sesión 2, programada | Cancelada por Sandra |
| 28 ago · 08:00 | `#cumplimiento` | Acta Sesión 1, programada | Cancelada por Sandra |
| 26 ago · 13:52 | `#contabilidad` | Acta S2 primera versión + canvas | Eliminados |
| 31 ago · 15:59 | `#educacion` | «Estoy en la sala esperándolos» — a pedido de Sandra, en el momento | **Publicado por Lucía** |
| 2 sept · 08:00 | `#juridica` | Resumen de la Sesión 3 | ⚠️ **Desactualizado** — dice que a Lilibeth le rechaza la tarjeta, y ya activó Pro |
| 2 sept · 08:01 | `#serivcios-sociales` | Resumen de la Sesión 5 | **Programado** `Dr0BU4SRNYTD` |
| 2 sept · 08:02 | `#talento-humano` | Resumen de la Sesión 2 | **Programado** `Dr0BV5FH1C6L` |
| 2 sept · 08:03 | `#contabilidad` | Resumen de la individual de Lisbeth | **Programado** `Dr0BTVP19MCP` |
| 2 sept · 08:04 | `#sub-operativa` | Resumen de la Sesión 3 | **Programado** `Dr0BU96C7WGN` |
| 2 sept · 08:05 | `#juridica` | Recordatorio · individual de Lilibeth, 9:00 | ⚠️ **Equivocado** — la movió al lunes 7. Solo Sandra lo puede borrar |
| 2 sept · 06:30 | los cinco canales | **Los cinco PDF, subidos por Sandra** | **Publicado** |
| 2 sept · 08:10 | `#juridica` | Resumen corregido de la Sesión 3 | **Programado** `Dr0BUD8ESSG6` |
| 2 sept · 09:00 | `#comunicaciones` | Recordatorio · Ambassadors con María Elvira, 10:00 | **Programado** `Dr0BUB3SPUFL` |
| 2 sept · 10:00 | `#sub-admin-y-financiera-infraestructura` | Recordatorio · individual de Rafael, 11:00 | **Programado** `Dr0BUD241LKB` |
| 2 sept · 13:00 | `#contabilidad` | Recordatorio · individual de Carlos, 14:00 | **Programado** `Dr0BU6T13DJR` |

**Las actas todavía las publica Sandra a mano.** Las dos que están en los canales las
puso ella, copiando el texto y adjuntando el CSV. Lucía ya publica mensajes de texto
—el aviso del 31 en `#educacion` salió de ella—, pero el PDF sigue sin poder subirlo:
falta la app de Slack y abrir `slack.com` en la red. Ver `GUIA-APP-SLACK.md`.

**Los avisos del momento son de Lucía.** Un «estoy en la sala esperándolos», un cambio
de hora, un «se cancela la de hoy»: eso es operación, no contenido, y lo lleva Lucía
porque es quien lee el calendario. Elia no toca esos avisos.

## Lo programado no se puede cancelar por API

El conector de Slack programa, pero **no cancela ni edita**. Un mensaje programado con
un dato que cambió solo se puede borrar desde Slack, en **Borradores y enviados**, y eso
lo hace Sandra.

Pasó el 2 de septiembre: los dos mensajes de `#juridica` quedaron obsoletos entre la
noche del martes y la mañana del miércoles, porque Lilibeth activó Claude Pro y movió su
individual al lunes 7. Se programaron el martes a las 8 p. m. con la información de esa
hora, y a las 6:30 a. m. ya no era cierta.

**La regla que sale de esto:** antes de programar de noche, leer los canales una vez más.
Y a primera hora del día siguiente, releer lo que está por salir contra lo que pasó
después. Doce horas en este proyecto alcanzan para que un dato cambie.

## Lo que Elia tiene que saber de esta tanda

**Nueve mensajes programados para el miércoles 2**, cinco resúmenes de sesión y cuatro
recordatorios. Ninguno se ve leyendo los canales: Slack no expone lo programado por API.
Antes de escribir el miércoles, Elia lee esta tabla.

**Dos canales llevan dos mensajes ese día** — `#juridica` y `#contabilidad`. Con eso se
agota el cupo del día en los dos. Elia no publica ahí el miércoles.

**Cumplimiento no lleva recordatorio** aunque la cita siga en el calendario: la sesión
del miércoles a las 4:00 p. m. está cancelada. Ver `cancelaciones.json`.

## Un adjunto sin texto se lee como un mensaje vacío

El 2 de septiembre a las 6:30 Sandra subió los cinco PDF, uno por canal, sin escribir
nada en el mensaje. Al leer el canal en formato conciso, el conector devolvió cinco
mensajes con texto vacío y Lucía los reportó como enters sueltos. **No lo eran: eran
las actas.**

Para ver los adjuntos hay que leer el canal en formato `detailed`. Antes de decir que un
mensaje está vacío, releerlo así.

## Actas listas, sin publicar

| Sesión | Fecha | Canal | Estado |
|---|---|---|---|
| Servicios Sociales S4 — individual de Juan Pablo | 27 ago | `#serivcios-sociales` | Acta lista · pendiente del visto bueno |
| Jurídica S3 | 31 ago | `#juridica` | **Nueva** · pendiente del visto bueno |
| Servicios Sociales S5 | 31 ago | `#serivcios-sociales` | **Nueva** · pendiente del visto bueno |
| Talento Humano S2 | 1 sept | `#talento-humano` | **Nueva** · pendiente del visto bueno |
| Contabilidad S3 — individual de Lisbeth | 1 sept | `#contabilidad` | **Nueva** · pendiente del visto bueno |
| Sub. Operativa y Comercial S3 | 1 sept | `#sub-operativa` | **Nueva** · pendiente del visto bueno |

Las cinco nuevas se armaron en la corrida del 1 de septiembre por la noche, en cuanto
los CSV y los VTT aparecieron en Dropbox. A las cinco les falta lo mismo: **el enlace
de la grabación**, que hoy dice «pendiente» en la tabla de datos de la sesión.

## Canales reservados

Ninguno vigente. Las reservas del 28 al 30 de agosto vencieron.

## Cómo se usa

Antes de publicar, cualquiera de las dos:

1. Lee `agentes/CONTRATO-SLACK.md` — el reparto de quién dice qué.
2. Lee el registro de la otra, **incluido lo programado**.
3. Lee los últimos cinco mensajes del canal.
4. Publica y lo anota aquí en la misma corrida.

Un mensaje programado que se cancela se marca como cancelado, no se borra de la tabla:
el historial de lo que no salió también explica el canal.
