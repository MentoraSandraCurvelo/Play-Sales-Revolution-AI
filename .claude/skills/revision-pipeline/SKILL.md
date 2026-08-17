---
name: revision-pipeline
description: >
  Revisión operativa del pipeline comercial: qué oportunidades están vivas, cuáles
  están estancadas y qué toca hacer esta semana con cada una. Actívalo ante "revisemos
  el pipeline", "cómo va la venta", "qué prospectos tengo", "el embudo", "seguimiento
  de clientes", "¿a quién le hago seguimiento?", o cuando se pida priorizar esfuerzo
  comercial. Es una revisión semanal ligera, no una junta completa.
---

# Revisión de Pipeline IAM™

Esto es una revisión operativa, no una junta directiva. Se resuelve rápido y termina
en una lista de acciones para la semana. No convoques a toda la junta.

## Paso 1 — Leer el pipeline real

Consulta Airtable (`mcp__airtable__*`). Si no está configurado, dilo de entrada:
sin el pipeline real esta revisión es un ejercicio teórico.

Necesitas por cada oportunidad: nombre del prospecto, etapa, valor estimado, fecha
del último contacto y próximo paso comprometido.

## Paso 2 — Clasificar por temperatura, no por etapa

La etapa dice dónde está. La temperatura dice si se va a cerrar.

| Temperatura | Señal | Qué merece |
|---|---|---|
| 🔥 **Caliente** | Contacto en los últimos 7 días, próximo paso con fecha | Empujar al cierre esta semana |
| 🟡 **Tibia** | Contacto hace 8–21 días, o próximo paso sin fecha | Un movimiento concreto que la reactive |
| 🧊 **Fría** | Sin contacto hace más de 21 días | Un último intento con valor nuevo, o cerrarla |
| ⚫ **Muerta** | Sin respuesta tras dos intentos con valor | Cerrarla y decirlo |

**Cerrar oportunidades muertas es parte del trabajo.** Un pipeline inflado con
oportunidades que nadie va a cerrar impide ver el real y distorsiona cualquier
proyección de ingresos. Di cuáles hay que cerrar.

## Paso 3 — Diagnosticar dónde se rompe el embudo

Cuenta cuántas oportunidades hay en cada etapa y busca la acumulación:

- **Se acumulan en conversación** → el diagnóstico no se está haciendo, o el
  prospecto no era ICP
- **Se acumulan en propuesta** → la propuesta no está conectando el precio con el
  problema, o falta seguimiento
- **Se acumulan en negociación** → problema de valor percibido, no de precio
- **Hay pocas al inicio** → problema de generación, no de conversión

Nombra **una sola** etapa como el cuello de botella. Si dices que todo está mal, no
has diagnosticado nada.

## Paso 4 — Las acciones de la semana

Máximo **5 acciones**. Ordenadas por valor esperado (valor de la oportunidad ×
probabilidad de avanzar con esta acción).

```markdown
## ⭕ Acciones de la semana

| # | Prospecto | Acción concreta | Canal | Cuándo |
|---|---|---|---|---|
```

"Acción concreta" significa que Sandra puede ejecutarla sin pensar más: *"mandar a
X el dato de conversión de su sector y preguntar si tiene 20 minutos el jueves"*,
no *"hacer seguimiento a X"*.

## Paso 5 — Redactar los mensajes

Para las 2–3 acciones de mayor valor, **redacta el mensaje listo para enviar**.

Estructura de mensaje de LinkedIn (3 líneas, no más):
1. Referencia específica y real a su perfil, su empresa o algo que publicó
2. Puente entre su realidad y el valor de IAM™ — sin vender todavía
3. Invitación a conversar, nunca a comprar

Para follow-up: reconocer el silencio sin disculparse, aportar valor nuevo (un dato,
un insight, un recurso), y cerrar con un CTA de bajo compromiso.

**En modo lectura, entrega los mensajes redactados para que Sandra los envíe.** No
intentes enviarlos.

## Paso 6 — Registrar

Si hay memoria disponible, registra los KPIs de la revisión con
`mcp__memoria__registrar_kpi`: `prospectos_activos`, `valor_pipeline_cop`,
`tasa_conversion_pct`.

## El criterio que gobierna esta revisión

*"No se trata de sumar más prospectos, sino de convertir mejor los que ya tienes."*

Antes de recomendar prospección nueva, agota lo que ya está en el pipeline. Si aun
así recomiendas prospectar, justifica por qué la conversión actual ya llegó a su
techo.
