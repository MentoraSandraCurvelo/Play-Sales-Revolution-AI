# IAM™Hello — el archivo del programa, que es de Sandra

Slack en plan gratuito **esconde los mensajes a los 90 días y borra a un año** lo que
tenga más de doce meses. Este archivo existe para que eso deje de importar: lo que se
baja aquí ya no depende de Slack.

## Qué hay dentro

| Carpeta | Qué guarda |
|---|---|
| `raw/` | El volcado crudo de cada canal, tal como lo devuelve Slack. No se edita a mano. |
| `datos/archivo.json` | Los mensajes ya normalizados: autor, fecha, texto, adjuntos, hilos, reacciones. |
| `fijados.json` | **Este sí lo edita Sandra.** Las carpetas y enlaces de cada canal. |
| `plantilla_v2/` | **La aplicación.** Viene de diseño y es fija — salvo `data/archivo.js`. |
| `plantilla_v2/data/archivo.js` | Mensajes + actas + fijados. **Es lo único que cambia cada mes.** |
| `entregable/` | El HTML único que se entrega. No se versiona. |

## Cómo se actualiza — tres pasos

```bash
python3 extraer.py     # 1 · recoge los canales leídos y los deja en raw/
python3 parsear.py     # 2 · normaliza raw/ → datos/archivo.json
python3 construir.py   # 3 · junta mensajes + actas + fijados → plantilla_v2/data/archivo.js
python3 empaquetar.py --sin-internet --con-pdfs   # 4 · el entregable
python3 probar.py                                 # 5 · abrir todas las vistas
```

**El paso 5 no es opcional.** `probar.py` abre las ≈180 vistas de la app —cada acta,
cada pestaña de cada canal y las globales— y avisa si alguna revienta o sale vacía.
_Nació de un fallo real:_ un acta escrita a mano llevaba un campo como texto donde la
app esperaba una lista, y con eso **la app entera dejaba de verse**, no solo esa acta.
Se entregó tres veces sin detectarlo porque solo se probaba una vista. **Nada sale sin
pasar por ahí.**

El paso 3 lee las actas de `agentes/lucia/sesiones/*.json`, así que **cada acta nueva
entra sola**: no hay que copiar nada.

## Los fijados

`fijados.json` replica lo que está fijado arriba en cada canal de Slack. **Hoy solo lleva
la carpeta común del programa, y así se queda:** _decisión de Sandra del 2 de octubre,_
«olvídate de los fijados, no los voy a poner de momento». **No hay que volver a
pedírselos.**

Si algún día quiere añadir carpetas por canal, la estructura es esta y luego se corre
`python3 construir.py`:

```json
"subsidio": {
  "carpetas": [
    {
      "titulo": "Tableros del área",
      "icono": "📊",
      "enlaces": [
        { "titulo": "Tablero de productividad", "url": "https://…", "nota": "Se actualiza solo" }
      ]
    }
  ]
}
```

## La plantilla y las dos versiones del entregable

La aplicación la mantiene diseño y llega en una carpeta (`plantilla_v2/`, con su propio
`README.md`). El agente **no la edita**: solo reescribe `data/archivo.js`.

`empaquetar.py` la convierte en un HTML único que se abre con doble clic. Tiene dos
modos, y la diferencia importa:

```bash
python3 empaquetar.py                  # ~2 MB · necesita internet
python3 empaquetar.py --sin-internet    # ~6 MB · se abre sin conexión
```

**La versión normal no se abre sin internet.** No es por las fuentes: el runtime de la
plantilla descarga *React, React DOM y Babel* de `unpkg.com` cada vez que se abre el
archivo, y sin eso la página queda en negro. `--sin-internet` mete esas tres librerías
y three.js dentro del HTML, usando el gancho `window.__resources` que el propio runtime
trae previsto. Antes hay que correr `traer-librerias.py` una vez, que las baja de npm a
`plantilla_v2/vendor/` (esa carpeta no se versiona).

> **Para el cliente va la versión `--sin-internet`.** Este archivo tiene que seguir
> abriendo cuando Slack ya haya borrado el espacio; depender de que tres CDN sigan en
> pie —y de que la red de Comfacesar no los bloquee— es exactamente lo que el archivo
> viene a evitar.

Cambio hecho sobre la plantilla, uno solo: `hero3D` en `lib/iam.js` queda dentro de un
`try`. Sin WebGL —equipo corporativo bloqueado, escritorio remoto— la excepción tumbaba
la página entera y no solo la escena del hero.

## Cadencia

**Cada mes, el día 2.** Es el margen: Slack esconde a los 90 días, así que bajando
mensualmente nunca se pierde nada. Está en el calendario de Sandra.

## Enlaces dentro de la aplicación

Cada vista tiene dirección propia, así que un canal o un acta se puede enviar por enlace:

- `#/juridica/mensajes` — el canal
- `#/juridica/actas` — sus actas
- `#/juridica/actas/juridica-s9-2026-09-22.json` — un acta concreta
- `#/buscar/agente` — una búsqueda
- `#/personas` · `#/archivos` · `#/actas` — las vistas transversales

## Cómo se abren los archivos (y por qué no basta con un enlace)

Publicada como página, la aplicación se sirve **dentro de un marco con `sandbox`**. Ahí
un enlace a un PDF no abre nada: ni pestaña nueva, ni descarga, ni un aviso en la
consola. Se midió con y sin `allow-popups`, con pestaña y sin ella, y el resultado es
siempre el mismo. Por eso los adjuntos **no se dejan al navegador**: `lib/iam.js`
intercepta el clic, se trae el archivo con `fetch` —mismo origen, eso sí funciona— y lo
pinta dentro: el PDF con pdf.js sobre un canvas, el informe de asistencia como tabla, la
imagen y el audio con su etiqueta. Abierto con doble clic desde el disco no se toca
nada, porque ahí `fetch` no funciona y el navegador sí abre el archivo por su cuenta.

pdf.js viaja incrustado en la página, y con él su worker **en el hilo principal**: al
encontrar `window.pdfjsWorker` ya no intenta crear un `Worker`, que es otra cosa con la
que no se puede contar dentro del marco.

## De dónde salen los adjuntos

Slack en plan gratuito exporta **el nombre del archivo, no el archivo** — pero sí el ID.
Con ese ID se bajan a `adjuntos/`, con el ID por nombre (el de Slack lleva emojis y
comas, y no sobrevive al viaje), y `construir.py` los enlaza. Los informes de asistencia
salen de los que ya teníamos cosechados de Dropbox, con su texto completo.

**Esa carpeta sí va al repositorio**: Slack ya ha borrado alguno —un vídeo de
Contabilidad de agosto ya no está— y esos archivos no se pueden regenerar.

Las grabaciones siguen viviendo en SharePoint; de ellas aquí queda el índice de qué se
publicó, cuándo y en qué canal — y, en el caso de las actas, **su contenido completo**,
que es lo que de verdad no debe caducar.

---
⭕ IAM™ Intelligence · Comfacesar · Sandra Curvelo, Mentora IAM™
