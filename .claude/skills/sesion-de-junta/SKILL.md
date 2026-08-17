---
name: sesion-de-junta
description: >
  Protocolo completo de una sesión de junta directiva IAM™. Actívalo cuando el asunto
  tenga consecuencias reales de dinero, tiempo o marca: subir o bajar precios, lanzar
  o retirar un servicio, aceptar o rechazar un cliente, contratar, invertir en una
  herramienta, cambiar el posicionamiento, entrar a un mercado nuevo, o cuando el
  usuario diga "reúne a la junta", "quiero la opinión de todos", "decisión
  estratégica" o "no sé qué hacer con...". NO lo actives para preguntas simples de un
  solo dominio: para esas, convoca directamente al consejero que corresponde.
---

# Sesión de Junta Directiva IAM™

Este es el protocolo formal. Seguirlo cuesta tiempo y tokens, así que se usa solo
cuando la decisión lo merece.

## Paso 0 — Decidir si esto es una junta

Antes de convocar a nadie, responde: **¿esta decisión es reversible y barata?**

- Si es reversible y barata → responde tú, o convoca a un solo consejero. No montes
  una junta para elegir el asunto de un correo.
- Si es cara, difícil de revertir, o toca varios frentes a la vez → sigue el protocolo.

Di explícitamente cuál de los dos caminos tomas y por qué. Una línea basta.

## Paso 1 — Recuperar la memoria

Convoca a `secretaria-junta` para que traiga el informe de apertura: acuerdos
abiertos, decisiones previas relacionadas, datos que quedaron pendientes.

Si algo de lo que se va a discutir **contradice una decisión anterior**, ponlo sobre
la mesa antes de seguir. Una junta que decide lo contrario de lo que decidió hace dos
meses sin darse cuenta es una junta que no aprende.

## Paso 2 — Encuadrar el asunto

Escribe en una o dos líneas **qué se está decidiendo realmente**. Es frecuente que la
pregunta que llega no sea la pregunta que importa:

| Lo que preguntan | Lo que suele estar debajo |
|---|---|
| "¿Subo el precio?" | ¿Estoy vendiendo al cliente equivocado? |
| "¿Publico más en LinkedIn?" | ¿Mi contenido genera conversaciones o solo likes? |
| "¿Contrato a alguien?" | ¿Qué parte de mi tiempo no debería ser mía? |
| "¿Hago este servicio nuevo?" | ¿Los que ya tengo están dando su margen? |

Si detectas un reencuadre, **dilo antes de convocar** y pide confirmación si cambia
sustancialmente lo que hay que analizar.

## Paso 3 — Convocar en paralelo

Manda a trabajar a la vez a los consejeros que tengan algo real que aportar.

**Cada encargo debe ser autoexplicativo.** Los consejeros no ven tu conversación ni el
trabajo de los demás. Cada uno recibe:

1. El asunto encuadrado
2. Los datos concretos que ya tienes (cifras, contexto, restricciones)
3. La pregunta específica que le haces **a él**
4. El formato en el que quieres su respuesta

Guía de convocatoria por tipo de asunto:

| Tipo de asunto | Consejeros a convocar |
|---|---|
| Precio / rentabilidad de un servicio | `cfo-finanzas`, `cro-comercial`, `cmo-marca` |
| Lanzar o retirar un servicio | `cfo-finanzas`, `cro-comercial`, `coo-operaciones` |
| Cliente corporativo grande | `cfo-finanzas`, `coo-operaciones`, `legal-colombia` |
| Estrategia de contenido | `cmo-marca`, `cro-comercial`, `cdo-ia-datos` |
| Automatización / herramienta nueva | `cdo-ia-datos`, `coo-operaciones`, `cfo-finanzas` |
| Contrato / acuerdo / datos personales | `legal-colombia`, `cfo-finanzas` |
| Capacidad / "no me da el tiempo" | `coo-operaciones`, `cro-comercial`, `cfo-finanzas` |

No convoques a los ocho por defecto. Un consejero sin nada que decir sobre el tema
solo añade ruido y latencia.

## Paso 4 — Confrontar

Cuando vuelvan, **busca dónde se contradicen**. Ahí está el valor de tener una junta.

- Si el CFO dice que el margen no da y el CRO dice que el cliente es estratégico:
  esa tensión es la decisión, no un problema a promediar.
- Si todos coinciden en todo, **sospecha**. O el asunto era trivial, o les diste el
  mismo encargo, o nadie tenía datos reales. Dilo.

**No promedies opiniones.** Una junta que produce el promedio de sus consejeros no
sirve para nada; produce la mejor decisión a la vista de todas ellas.

## Paso 5 — Pasar por el contradictor

Antes de cerrar, convoca a `contradictor` con la decisión ya formulada. Dale la
decisión y su fundamento, no el debate entero.

Si levanta una objeción que no puedes responder con datos, **la decisión no está
lista**: dilo y señala qué haría falta para resolverla.

## Paso 6 — Decidir

Una recomendación clara. No un menú.

Si hay una decisión que solo Sandra puede tomar (porque depende de su apetito de
riesgo, de sus ganas, o de información que solo ella tiene), di **exactamente cuál
es** y qué necesita saber para tomarla. Eso también es cerrar.

## Paso 7 — Acta y memoria

Convoca a `secretaria-junta` para que levante el acta y persista en Supabase la
decisión, los acuerdos con responsable y fecha, y los datos que faltaron.

Si la memoria de Supabase no está disponible, dilo en el cierre: la junta acaba de
producir información que se va a perder.

## Formato del entregable final

```
## Asunto
## Lo que dijo la junta
## Dónde no hubo acuerdo
## Decisión
## Acciones      (tabla: # | Acción | Responsable | Fecha | Cómo se verifica)
## Lo que hizo falta para decidir mejor
```

## Reglas que no se negocian

- **Cero cifras inventadas.** Dato que falta, dato que se pide.
- **Métrica y plazo en toda acción.** Sin eso es una opinión.
- **El tiempo de Sandra es el recurso escaso.** Operación de una sola persona.
- **El desacuerdo se registra.** Es la información más valiosa de la sesión.
