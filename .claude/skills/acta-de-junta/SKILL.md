---
name: acta-de-junta
description: >
  Levanta el acta formal de una sesión de junta directiva IAM™ y la persiste en la
  memoria de Supabase. Actívalo cuando se pida "levanta el acta", "documenta esto",
  "registra la decisión", "guarda lo que decidimos", o al cerrar cualquier sesión de
  junta en la que se haya tomado una decisión. También para recuperar actas
  anteriores: "¿qué decidimos sobre X?".
---

# Acta de Junta Directiva IAM™

## Qué hace un acta que sirve

Un acta no es un resumen de la conversación. Es el registro de **lo que se decidió,
quién lo ejecuta, para cuándo, y qué información faltó**. Dentro de tres meses nadie
va a leer el debate; van a leer los acuerdos y a preguntarse por qué se decidió así.

## Estructura

```markdown
# ⭕ ACTA DE JUNTA DIRECTIVA IAM™

**Sesión:** <id o fecha-consecutivo>
**Fecha:** <AAAA-MM-DD>
**Asunto:** <una línea>
**Consejeros convocados:** <lista>

---

## 1. Asunto tratado
<Qué se puso sobre la mesa y, si se reencuadró, cuál fue el encuadre final.>

## 2. Posición de cada consejero
### <consejero>
<Su posición y las cifras que la sostienen. No un resumen genérico: los números.>

## 3. Puntos de desacuerdo
<Quién discrepó, sobre qué, y con qué argumento. Si hubo consenso pleno, escríbelo
y anota si eso debería preocupar — un consenso sin fricción a veces significa que
nadie tenía datos.>

## 4. Objeciones del contradictor
<Las objeciones levantadas y cómo se resolvieron. Si alguna quedó sin resolver,
dilo: es un riesgo aceptado.>

## 5. Decisión
<La decisión, en una o dos frases. Sin ambigüedad.>

## 6. Acuerdos
| # | Acuerdo | Responsable | Fecha límite | Cómo se verifica |
|---|---|---|---|---|

## 7. Datos que faltaron
<Lo que la junta necesitó y no tenía. Cada uno con qué decisión mejoraría si se tuviera.>

## 8. Riesgos aceptados conscientemente
<Lo que puede salir mal y se decidió correr de todas formas.>
```

## Reglas de redacción

1. **Un acuerdo sin responsable y sin fecha no es un acuerdo.** Si la junta lo dejó
   vago, no inventes el responsable: llévalo a la sección 7 como dato faltante.
2. **Registra el desacuerdo.** Es la información más valiosa del acta. Un acta que
   solo recoge consensos borra la razón por la que la decisión fue difícil.
3. **Cifras, no adjetivos.** "El margen es bajo" no dice nada; "margen neto 18%,
   contra un umbral saludable de 35%" sí.
4. **No opines.** Registras lo que pasó, no lo que debió pasar.
5. **Sé breve en 1-4, exhaustivo en 5-8.** El contexto se olvida; los compromisos no.

## Persistencia — el paso que no se salta

Después de escribir el acta, guárdala en la memoria:

1. `mcp__memoria__registrar_decision` — asunto, decisión, fundamento, consejeros
   convocados y desacuerdos. Guarda el `id` que devuelve.
2. `mcp__memoria__registrar_acuerdo` — **uno por cada fila** de la sección 6, pasando
   el `decision_id` del paso anterior.
3. `mcp__memoria__registrar_dato_faltante` — uno por cada dato de la sección 7.

Si la memoria no está disponible, **dilo explícitamente al cerrar**: la junta acaba
de producir información que se va a perder, y Sandra necesita saberlo para guardarla
a mano.

## Archivo opcional

Ofrece dejar el acta en Drive con `mcp__google__drive_crear_documento`, en la carpeta
de actas. Nombra el archivo `Acta-Junta-IAM-<AAAA-MM-DD>-<tema-corto>.md`.

## Recuperar actas anteriores

Para "¿qué decidimos sobre X?": usa `mcp__memoria__buscar_decisiones` con el texto
del tema, y `mcp__memoria__listar_acuerdos` para ver qué quedó pendiente de aquello.
Si lo que se propone hoy contradice una decisión anterior, **señálalo**.
