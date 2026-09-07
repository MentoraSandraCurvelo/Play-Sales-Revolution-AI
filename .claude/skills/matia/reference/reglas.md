# Reglas de puntuación de matIA

Este es el motor. Todo puntaje del informe se puede reconstruir sumando estas
líneas, no hay caja negra. Si Sandra pregunta por qué un correo quedó en P1,
la respuesta se arma con esta tabla.

## Suma de puntos

### Quién escribe, lo que más pesa

| Condición | Puntos | Nota |
|---|---:|---|
| Está en `clientes_conocidos` | **+50** | Gana sobre todo lo demás, incluso si escribe desde Gmail |
| Está en `prospectos` | +30 | Conversación comercial abierta |
| Dominio corporativo propio, ejemplo `@bancoxyz.com.co` | **+25** | La regla que pidió Sandra |
| Dominio gratuito, gmail, hotmail, outlook, yahoo | **+8** | Segundo lugar por decisión de Sandra |
| Remitente automático, no-reply, notifications, mailer | −25 | No penaliza si es cliente |
| Dominio propio de Sandra | 0 | Correo interno, no es cliente |

### De qué se trata

| Condición | Puntos |
|---|---:|
| Categoría FACTURAS Y PAGOS | +18 |
| Categoría AGENDAR | +15 |
| Categoría CLIENTES Y OPORTUNIDADES | +15 |
| Señal de urgencia en asunto o cuerpo | +12 |
| Palabra de ruido, promoción, unsubscribe, boletín | −20 |

### Estado del hilo

| Condición | Puntos |
|---|---:|
| Sin leer | +5 |
| Responde un hilo que Sandra inició | +10 |
| Más de 48 horas sin respuesta de Sandra, siendo cliente, prospecto o corporativo | +10 |

## Cortes de prioridad

| Nivel | Puntaje | Compromiso |
|---|---:|---|
| P1 CRÍTICO | 60 o más | Hoy mismo |
| P2 ALTO | 35 a 59 | 24 a 48 horas |
| P3 NORMAL | 10 a 34 | Esta semana |
| P4 RUIDO | menos de 10 | Bloque semanal |

Todos los cortes viven en `config/matia.config.json`, campo `umbrales`. Se
ajustan sin tocar el código.

## Cuándo matIA levanta la mano

Un correo entra a la sección REVISAR cuando cumple una de estas, y además es
P1 o P2:

- El puntaje quedó a 6 puntos o menos de un umbral. Un correo de 58 no es
  distinto de uno de 61, y fingir que sí lo es sería deshonesto.
- Dos categorías empataron en coincidencias.
- El remitente tiene dominio corporativo, escribe de dinero o de propuestas,
  y no está en la lista de clientes. Muy probablemente es un cliente que falta
  registrar, o un prospecto caliente.
- Solo se leyó el snippet y no el cuerpo completo.

## Limitaciones conocidas, dichas de frente

1. **Un prospecto real desde Gmail cae a P3.** Es consecuencia directa de la
   regla que Sandra pidió. Ejemplo real de la prueba: alguien que escribe
   desde gmail.com pidiendo información de mentoría suma 28 puntos y queda en
   P3. Si eso incomoda, hay dos salidas, subir `dominio_gratuito` de 8 a 20,
   o registrar ese correo en `prospectos`. Recomiendo lo segundo, es más
   preciso y no degrada la regla general.

2. **Correos operativos con remitente tipo soporte@ caen a ruido.** Una
   renovación de dominio de GoDaddy es operativa y real, pero el penalizador
   de remitente automático la hunde. Si hay proveedores críticos, se agregan
   a `prospectos` o se les crea una lista blanca propia.

3. **La categoría sale de palabras clave, no de comprensión semántica.** Un
   asunto creativo tipo "sobre lo que hablamos" no matchea nada y cae en sin
   clasificar. Por eso el informe siempre muestra ese bloque, no lo esconde.

4. **La búsqueda de Gmail devuelve solo los mensajes más antiguos de cada
   hilo y no avisa que truncó.** Es una limitación documentada de la
   herramienta. Por eso todo P1 y P2 exige leer el hilo completo antes de
   resumirlo.
