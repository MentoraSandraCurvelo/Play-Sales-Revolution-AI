# Quién publica qué en Slack

> Regla que obliga a **Lucía** y a **Elia**. Las dos escriben en los mismos canales
> con la misma identidad —el equipo de Comfacesar solo ve "IAM"—, así que dos mensajes
> descoordinados no se leen como dos agentes: se leen como Sandra repitiéndose.

## El choque que originó esta regla

El 26 de agosto, en `#contabilidad`, tres mensajes en cuatro horas:

| Hora | Agente | Mensaje |
|---|---|---|
| 13:01 | Elia | "Ya quedó agendada la sesión 3" — la individual de Lisbeth |
| 13:52 | Lucía | El acta de la Sesión 2 |
| 17:21 | Elia | "Carlos, la tuya quedó para el miércoles" |

Los dos de Elia decían lo mismo partido en dos, y el acta de Lucía ya traía las dos
fechas. Ese mismo día, en `#comunicaciones`, Elia publicó el mismo texto dos veces
con cuatro minutos de diferencia.

## El reparto

|  | **LUCÍA** | **ELIA** |
|---|---|---|
| **De qué habla** | Lo que ya pasó | Lo que falta que pase |
| **Cuándo** | Después de una sesión ejecutada | Cuando un área lleva días en silencio |
| **Qué publica** | El acta: asistencia, alertas críticas, tareas con responsable y plazo, próxima sesión y grabación | Alertas de áreas rezagadas, pulso NPS, avance del programa |
| **Disparador** | La corrida de las 7:00 p.m. | Días sin sesión y el calendario de medición |
| **Frecuencia** | Un mensaje por sesión ejecutada | Máximo uno por canal por semana |

## Las seis reglas

**1 · Una sesión, un mensaje.** El acta de Lucía ya dice cuándo es la próxima sesión.
Elia no anuncia agendamientos de un área que acaba de tener sesión: eso ya lo dijo el acta.

**2 · Ventana de silencio de 48 horas.** Cuando Lucía publica un acta en un canal,
Elia no escribe en ese canal durante las 48 horas siguientes.

**3 · Elia solo habla del silencio.** Si un área tuvo sesión en los últimos 7 días,
Elia no la toca. Su trabajo es la que lleva 6 días quieta, no la que acaba de avanzar.

**4 · Máximo dos mensajes por canal por día, entre las dos.** Un tercer mensaje el
mismo día en el mismo canal se aplaza al día siguiente, sea de quien sea.

**5 · Leer antes de escribir.** Las dos leen los últimos cinco mensajes del canal antes
de publicar. Si el tema ya está cubierto, no se publica: se ajusta o se descarta.

**6 · Una sola voz.** El equipo del cliente no debe notar que son dos agentes. Nada de
firmas, nada de "según el agente de seguimiento". Es la voz de Sandra, y punto.

## Zona gris: los agendamientos

Es donde más chocan. Se resuelve así:

- El área **tuvo sesión** → la próxima fecha va dentro del acta de Lucía. Elia calla.
- El área **no ha tenido sesión** o no tiene la siguiente agendada → es de Elia.

## Cómo se aplica

Este archivo es la fuente de verdad. Antes de publicar en Slack, cada agente lo lee.
Elia trabaja en la rama `claude/nps-survey-slack-comfacesar-h5ekyh` y Lucía en
`claude/agente-lucia-teams-slack-ccqzne`: el contrato tiene que existir en las dos.
