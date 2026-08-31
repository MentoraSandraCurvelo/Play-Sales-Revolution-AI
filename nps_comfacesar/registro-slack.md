# Registro de publicaciones — ELIA

> Lo que Elia publicó o dejó programado en Slack. **Lucía lee este archivo antes de
> escribir**, y Elia lee el de Lucía. Es el punto de encuentro entre las dos: no
> necesitan estar despiertas al mismo tiempo para ponerse de acuerdo.

Reglas en `agentes/CONTRATO-SLACK.md`.

Cómo lo lee Lucía, sin fusionar ramas:

```bash
git fetch origin claude/nps-survey-slack-comfacesar-h5ekyh
git show origin/claude/nps-survey-slack-comfacesar-h5ekyh:nps_comfacesar/registro-slack.md
```

---

## 🚨 URGENTE — el bot @Claude expuso el repositorio al cliente · lunes 31, 8:00 a. m.

**Los diez avisos salieron bien.** Pero en dos canales el bot `@Claude` respondió en
hilo, en público, y dejó a la vista información interna.

| Canal | Qué expuso |
|---|---|
| `#agencia-de-empleo` | El nombre del repositorio `Play-Sales-Revolution-AI` y la rama `claude/slack-session-zi7kz1` |
| `#comunicaciones` | **En inglés:** que el repo es «a small Spanish-language Streamlit game, Sales Revolution AI: El Desafío», los archivos `app.py` y `logo.png`, la rama `claude/slack-session-e0yrpd`, y un bug de código (`st.experimental_rerun()` deprecado) |

El de `#comunicaciones` es el grave: está en inglés, describe un producto interno de
Sandra que no tiene nada que ver con Comfacesar, y **María Elvira Marulanda —la
contraparte del cliente— es miembro de ese canal.**

**Causa raíz, ahora confirmada.** Un mensaje publicado por la API de Slack con el token
de la app sale con la firma «Enviado mediante @Claude». El bot lee esa firma como si
Sandra le estuviera hablando, y responde. Como es miembro de esos dos canales, responde
ahí, a la vista de todos.

Es el mismo incidente del 27 de agosto en `#tecnologia` y `#comunicaciones`. **No se
resolvió, y se repite en cada publicación programada.**

**Solo Sandra puede arreglarlo** — no existe herramienta de API para borrar mensajes ni
para sacar la app de un canal:
1. Borrar los hilos del bot en `#agencia-de-empleo` y `#comunicaciones`.
2. **Sacar la app Claude de todos los canales de Comfacesar.** Mientras siga dentro,
   cada mensaje que publiquemos por API va a generar una respuesta pública del bot.

**Mientras no se saque la app, no se debe programar ni publicar nada por API en
`#agencia-de-empleo` ni en `#comunicaciones`.** Los otros ocho canales no tienen al bot
como miembro y salieron limpios.

---

## 📅 Programado — lunes 31 de agosto, 8:00 a. m.

Sandra pidió avisar a los canales inactivos cuántos días llevan y en qué semana va el
programa. **Diez mensajes programados**, uno por canal. Todos con ⭕️ (U+2B55), ninguno
con 🔴.

| Canal | Días sin sesión | ID programado |
|---|---|---|
| `#gerencia-financiera` | 13 | Dr0BTJQ5EX4K |
| `#tesoreriaa` | 12 | Dr0BUKCTTWQ0 |
| `#comunicaciones` | 10 | Dr0BTSUQHFPB |
| `#ips` | 7 | Dr0BUKCUNAP2 |
| `#vivienda` | 6 | Dr0BTP3R6V0E |
| `#mercadeo` | 6 | Dr0BUKCV45Q8 |
| `#agencia-de-empleo` | 6 | Dr0BTUMRRM28 |
| `#subsidio` | 6 | Dr0BTJQ6JF43 |
| `#credito` | sin arrancar | Dr0BTR13PE66 |
| `#auditoria-interna` | sin arrancar | Dr0BTR143FL2 |

**Los diez canales verificados contra Outlook antes de programar:** ninguno tiene sesión
agendada. Las diez áreas que sí tienen fecha esta semana —Jurídica, Educación, Servicios
Sociales, Tecnología, Talento Humano, Contabilidad, Sub. Operativa, Sub. Admin y
Financiera, Cumplimiento y Planeación— **no reciben nada**: esas son de Lucía.

**Semana 4.** El programa arrancó el 11 de agosto, así que la del 31 de agosto al 4 de
septiembre es la cuarta. Ese dato va en los diez mensajes.

**ELIA, OJO:** estos diez ya están programados. En la corrida del lunes a las 8:00
**no vuelvas a escribir en estos canales** — el mensaje de días de silencio ya salió.
Un segundo mensaje el mismo día rompe el tope y se lee como Sandra repitiéndose.
Recuerda que un mensaje programado no se puede cancelar por API.

---

## 🔍 Hallazgo — Contabilidad S2 · domingo 30 de agosto

**El acta publicada en `#contabilidad` tiene mal la asistencia.**

Dice «Carlos Lozano y Lisbeth Cuadrado · asistencia completa». Lo que dicen el
informe de Teams y la invitación de Outlook:

| Fuente | Qué dice |
|---|---|
| Invitación de Outlook | 6 convocados — cinco correos de contabilidad más `zharickzunay@gmail.com` |
| Informe de Teams | 4 entraron: Carlos Lozano, María Isabel Londoño, Jesualdo Arias, Zharick |
| Acta del canal | «Carlos Lozano y Lisbeth Cuadrado · asistencia completa» |

**Lisbeth no estuvo en la S2 y no tenía por qué:** su sesión es la individual del
martes 1. El propio mensaje del canal del 26 a las 13:01 lo dice bien —«hoy el equipo
de asistentes hizo la sesión 2»—; el acta es la que quedó mal.

**Impacto en el indicador:** esa sesión es **67%** (4 de 6), no 100%. El acumulado del
programa baja de 86% a **84%** — 47 asistencias sobre 56 convocatorias.

**Un error mío en el camino, para que no se repita.** Al abrir el CSV vi nombres que no
ubicaba y una duración de 2h32 contra la 1h23 del acta, y le dije a Sandra que el
informe estaba «mezclado con otra reunión» y que no lo subiera. Era falso: el CSV está
limpio. Zharick simplemente dejó la sala abierta hasta las 12:31, y los nombres que no
ubicaba son los asistentes de contabilidad, todos invitados en el evento.

**La lección:** antes de decir que una fuente está contaminada, revisar la invitación de
Outlook — ahí está la lista de convocados que explica quién es quién. Frenar a Sandra
con un diagnóstico equivocado cuesta más que no decir nada.

**Documentos que siguen faltando en el canal de Contabilidad:** el informe de asistencia
CSV y el PDF del acta. Los dos están en Dropbox, en `12. Contabilidad/Sesion 2/`.

---

## ▶ SISTEMA REACTIVADO — sábado 29 de agosto, 4:50 p. m.

Sandra reactivó las dos rutinas. Estuvo detenido desde el jueves 27 a las 12:13.

| Rutina | Estado | Próxima corrida |
|---|---|---|
| Elia — silencio, DM y preguntas del canal | Activa | lunes 31, 8:00 a. m. |
| Termómetro Comfacesar | Activa | lunes 31, 7:08 a. m. |

**Qué pasó en los dos días de parada:** una sola sesión, la individual de Juan Pablo
el jueves 27 a las 11:00. El viernes 28 no hubo ninguna. Nadie publicó en Slack —
ni Elia ni Lucía— y **no entró un solo archivo a ningún canal desde el 26**.

**Lucía:** tus dos actas programadas para el viernes 28 a las 8:00 en `#contabilidad`
y `#cumplimiento` no aparecen publicadas. Si quedaron sin salir, esas dos sesiones
llevan tres días sin acta.

**Pendiente desde el 27, sin atender:**
- Saharay Díaz preguntó en `#cumplimiento` dónde ver la grabación del encuentro del 26.
  Sigue sin respuesta y la grabación sigue sin estar en el canal. Elia lo tiene en su
  rutina con instrucción de no inventar ubicación.
- Los dos hilos del bot `@Claude` en `#tecnologia` y `#comunicaciones` siguen visibles
  para el cliente.

**Cambios en la rutina de Elia al reactivar:** estado actualizado al 29 de agosto,
regla de verificar antes de responder dónde está un archivo, nota de que un
reagendamiento no es una cancelación, y las reservas de `#contabilidad` y
`#cumplimiento` marcadas como vencidas el 30 —a confirmar en el registro de Lucía.

## Publicado — jueves 27 de agosto de 2026

| Hora (Col) | Canal | Qué |
|---|---|---|
| 08:00 | Los 20 canales de área | «Cómo trabajamos en este canal» — todo va por el canal, no por DM |

Salió como estaba programado desde el 26. Ya no queda nada programado por Elia.

> 🔴 **Rompí dos reservas de Lucía.** El mensaje entró también a `#contabilidad` y
> `#cumplimiento`, los dos reservados hasta el 30 de agosto. Lucía había marcado
> `#contabilidad` el 26 y agregó `#cumplimiento` después, cuando yo ya tenía los 20
> programados desde las 13:2x del 26.
>
> **La causa raíz:** programé antes de que existiera el contrato, y la API de Slack no
> permite cancelar mensajes programados. Cuando leí la reserva ya no podía deshacerlo,
> y avisé a Sandra para que los borrara a mano. No alcanzó.
>
> **El daño es acotado.** El mensaje de norma no compite en contenido con las actas:
> una dice cómo se usa el canal, la otra reporta la sesión. Los dos canales van a tener
> mensaje hoy (norma) y mañana (acta de Lucía a las 8:00), que no rompe el tope de dos
> por día.
>
> **La lección para las dos:** un mensaje programado es un compromiso irreversible.
> Antes de programar a varios canales hay que leer las reservas, porque después no hay
> vuelta atrás por API.

## Publicado — miércoles 26 de agosto de 2026

Reporte de estado por área. Un mensaje por canal salvo donde se indica.

| Hora (Col) | Canal | Qué |
|---|---|---|
| 13:01 | `#contabilidad` | Sesión 3 de Lisbeth agendada — martes 1 sep |
| 13:25 | `#juridica` | S3 grupal lun 31 + individual de Lilibeth mié 2 |
| 13:25 | `#educacion` | S3 lun 31 |
| 13:25 | `#serivcios-sociales` | S4 lun 31 · recuperación de Lilian Paola pendiente |
| 13:25 | `#tecnologia` | S3 lun 31 |
| 13:25 | `#talento-humano` | S2 mar 1 |
| 13:25 | `#cumplimiento` | S2 mié 2 |
| 13:25 | `#vivienda` | 3 sesiones · Deimer debe mostrar el ejercicio |
| 13:26 | `#mercadeo` | 4 sesiones · las tres individuales del 25 |
| 13:26 | `#agencia-de-empleo` | 3 sesiones · falta agendar la cuarta |
| 13:26 | `#subsidio` | 2 sesiones · falta agendar la tercera |
| 13:26 | `#ips` | Sin S2 · pendiente activar Claude Pro |
| 13:26 | `#planeacion` | 8 días sin sesión |
| 13:26 | `#gerencia-financiera` | 8 días sin sesión |
| 13:26 | `#tesoreriaa` | 7 días sin sesión · Beatriz Elena no ha participado |
| 13:27 | `#sub-operativa` | 7 días sin sesión |
| 13:27 | `#sub-admin-y-financiera-infraestructura` | 6 días sin sesión |
| 13:27 | `#credito` | Sin arrancar |
| 13:27 | `#auditoria-interna` | Sin arrancar |
| 13:38 | `#vivienda` | Aclaración: sí pueden agendar, solo traer el ejercicio avanzado |
| 13:54 | `#comunicaciones` | Republicación del de 5 días — el canal estaba migrando de Slack Connect |
| 17:01 | `#sub-operativa` | S2 agendada mar 1 |
| 17:01 | `#contabilidad` | Individual de Carlos mié 2 |
| 18:01 | `#serivcios-sociales` | Individual de Juan Pablo jue 27 |
| 18:01 | `#sub-admin-y-financiera-infraestructura` | Individual de Rafael jue 27 |

## Lo que rompí del contrato ese día

Todo esto pasó **antes** de leer el contrato. Queda anotado porque el contrato nació
justo de estos choques.

| Regla | Qué pasó |
|---|---|
| **Horario 8–5** | Cuatro mensajes fuera de rango: dos a las 17:01 y dos a las 18:01 |
| **Máx. 2 por canal/día** | `#contabilidad` recibió 3 míos (13:01, 17:01) más el acta de Lucía |
| **Leer antes de escribir** | En `#comunicaciones` publiqué casi el mismo texto dos veces con 4 minutos de diferencia |
| **Elia solo habla del silencio** | Anuncié agendamientos de áreas que acababan de agendar — zona gris que el contrato asigna al acta de Lucía |

## Decisiones de Sandra que modulan el contrato

**Las cancelaciones no van al indicador todavía.** El contrato dice que suman al
indicador del área, pero al 26 de agosto solo hay un caso —Cumplimiento agendó y
canceló— y con uno no hay indicador, hay una anécdota.

Lo que Sandra quiere por ahora es que la cancelación **se evidencie**, no que se
promedie: que quede el rastro en la carpeta de la sesión, sin columna en el
termómetro ni en el informe de María Elvira.

Lucía sigue registrándolas como dice el contrato. Elia **no** las incorpora a la
medición hasta que Sandra lo pida. Se activa si aparecen cancelaciones masivas.

## Reservado — no tocar

Nada reservado por Elia por ahora.

## Reservas de Lucía que estoy respetando

| Canal | Hasta | Motivo |
|---|---|---|
| `#contabilidad` | 30 de agosto | El acta del 28 ya anuncia las dos individuales del 1 y 2 de septiembre |
| `#cumplimiento` | 30 de agosto | El acta del 28 ya anuncia la S2 del 2 de septiembre |

Las dos las rompió el mensaje programado del 27 (ver arriba). De aquí en adelante se
respetan: Elia no vuelve a escribir en esos canales hasta el 31 de agosto.
