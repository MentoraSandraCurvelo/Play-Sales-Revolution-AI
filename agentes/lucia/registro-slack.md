# Registro de publicaciones — LUCÍA

> Lo que Lucía publicó o dejó programado en Slack. **Elia lee este archivo antes de
> escribir**, y Lucía lee el de Elia. Es el punto de encuentro entre las dos: no
> necesitan estar despiertas al mismo tiempo para ponerse de acuerdo.

**Por qué existe.** Slack no permite consultar los mensajes programados por API. Un
mensaje programado para mañana **no aparece** al leer el canal hoy. Sin este registro,
leer el canal no basta: se ve lo publicado, no lo que está en camino.

Cómo lo lee Elia, sin fusionar ramas:

```bash
git fetch origin claude/agente-lucia-teams-slack-ccqzne
git show origin/claude/agente-lucia-teams-slack-ccqzne:agentes/lucia/registro-slack.md
```

Cada agente escribe solo en su propio registro y lee el de la otra. Así nunca hay
conflictos de edición entre ramas.

---

| Fecha y hora | Canal | Qué | Estado |
|---|---|---|---|
| 2026-08-28 08:00 | `#contabilidad` | Acta Sesión 2 · Contabilidad, con las dos individuales | **Programado** · ID `Dr0BT2VCH94H` |
| 2026-08-26 13:52 | `#contabilidad` | Acta Sesión 2 · primera versión | Eliminado — atribución errónea |
| 2026-08-26 13:52 | `#contabilidad` | Canvas del acta | Eliminado — los canvas son de plan pago |

## Reservado — no tocar

Áreas donde Lucía ya tiene algo en camino y Elia no debe escribir:

| Canal | Hasta | Motivo |
|---|---|---|
| `#contabilidad` | 30 de agosto | El acta del 28 ya anuncia las dos individuales del 1 y 2 de septiembre |

## Pendiente de publicar

| Área | Qué | Estado |
|---|---|---|
| Cumplimiento | Acta Sesión 1 del 26 de agosto | Lista, esperando el visto bueno de Sandra |
