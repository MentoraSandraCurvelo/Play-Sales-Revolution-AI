# El archivo propio de Slack

> **El espacio `iamteamespacio` está en plan gratuito.** Los mensajes de más de **90 días se ocultan**
> y a partir del **año se borran de verdad**. Todo el historial del programa —actas, resúmenes,
> grabaciones, avisos, respuestas de las áreas— vive ahí. *Este archivo es el seguro.*

**Las fechas que importan.** Los primeros mensajes del programa son del **11 de agosto de 2026**:
se ocultan alrededor del **9 de noviembre de 2026** y cumplen el año el **11 de agosto de 2027**.
*Lo oculto vuelve a aparecer si el espacio pasa a plan pago; lo borrado, no.*

## Cómo entra la información

**Sandra baja el export; Lucía lo carga.** _Esa es la división y no cambia_ — el export solo lo puede
pedir la propietaria del espacio.

| Paso | Quién | Qué |
|---|---|---|
| 1 | **Sandra** | Abre https://iamteamespacio.slack.com/services/export y pide el export |
| 2 | **Sandra** | Cuando llega el correo de Slack, baja el ZIP y lo sube a Dropbox, carpeta del proyecto |
| 3 | **Sandra** | Le avisa a Lucía |
| 4 | **Lucía** | Carga el ZIP, normaliza por canal y fecha, actualiza el archivo y republica la web app |

**Cadencia: mensual, el 2 de cada mes.** *Nunca más de 30 días de distancia, y siempre dentro de los
90 días visibles.*

## Los dos recordatorios

| Dónde | Qué es | Detalle |
|---|---|---|
| **Google Calendar** | Evento mensual recurrente, el 2 a las 7:30 a. m. | `RRULE:FREQ=MONTHLY;BYMONTHDAY=2` · aviso 10 min antes y correo el día anterior · lleva el paso a paso dentro |
| **Routine de Claude** | `trig_01VwFuBBuwHiUsFeLGAckZY4` · el 2 a las 7:22 a. m. | Despierta una sesión que le escribe a Sandra · aviso al teléfono y al correo |

**No se pudo dejar en Outlook.** *El conector de Microsoft 365 de esta sesión es de solo lectura del
calendario* — tiene `Calendars.Read`, no `Calendars.ReadWrite`. **Por la misma razón, Lucía tampoco
puede corregir los títulos de los eventos del calendario de trabajo:** eso lo hace Sandra.

## Límite de la Routine, y cómo se levanta

**La rutina no lleva conectores**, así que la sesión que despierta **no puede entrar a Dropbox ni a
Slack por su cuenta.** *Se intentó dárselos y el parámetro no está habilitado para la organización.*

_Mientras siga así, la rutina sirve de recordatorio y la carga la hace Lucía cuando Sandra le
escribe._ **Para que la haga sola, hay que recrear la rutina desde la pantalla de Routines en
claude.ai**, donde Sandra le asigna Slack y Dropbox a mano.

## Qué trae el export y qué no

**Trae** los mensajes completos de **todos los canales públicos** — los 19 del programa lo son.

**No trae** los archivos, solo sus enlaces, y solo los de los últimos 90 días. *Las grabaciones están
en SharePoint y las actas en Dropbox*, así que el contenido no se pierde — **pero conviene revisar
que los enlaces queden.**

**No trae** mensajes directos ni canales privados. _Si algo importante se habló por privado, no está._

## La web app

**Archivo propio, con lector de canales por fecha y buscador.** *Privada* — ahí hay nombres reales y
datos internos del cliente, así que **no se comparte el enlace** y se rige por lo mismo que el
tablero de agentes.

*Se construye cuando llegue el primer ZIP.* **El enlace fijo se anota aquí en cuanto exista.**
