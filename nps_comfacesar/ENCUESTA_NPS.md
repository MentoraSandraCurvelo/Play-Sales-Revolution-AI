# Encuesta NPS — IAM™ Intelligence · Comfacesar (Grupo Comunicaciones)

**Cliente:** Comfacesar — Área de Comunicaciones
**Programa:** IAM™ Intelligence (agosto → octubre 2026)
**Momento de medición:** Pulso intermedio, después de la Sesión 2 (20 de agosto)
**Duración estimada para el participante:** 2 minutos
**Responsable:** Sandra Curvelo — Founder & CSO, IAM™ LATAM

---

## 1. Por qué medir ahora (y no al final)

Medir a mitad del programa tiene tres usos concretos:

1. **Corregir en caliente.** Si el ritmo o la profundidad no encaja, quedan 2 meses para ajustar. Un NPS al final solo sirve para el informe, no para el cliente.
2. **Construir el caso de éxito con datos.** El delta entre "confianza en IA antes" y "confianza en IA hoy" es el número que después se convierte en testimonio y en propuesta comercial para el próximo cliente.
3. **Demostrar método.** Un programa que se mide se percibe como consultoría, no como capacitación. Es diferenciador frente a cualquier competidor que solo dicta sesiones.

---

## 2. Estructura de la encuesta (6 preguntas)

### P1 — NPS (la pregunta madre)
> **En una escala de 0 a 10, ¿qué tan probable es que recomiendes el programa IAM™ Intelligence a un colega de otra área de Comfacesar?**

Escala 0–10. Clasificación estándar:

| Rango | Categoría | Lectura |
|---|---|---|
| 9–10 | **Promotores** | Embajadores internos. Son quienes abren la puerta a otras áreas. |
| 7–8 | **Pasivos** | Satisfechos pero no comprometidos. No suman al NPS. |
| 0–6 | **Detractores** | Riesgo de reputación interna. Requieren conversación 1:1. |

**Fórmula:** `NPS = %Promotores − %Detractores` → resultado entre −100 y +100.

Referencias de lectura para programas de formación B2B:
- `> 50` excelente · `20 a 50` bueno · `0 a 20` a mejorar · `< 0` alerta.

---

### P2 — Metodología
> **La metodología del programa (sesiones en vivo + ejercicios prácticos + documentación y actas en Slack) me resulta clara y fácil de seguir.**

Escala 1–5 (1 = Totalmente en desacuerdo · 5 = Totalmente de acuerdo).

*Qué mide:* si el formato IAM™ (vivo + práctica + trazabilidad en Slack) está funcionando como sistema, no solo como contenido.

---

### P3 — Aprendizaje aplicado (abierta, la más valiosa)
> **De lo visto en las sesiones 1 y 2, ¿qué ya aplicaste — o vas a aplicar esta semana — en tu trabajo de comunicaciones?**

Texto libre.

*Qué mide:* transferencia real al puesto de trabajo. Es la pregunta que produce las frases que después se usan como testimonio y como evidencia de ROI ante el comité de Comfacesar.

---

### P4 — Ritmo y profundidad
> **¿Cómo sientes el ritmo del programa?** → Muy lento · Adecuado · Muy rápido
> **¿Y el nivel de profundidad técnica?** → Muy básico · En el punto · Muy avanzado

*Qué mide:* el ajuste fino de las sesiones 3 en adelante. Es la pregunta que permite corregir sin adivinar.

---

### P5 — Confianza en IA: antes vs. hoy
> **Antes de empezar el programa, ¿qué tan seguro/a te sentías usando IA en tu día a día? (0–10)**
> **¿Y hoy? (0–10)**

*Qué mide:* el **delta de confianza**. Es el indicador de impacto del programa y el número que mejor vende el caso Comfacesar hacia afuera (con autorización del cliente).

---

### P6 — Qué falta (abierta)
> **¿Qué necesitas de mí o del programa para que las próximas sesiones te generen aún más valor?**

Texto libre.

*Qué mide:* expectativas no cubiertas. Responder públicamente a esto en la Sesión 3 sube el NPS de la siguiente medición casi siempre.

---

## 3. Calendario de medición sugerido

| Momento | Qué se mide | Objetivo |
|---|---|---|
| **Pulso 1** — tras Sesión 2 (ahora) | Las 6 preguntas | Línea base + corrección de ritmo |
| **Pulso 2** — mitad de septiembre | P1, P4, P6 | Verificar que los ajustes funcionaron |
| **Cierre** — octubre | Las 6 + P5 final | NPS final, delta de confianza, testimonios |

Comparar Pulso 1 → Cierre es lo que convierte el proyecto en caso de éxito publicable.

---

## 4. Dos formas de aplicarla (elegir una o combinar)

### Opción A — Nativa en Slack (recomendada para arrancar hoy)
El NPS se responde con **reacciones de emoji 0️⃣–🔟** sobre el mensaje, y las preguntas abiertas en **hilo**.

- ✅ Cero fricción: se responde sin salir de Slack, desde el móvil.
- ✅ Se lanza hoy mismo, sin desplegar nada.
- ✅ Genera conversación visible en el canal (las respuestas en hilo alimentan a todo el grupo).
- ⚠️ No es anónima: las reacciones y los hilos llevan nombre.

Copys listos para pegar: `slack_mensajes.md`.

### Opción B — App web anónima (IAM™ branded)
Encuesta interactiva desplegada en Streamlit, con la identidad IAM™, que guarda respuestas y calcula el NPS en vivo.

- ✅ **Anónima** → respuestas más honestas, sobre todo de detractores.
- ✅ Panel de resultados con NPS, distribución y delta de confianza.
- ✅ Se comparte como un simple link en el canal de Slack.
- ⚠️ Requiere desplegarla (Streamlit Cloud, 5 min).

Código: `app_nps.py` · Cálculo y reportes: `calcular_nps.py`.

**Recomendación:** empezar con la **Opción A** para el pulso de esta semana (velocidad y participación), y usar la **Opción B** en el cierre de octubre, cuando el anonimato importa más porque el resultado va a informe.
