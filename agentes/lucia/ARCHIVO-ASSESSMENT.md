# El archivo de assessment — dónde está el que vale

**El que importa es el de Google Drive:**

`Dashboard_IAM_Intelligence_Comfacesar.xlsx`
ID `15MttClb8I_USqiJ537Ne_huySFnzF2Gg`
Carpeta *Comfacesar-IAM™Intelligence* · https://drive.google.com/file/d/15MttClb8I_USqiJ537Ne_huySFnzF2Gg/view

**Permisos:** *cualquiera con el enlace puede editar*, más `web@comfacesar.com` como editor.
Por eso las 21 áreas escriben ahí. **Son 62 registros que sostienen los $210 millones y
cualquiera puede borrarlos sin dejar rastro de quién** — conviene guardar copia fechada.

**El que está colgado en Slack (`F0BPZV1MRRQ`) es la plantilla en blanco del 13 de agosto.**
Cero registros. *No confundirlos:* si hay que leer datos, es el de Drive.

**Tampoco es el de Dropbox** (`Assessment_IAM_Intelligence_Comfacesar_v2.xlsx`, en
*0. Propuesta Documentos iniciales*) — ese también es plantilla.

## Lo que no puedo hacer, y cómo se resuelve

**No puedo escribir dentro del archivo de Drive.** El conector solo permite cambiar nombre y
carpeta, no reemplazar el contenido. *Crear uno nuevo cambiaría el enlace*, y el marcador de
Slack apunta al actual.

**La vía que conserva el enlace la hace Sandra:** en Drive, clic derecho → **Gestionar
versiones** → **Subir nueva versión**. Mismo ID, mismo enlace, todos lo ven actualizado.

## Estructura de las hojas

23 hojas: `INSTRUCCIONES`, `RESUMEN GLOBAL` y 21 de área. **La posición de las filas varía por
hoja** — hay que detectarla, no asumirla:

| Columna | Qué es |
|---|---|
| B | TAREA / REPORTE |
| C | FRECUENCIA |
| D | TIEMPO ACTUAL (minutos) |
| E | HERRAMIENTA IA |
| F | TIEMPO CON IA (minutos) |
| G | AHORRO (min) — *fórmula* `=IFERROR(D-F,"")` |
| H | % REDUCCIÓN — *fórmula* |
| I | **AHORRO (HORAS)** — *añadida el 30 de septiembre* |
| J | OBSERVACIONES |

**La fila del encabezado de tareas está en la 9 o en la 10 según la hoja**, y **la fila de
participantes no es siempre la siguiente al rótulo** — en Subsidio el rótulo está en la 4 y los
nombres en la 7. *Se localiza buscando la fila que tiene los ✓.*

**Los 23 dibujos del archivo están vacíos** — restos del exportador de Google. Editarlo con
openpyxl los descarta y no se pierde nada visual; todo lo demás (combinadas, anchos, rellenos,
fuentes, fórmulas) sobrevive. **Verificado comparando parte por parte.**

## Ojo con el resumen de cada hoja

`HRS/SEM ACTUAL` se calcula como `SUM(D)/60`, **una suma plana sin aplicar la frecuencia.**
Por eso no coincide con las horas del tablero de la Sala de Control, que sí pondera diaria,
semanal, quincenal y mensual. *Son dos medidas distintas y no hay que mezclarlas.*

## Versión subida el 30 de septiembre, 4:26 p. m.

**Sandra la subió como nueva versión desde Drive** — *mismo ID, mismo enlace*, así que el marcador
de Slack sigue sirviendo. **Verificado dentro del archivo que quedó en Drive:** los tiempos de
Vivienda y Talento Humano ya son números, el ahorro sale de la fórmula, la columna
`AHORRO (HORAS)` está en la I, Cindy Rodríguez aparece en Subsidio, los cinco nombres quedaron
corregidos y los campos sin diligenciar están en amarillo.

**El orden del final quedó distinto** al del archivo entregado: las cuatro hojas ocultas se fueron
todas al fondo, y **Talento Humano quedó por debajo de Subsidio y Educación**, que tienen cero
registros. *Sandra lo ajusta ella.*

## Qué son los minutos de la columna D · 9 de octubre

**Son el tiempo total que cuesta la tarea, no los minutos que se le dedican en un día.** Lo
corrigió Sandra el 9 de octubre: *«esos tableros reportan los minutos que se gastan no solo en el
día, o sea, lo que se gastan en total haciendo eso. Entonces puede ser tres días, cuatro días más
bien, esos minutos conviértelos en horas laborales.»*

**Y el acta de Servicios Sociales S6 ya lo decía con el ejemplo delante:** *«un trabajo de dos días
son 960 minutos, dos jornadas de ocho horas, y uno de ocho días son 3.840.»* La conversión del
programa es **una jornada = 8 horas = 480 minutos**.

Con esa lectura, las filas que parecían imposibles no lo son:

| Fila | Minutos | En horas laborales |
|---|---|---|
| Subsidio · Gestión correo | 1.440 | 24 h · 3 jornadas |
| Jurídica · agente matIA | 960 | 16 h · 2 jornadas |
| Jurídica · agente sofIA | 960 | 16 h · 2 jornadas |
| Sub. Admin · Prevalidación precontractual | 480 | 8 h · 1 jornada |

**Lo que sigue estando mal es el rótulo, no la cuenta.** La columna dice `HRS/SEM` y no son por
semana: son el total de horas laborales que costaba la tarea. *Nunca anunciar el total como una
cifra semanal.*

## Las hojas se buscan por nombre, nunca por número

**Cuando alguien edita el tablero desde Sheets, el orden de los `sheetN.xml` cambia.** El 9 de
octubre IPS pasó de `sheet14` a `sheet11` y Subsidio de `sheet15` a `sheet13`. Escribir por número
metió dos filas en Talento Humano y Cumplimiento. Se resuelve leyendo `xl/workbook.xml` y
`xl/_rels/workbook.xml.rels` y mapeando nombre → archivo.

## Dos tablas que ya no tienen sitio

**Jurídica llegó al tope.** Su tabla son las filas 11 a 29 y las diecinueve están ocupadas. La fila
30 era una banda vacía combinada `B30:J30`; se liberó y se usó como fila de tarea, ampliando el
resumen a `B11:B30`.

**Vivienda tiene una tarea que no se cuenta.** El área escribió su novena, *Presentación de Gestión
General a Nivel Gerencial*, semanal, 120 → 15, en la fila 18, y el resumen solo sumaba hasta la 17.
Se amplió a `B10:B18`. **Son 105 minutos suyos que el tablero no estaba contando.**

**Antes de escribir hay que mirar si la tabla del área tiene fila libre.** Si no la tiene, hay que
liberar la banda y ampliar el rango del resumen, o el dato entra y no suma.
