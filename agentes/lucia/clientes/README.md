# IAM™Hello · el directorio de clientes

**Esta carpeta es la columna del producto.** Todo lo demás lee de aquí: la plantilla
construye la app de cada cliente, la consola de Sandra lista los clientes, y cada agente
averigua a qué app le toca entrar.

**Dar de alta un cliente nuevo es escribir un archivo aquí**, no construir una aplicación.

## Por qué una app por cliente

_Se evaluó meter todos los clientes en una sola app publicada y no sirve._ Los permisos de
datos de una página publicada se definen por **nivel de acceso** (ver, escribir, administrar)
y **por persona**, pero no existe una regla de grupo. **Un canal que todo el equipo de un
cliente debe leer queda legible por cualquiera que pueda abrir la app.** Se puede esconder de
la pantalla, pero el dato sigue alcanzable: sería cerrado a la vista y no cerrado de verdad.

**Con una app por cliente el aislamiento es real:** cada cliente tiene su enlace y su lista de
invitados, y nadie de un cliente está invitado a la app de otro. _De paso resuelve lo que
molestaba de Slack:_ **no hay zona común.** El cliente entra y ya está adentro.

**Sandra sí ve todo**, porque es la dueña de todas las apps. El aislamiento es entre clientes,
no entre ella y sus clientes.

## La identidad no se toca

**El look and feel es el mismo para todos los clientes:** rojo IAM `#C00000`, Geist, fondo
oscuro `#060607`. _Lo que cambia por cliente es el logo y el nombre._ Esa es la decisión de
producto: **el cliente debe reconocer que está en IAM™Hello**, no en una app genérica con sus
colores. `color` existe en el archivo para una excepción, pero se deja vacío.

## El archivo de un cliente

| Campo | Qué es |
|---|---|
| `slug` | El identificador. Minúsculas, sin espacios. Es el nombre del archivo |
| `nombre` | Como se escribe en pantalla |
| `nombre_largo` | La razón social, si se necesita en un documento |
| `programa` | El programa que se le presta |
| `espacio` | El nombre que ve el cliente arriba a la izquierda |
| `logo` | Ruta dentro de `logos/`. Si falta, se usa `sigla` sobre el círculo rojo |
| `logo_fondo` | El color sobre el que vive ese logo. **Hace falta:** el de Comfacesar es sobre blanco y sin ese dato quedaría un recuadro raro sobre el fondo oscuro |
| `sigla` | Una letra, el respaldo cuando no hay logo |
| `estado` | En qué va el cliente. Lo lee la consola |
| `url` | La app publicada. **Esto es lo que un agente necesita para saber a dónde entrar** |
| `modo` | `archivo` (solo lectura) o `espacio` (con conversación) |
| `conversacion` | Si el cliente puede escribir |
| `fuente_datos` | De dónde sale el contenido al construir |
| `notas` | Lo que hay que saber antes de tocarlo |

## Abrir el espacio cerrado de un cliente

**El espacio cerrado es la app entera, no el canal.** Dentro de una app, quien puede abrirla
ve todos sus canales: no hay forma de esconderle uno. Así que un cliente nuevo es una app
nueva, y ese es el aislamiento de verdad.

**Sandra no lo monta, lo pide.** Son tres pasos y los hace Lucía:

1. Un archivo `clientes/<slug>.json` con el nombre, el programa, el logo, su color de fondo
   y los canales que lleve. Lo que distingue a un cliente del siguiente es ese archivo, no la
   plantilla.
2. `python3 construir_cliente.py <slug>` arma el paquete de datos, con todo en cero para un
   espacio que arranca.
3. `python3 publicar.py --cliente <slug>` arma la página, y Lucía la publica como artefacto.

**Al publicarla hay que declararle dos capacidades**, o la conversación no funciona y no avisa:

    capabilities: {"db": {"rules": [{"path": "mensajes", "read": "view", "write": "interact"}]},
                   "user": {"scopes": ["profile"]}}

La regla dice quién escribe: **leer, cualquiera que tenga acceso; escribir, de `interact`
hacia arriba.** _En la práctica eso es el nivel Editor_, por lo que se explica más abajo. Y
`scopes: ["profile"]` es lo que hace que salga el nombre de quien escribe en vez de «Alguien».

## Invitar a la gente del cliente

**Esto sí lo hace Sandra, y solo ella**, porque es la dueña. Desde la propia app, en el menú
de compartir, persona por persona y con su correo.

**El menú de compartir ofrece tres niveles, y solo uno sirve aquí.**

| Nivel del menú | Qué puede hacer |
|---|---|
| **Editor** | Leer, escribir en los canales, abrir y descargar los documentos, ver los canales cerrados 🔒 y crear o renombrar canales |
| Comentarista | Solo leer. El propio panel lo dice: no puede cambiar los datos del artefacto |
| Visualizador | Solo leer |

**La regla de los proyectos IAM™Hello es que todo el mundo entra como Editor.** No se usan los
niveles de solo lectura: quien está en el espacio participa, y quien no participa no está.

Eso trae dos consecuencias que conviene tener presentes:

- **El enlace abierto hay que quitarlo.** Una persona de fuera de la organización invitada como
  editor mantiene ese nivel _solo mientras el espacio no esté compartido también por enlace_.
  Con el enlace encendido se queda en lectura, aunque el menú diga Editor. Y al apagarlo, el
  enlace que ya se repartió deja de servir: toca invitar a todos por correo.
- **Los canales cerrados 🔒 dejan de esconder nada.** Son visibles para quien puede editar, y
  aquí puede editar todo el mundo. _En un espacio de un solo nivel, el candado es una etiqueta,
  no una pared._ Lo que no deba ver alguien del equipo va en otro espacio, no en otro canal.

**Las invitaciones caducan a los treinta días.** En un programa de ocho semanas eso cae a mitad
de camino, así que conviene dejarlo en el calendario el día que se invita.

**Y la persona necesita cuenta.** Sin sesión iniciada ve el archivo pero no le aparece el
campo para escribir. _No es un error de la app: es que no sabe quién es._

**Una app, una lista de invitados.** Nadie de un cliente está en la lista de otro, y por eso
no hay manera de que vean lo ajeno ni por error.

## Lo que falta

- **Los logos de los clientes que vengan.** Los de Comfacesar y Novasoft ya están.
  _Del de Comfacesar se recortó el símbolo_, porque el logotipo completo no se lee a tamaño
  de icono; el original entero queda en `comfacesar-completo.jpg`. **Sin logo, un cliente
  sale con su sigla sobre el rojo IAM**, que se ve bien pero no es lo pedido.
- **Los participantes de Novasoft**, con sus correos, y quién escribe frente a quién solo lee.
- **La consola de Sandra**, que es su vista única sobre todos los clientes.
