# Mapa de canales de Slack — IAM™ Intelligence · Comfacesar

Workspace: `iamteamespacio.slack.com` · Verificado canal por canal el 21 de agosto de 2026.

El programa trabaja **un canal por área**, y cada área va a su propio ritmo. Las ~26 reuniones a la
fecha son la **suma de las sesiones de todos los canales**. Por eso el pulso NPS se lanza
**solo donde ya hubo sesión**, y el reporte se entrega **segmentado por área**.

> **Criterio:** un área entra al pulso si en su canal ya hay acta, asistencia o grabación de al menos
> la Sesión 1. No se le puede pedir a alguien que evalúe una metodología que todavía no ha vivido.

---

## ✅ Listos para el pulso — 14 áreas · 36 funcionarios

| Área | Canal | ID | Última sesión | Func. |
|---|---|---|---|---|
| Comunicaciones | `#comunicaciones` | `C0BPC33FM9D` | S2 · 20 ago | 5 |
| Jurídica | `#juridica` | `C0BPYQD0UQ4` | S2 · 20 ago | 2 |
| Mercadeo | `#mercadeo` | `C0BPT4GE8NS` | S2 · 19 ago | 3 |
| Agencia de Empleo | `#agencia-de-empleo` | `C0BPV2YLLBU` | S2 · 20 ago | 2 |
| Planeación | `#planeacion` | `C0BQPDJD0LQ` | S1 · 18 ago | 5 |
| Gerencia Financiera | `#gerencia-financiera` | `C0BPV3QQ9SN` | S1 · 18 ago | 3 |
| Talento Humano | `#talento-humano` | `C0BPCQF8GCX` | S1 · 15 ago | 2 |
| Contabilidad | `#contabilidad` | `C0BPDN9PKPH` | S1 · 19 ago | 2 |
| Tesorería | `#tesoreriaa` | `C0BPNSNNGLT` | S1 · 19 ago | 2 |
| Sub Admin Financiera | `#sub-admin-y-financiera-infraestructura` | `C0BPV3TEKB4` | S1 · 20 ago | 2 |
| Sub Operativa | `#sub-operativa` | `C0BPYQFRYP6` | S1 · 19 ago | 2 |
| Servicios Sociales | `#serivcios-sociales` | `C0BPRGNGLJ1` | S1 · 19 ago | 2 |
| Vivienda | `#vivienda` | `C0BPRGLBTUM` | S1 · 13 ago | 2 |
| Educación | `#educacion` | `C0BPDPF4YMD` | S1 · 14 ago | 2 |

## ⏸️ Todavía no — sin sesión registrada en el canal

| Área | Canal | ID | Estado | Func. |
|---|---|---|---|---|
| Cumplimiento | `#cumplimiento` | `C0BRMUV71UJ` | Canal creado el 20 ago, sin sesión | 3 |
| Subsidio | `#subsidio` | `C0BPDP5SNMD` | Solo ingresos al canal | 3 |
| IPS | `#ips` | `C0BPNT6UV8B` | Solo ingresos al canal | 1 |
| Crédito | `#credito` | `C0BPT65MLNA` | Solo ingresos al canal | 1 |
| Auditoría Interna | `#auditoria-interna` | `C0BPDPM30UX` | Solo ingresos · no figura como área en el dashboard | — |

## ❓ Por confirmar

**Tecnología** (`#tecnologia`, `C0BPV433VSN`, 1 func.). En el canal hay conversación del 20 de agosto
— Olga Lucía menciona *"que no se repita lo de la vez pasada"* y que ya quedó agendada la próxima
reunión — pero **no hay acta ni grabación cargada**. Si la sesión 1 se dio (aunque con problemas
técnicos), el área entra al pulso y pasan a ser 15 áreas · 37 funcionarios.

---

## Pendientes de estructura

1. **Archivar `#tesoreria`** (`C0BPRFGR621`, público). El canal válido es **`#tesoreriaa`**
   (`C0BPNSNNGLT`), que es donde están Yohana y Beatriz y donde se cargó la sesión. Archivar el
   duplicado desde Slack: canal → nombre del canal → *Configuración* → *Archivar canal*.
2. **Presupuesto y Dirección Admin no tienen canal propio.** Nota: Sandra Milena Hinojosa
   (`presupuesto@comfacesar.com`) participa dentro de `#planeacion`, así que Presupuesto podría estar
   ya cubierto ahí. Dirección Admin (Alemar Granadillo) sigue sin canal.
3. **Error de tipeo:** `#serivcios-sociales` debería ser `#servicios-sociales`. Renombrarlo no rompe
   nada — el ID del canal no cambia.

También existe `#todo-iamteam` (`C0BN3KV3804`): canal general del equipo IAM, no un área de
Comfacesar. No entra en el pulso.

---

## Cómo se lanza

1. Un mensaje por canal, **solo en los 14 canales listos**, con el copy de `slack_mensajes.md`.
2. Las 11 reacciones `0️⃣`–`🔟` se pre-cargan en cada mensaje para que responder sea un solo toque.
3. Cada área responde en su propio canal → el NPS nace ya segmentado por área.
4. Consolidación: `calcular_nps.py --por-area` para el reporte a María Elvira.
5. Las 5 áreas en espera entran al pulso **después de su Sesión 1**, con el mismo mensaje.
