# La Sala de Control al cierre, esperando publicación

`sala-de-control-cierre.html` es la Sala de Control recalculada al cierre del 13 de
octubre de 2026. **Todavía no está publicada.**

**Va al mismo enlace de siempre**, `https://claude.ai/artifact/YWpdmWuHVi4jXYW94duVqp`,
nunca a uno nuevo. Ese tablero está compartido con cualquiera que tenga el enlace.

## Por qué está aquí y no publicado

El intento de publicarlo el 13 de octubre quedó frenado: **el tablero está compartido en
vivo y el cambio mueve una cifra de dinero que el director ya vio**, de $253,0 a $355,0
millones a doce meses. Hace falta que Sandra lo apruebe.

**Elia había llegado al mismo punto el 12 de octubre por su cuenta** y lo dejó escrito en
`nps_comfacesar/registro-slack.md`: *«No publiqué nada. El $253,0 M está en dos tableros
públicos y es la cifra que el director ya tiene. Subirla un 40% el día que salen los
mensajes de cierre no es algo que yo deba decidir sola.»*

**Los dos tableros públicos tienen que moverse juntos.** Si se publica este, hay que
publicar también los KPIs (`https://claude.ai/artifact/MhJTwMjwSshsUMYy1gQteg`), que
llevan la misma cifra. Dejar uno diciendo $253 y otro $355 es peor que no tocar ninguno.

## De dónde sale la cifra

`generar_sala.py` arma el tablero desde `datos_cierre.json`, que sale del archivo de
assessment de Drive leído hoja por hoja. **Las gráficas y las tablas se calculan, no se
escriben a mano**, así que no puede quedar un número viejo suelto en el texto.

**Las 187,8 horas las calcularon por separado Lucía y Elia**, cada una partiendo del
archivo y sin ver el resultado de la otra, y coincidieron en la misma cifra. Lo que subió
no es el resultado del programa: es la cantidad de filas que el tablero estaba leyendo.
