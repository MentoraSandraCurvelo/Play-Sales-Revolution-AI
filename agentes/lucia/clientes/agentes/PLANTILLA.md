# Cómo se crea el agente de un cliente

**Un agente por cliente. La misma receta, cambiando el archivo.** Es el mismo método que
las áreas aprendieron en el programa: una carpeta, un flujograma, una cadencia.

## Lo que el agente necesita para existir

| Qué | De dónde sale |
|---|---|
| **Un nombre** | Se lo pones tú. Terminado en ía, como los demás |
| **Una carpeta** | `clientes/` del repositorio. Ahí está el directorio y los archivos de cada cliente |
| **La dirección de la app** | El campo `url` de `clientes/<slug>.json`. **Es lo único que necesita para saber a dónde entrar** |
| **Un flujograma** | El archivo de este cliente, al lado de este |
| **Una cadencia** | Cuándo revisa y cuándo reporta |

## Cómo se conecta con la app

**No hay nada que integrar.** La app del cliente guarda su conversación y su material en una
base de datos propia, y el agente la lee y la escribe **con tu cuenta**, que es la dueña de
todas las apps.

_Eso tiene una consecuencia que hay que tener presente:_ **el agente podría entrar a la app
de cualquier cliente**, porque tu cuenta las abre todas. El aislamiento es entre clientes, no
entre tú y ellos. **Por eso la primera regla del flujograma de cada agente es que solo toca
su cliente.** No es una advertencia decorativa: es la regla que sostiene la promesa del
producto.

## Cómo reporta

El agente escribe en el documento de su cliente dentro de la consola, en el bloque
`reporte`, con cuatro datos:

| Campo | Qué va |
|---|---|
| `ts` | Cuándo reportó |
| `titular` | Una frase. Lo más importante desde el último reporte |
| `detalle` | Dos o tres líneas. Qué pasó y qué sigue |
| `pendientes` | Cuántas cosas esperan respuesta. **Es el número que suma en tu vista** |

_La consola no entra a las apps de los clientes y no puede hacerlo._ **Lo que tú ves ahí es
lo que los agentes reportaron**, y eso es a propósito: si la consola pudiera leer los
espacios por su cuenta, el espacio cerrado dejaría de ser cerrado.

## Lo que un agente de cliente NO hace

- **No le escribe al cliente sin aprobación.** Redacta, tú apruebas, y **envía él**. _Lo
  que no pasó por ti no sale, pero una vez aprobado no tienes que mandarlo tú._
- **Sí sube los documentos a la app.** El acta en PDF, la grabación, el material del
  proyecto. _En Slack ese paso lo hacía Sandra a mano porque desde aquí no se puede subir
  archivos a Slack. En Hello el agente lo sube él mismo._
- **No borra ni edita lo que escribió un cliente.** La memoria del espacio no se toca.
- **No entra a la app de otro cliente**, aunque pueda.
- **No inventa.** Lo que no sepa, lo deja anotado como pendiente.

## Dar de alta un cliente nuevo, de principio a fin

1. `clientes/<slug>.json` con sus datos
2. `python3 construir_cliente.py <slug>` y `python3 publicar.py --cliente <slug>`
3. El documento `clientes/<slug>` en la base de la consola
4. Una copia de este flujograma con el nombre del cliente, en esta carpeta
5. Crear el agente con esa carpeta y ese flujograma
