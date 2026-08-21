# Kit de Encuesta NPS — IAM™ Intelligence · Comfacesar

Kit completo para medir el pulso del programa **IAM™ Intelligence** en Comfacesar y convertir el
resultado en decisiones (y en caso de éxito).

**Alcance del programa:** 21 áreas · 47 funcionarios · **26 reuniones** realizadas (agosto → octubre 2026).
Contraparte cliente: María Elvira Marulanda.

## Contenido

| Archivo | Para qué sirve |
|---|---|
| `ENCUESTA_NPS.md` | Diseño de la encuesta: las 6 preguntas, por qué cada una, cómo se lee el NPS y calendario de medición. |
| `slack_mensajes.md` | Los 4 copys listos para pegar en `#comunicaciones`: lanzamiento, hilo con preguntas, recordatorio y devolución de resultados. |
| `app_nps.py` | Encuesta web interactiva y **anónima**, con identidad IAM™, más panel de resultados en vivo con **NPS por área**. |
| `calcular_nps.py` | Calculadora de NPS desde las reacciones de Slack o desde el CSV, con desglose por área. |

> ⚠️ **Cobertura:** hoy el único canal de Slack con gente de Comfacesar es `#comunicaciones` (5 personas
> de 47). Para cubrir las 21 áreas: crear un canal general del programa, replicar el mensaje por área,
> o usar la Opción B (un link para todos).

## Opción A — Lanzar hoy en Slack (sin desplegar nada)

1. Publicar el **Mensaje 1** de `slack_mensajes.md` en `#comunicaciones`.
2. Pre-cargar las reacciones `:zero:` … `:keycap_ten:` para que solo tengan que tocar un número.
3. Publicar el **Mensaje 2** como primera respuesta del hilo.
4. Contar las reacciones y calcular:

```bash
# desde las reacciones de Slack
python3 nps_comfacesar/calcular_nps.py --slack "10:2,9:1,8:2,6:1"

# desde el CSV de la app, con desglose por área
python3 nps_comfacesar/calcular_nps.py --csv nps_comfacesar/respuestas_nps.csv --por-area
```

5. Publicar el **Mensaje 4** con los resultados y los ajustes. Este paso no es opcional.

## Opción B — Encuesta web anónima

```bash
pip install streamlit pandas
streamlit run nps_comfacesar/app_nps.py
```

- Encuesta: la URL raíz.
- Panel de resultados: `?admin=1` + clave (por defecto `IAM2026`; en producción se define en
  `.streamlit/secrets.toml` como `admin_key = "..."`).

Para publicarla: subir el repo a [share.streamlit.io](https://share.streamlit.io), apuntar el
archivo principal a `nps_comfacesar/app_nps.py` y compartir el link en el canal de Slack.

> **Sobre la persistencia:** en Streamlit Community Cloud el sistema de archivos es efímero —
> las respuestas del CSV se pierden si la app se reinicia o se redespliega. Para el pulso de una
> semana funciona bien si se descarga el CSV al cerrar. Para el cierre de octubre conviene
> conectar Google Sheets como almacenamiento permanente.

## Las 6 preguntas, en corto

**0. Área** — obligatoria, en la pantalla de inicio. Agrupa, no identifica. Es lo que permite reportar
por área en lugar de un promedio que esconde la realidad.

1. **NPS 0–10** — probabilidad de recomendar el programa a otra área de Comfacesar.
2. **Metodología 1–5** — claridad del formato (vivo + práctica + Slack).
3. **Aplicación (abierta)** — qué ya aplicaron en su trabajo.
4. **Ritmo y nivel** — para calibrar las sesiones que quedan.
5. **Confianza en IA antes vs. hoy (0–10) + ahorro de tiempo percibido** — el impacto del programa,
   contrastable con el ahorro medido tarea por tarea en `Dashboard_IAM_Intelligence_Comfacesar.xlsx`.
6. **Qué necesitan (abierta)** — expectativas no cubiertas.

## Cómo se lee el resultado

`NPS = %Promotores (9–10) − %Detractores (0–6)` · rango −100 a +100.

`> 50` excelente · `20–50` bueno · `0–20` a mejorar · `< 0` alerta.

Y siempre en dos niveles: **NPS global** para el comité, **NPS por área** para gestionar. Un área en
rojo dentro de un global verde es exactamente el problema que esta encuesta existe para detectar.
