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

## Lo que falta

- **Los logos de los clientes que vengan.** Los de Comfacesar y Novasoft ya están.
  _Del de Comfacesar se recortó el símbolo_, porque el logotipo completo no se lee a tamaño
  de icono; el original entero queda en `comfacesar-completo.jpg`. **Sin logo, un cliente
  sale con su sigla sobre el rojo IAM**, que se ve bien pero no es lo pedido.
- **Los participantes de Novasoft**, con sus correos, y quién escribe frente a quién solo lee.
- **La consola de Sandra**, que es su vista única sobre todos los clientes.
