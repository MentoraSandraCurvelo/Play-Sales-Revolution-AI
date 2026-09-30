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
