# El circuito de una sesión

**Desde que termina la reunión hasta que la sesión está cerrada.** Seis pasos, en este orden.

## 1 · Llegan los insumos

De cada sesión quedan tres archivos en la carpeta del cliente:

| Archivo | Qué trae |
|---|---|
| La transcripción `.vtt` | Todo lo que se dijo, con marca de tiempo |
| El informe de asistencia `.csv` | Quién entró, a qué hora, cuántos minutos |
| La grabación | El enlace que genera quien organizó la reunión |

**El informe de asistencia manda sobre la memoria.** La duración real de la sesión, quién
asistió y cuánto tiempo estuvo salen de ahí, no de la impresión de nadie.

_Ojo con los duplicados:_ **una misma persona puede aparecer dos o tres veces** porque se
conectó desde el computador y desde el teléfono, o porque se le cayó la conexión. Dos
entradas con el mismo nombre son la misma persona, no dos. Y un nombre con un número al
final suele ser el segundo equipo de alguien.

## 2 · Se lee la transcripción entera

**Entera, no por encima.** El valor del acta está en los detalles que solo aparecen leyendo:
la pregunta que alguien hizo y nadie respondió, el número que el área soltó de pasada, el
momento en que la herramienta avisó de algo que nadie le preguntó.

## 3 · Se escribe el acta

El JSON de la sesión, con la estructura de `02-el-acta.md`. **Nombre del archivo:**
`<area>-s<numero>-<fecha>.json`.

Y se genera el documento:

```bash
python3 generar_acta.py sesiones/<area>-s<numero>-<fecha>.json
```

**Antes de generar, se cuenta:** cero guiones medios en el archivo. _Si hay uno, se quita._

## 4 · Sale la grabación

Primero la grabación, en el espacio del cliente, con el enlace tal como viene.

## 5 · Sale el resumen

Después el resumen. **El orden importa y se acordó el 2 de septiembre:** primero el texto,
después el documento. _Al revés se lee mal, como si el acta necesitara pie de página._

## 6 · Sube el acta en PDF

**En Hello la sube el agente.** _En Slack no se podía y le tocaba a Sandra: el servidor de
archivos de Slack está bloqueado desde donde corre el agente._ Ese paso desaparece.

**El PDF se sube una sola vez y no se vuelve a tocar.** No se le mete dentro el enlace de la
grabación: obliga a regenerarlo y a reemplazarlo en todos lados, y el equipo busca la
grabación en el espacio, no dentro del PDF. _Se intentó el 2 de septiembre y se devolvió el
mismo día._

## Y al final del día

**Se verifica sin que nadie lo pida:** de las sesiones de hoy, cuáles tienen las tres cosas
y cuáles no. **Lo que falte se cierra ese mismo día.**
