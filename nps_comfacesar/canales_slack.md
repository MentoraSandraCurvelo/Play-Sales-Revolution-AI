# Mapa de canales de Slack — IAM™ Intelligence · Comfacesar

Workspace: `iamteamespacio.slack.com` · Verificado el 21 de agosto de 2026.

El programa trabaja **un canal por área**. Las 26 reuniones a la fecha son la **suma de las sesiones
de todos los canales**, no las de un área sola. Por eso el pulso NPS se lanza **canal por canal** y
el reporte se entrega **segmentado por área**.

## Canales por área

| Área (dashboard) | Canal de Slack | ID | Func. |
|---|---|---|---|
| Comunicaciones | `#comunicaciones` | `C0BPC33FM9D` | 5 |
| Planeación | `#planeacion` | `C0BQPDJD0LQ` | 5 |
| Mercadeo | `#mercadeo` | `C0BPT4GE8NS` | 3 |
| Gerencia Financiera | `#gerencia-financiera` | `C0BPV3QQ9SN` | 3 |
| Cumplimiento | `#cumplimiento` | `C0BRMUV71UJ` | 3 |
| Subsidio | `#subsidio` | `C0BPDP5SNMD` | 3 |
| Agencia de Empleo | `#agencia-de-empleo` | `C0BPV2YLLBU` | 2 |
| Talento Humano | `#talento-humano` | `C0BPCQF8GCX` | 2 |
| Contabilidad | `#contabilidad` | `C0BPDN9PKPH` | 2 |
| Tesorería | `#tesoreria` | `C0BPRFGR621` | 2 |
| Sub Admin Financiera | `#sub-admin-y-financiera-infraestructura` | `C0BPV3TEKB4` | 2 |
| Jurídica | `#juridica` | `C0BPYQD0UQ4` | 2 |
| Sub Operativa | `#sub-operativa` | `C0BPYQFRYP6` | 2 |
| Vivienda | `#vivienda` | `C0BPRGLBTUM` | 2 |
| Educación | `#educacion` | `C0BPDPF4YMD` | 2 |
| Servicios Sociales | `#serivcios-sociales` | `C0BPRGNGLJ1` | 2 |
| Tecnología | `#tecnologia` | `C0BPV433VSN` | 1 |
| IPS | `#ips` | `C0BPNT6UV8B` | 1 |
| Crédito | `#credito` | `C0BPT65MLNA` | 1 |

**19 áreas con canal · 43 funcionarios cubiertos.**

## Inconsistencias detectadas (revisar antes de lanzar)

1. **Dos áreas del dashboard no tienen canal:** **Presupuesto** (1 func.) y **Dirección Admin**
   (1 func.). O se crean sus canales, o esas 2 personas responden por otra vía.
2. **`#auditoria-interna`** (`C0BPDPM30UX`) existe como canal pero **no aparece como área en el
   dashboard**. Falta decidir si entra al programa y al assessment.
3. **Canal duplicado:** existen `#tesoreria` (`C0BPRFGR621`, público) y `#tesoreriaa`
   (`C0BPNSNNGLT`, privado). Hay que archivar uno antes de lanzar, o las respuestas se parten.
4. **Error de tipeo en el nombre:** `#serivcios-sociales` debería ser `#servicios-sociales`.
   Renombrarlo no rompe nada — el ID del canal no cambia.

También existe **`#todo-iamteam`** (`C0BN3KV3804`, público): es el canal general del equipo IAM, no
un área de Comfacesar. No entra en el pulso.

## Cómo se lanza

1. Un mensaje por canal de área, con el copy de `slack_mensajes.md`.
2. Cada área responde en su propio canal → el NPS ya queda segmentado por área desde el origen.
3. Consolidación: `calcular_nps.py --por-area` para el reporte a María Elvira.
