---
name: tablero-kpi
description: >
  Construye el tablero mensual de indicadores del negocio IAM™ con semáforo, lectura
  ejecutiva y comparativo contra el mes anterior. Actívalo cuando se pida "el tablero",
  "los KPIs", "cómo vamos este mes", "el cierre del mes", "los indicadores",
  "dashboard", o cuando alguien pregunte por el estado general del negocio sin
  concretar un área. También al terminar un análisis financiero, para dejar la serie
  histórica registrada en la memoria.
---

# Tablero de KPIs IAM™

## Principio

*"Lo que no se mide no puede ser mejorado."* El tablero existe para que cada mes se
pueda comparar contra el anterior. Un tablero que se construye distinto cada vez no
sirve: **los nombres de los KPIs deben ser estables en el tiempo**.

## Paso 1 — Reunir los datos, sin inventar ninguno

Fuentes, en este orden de preferencia:

1. **Airtable** (`mcp__airtable__*`) — pipeline, clientes, oportunidades
2. **Memoria** (`mcp__memoria__consultar_kpis`) — la serie histórica ya registrada
3. **Meta** (`mcp__meta__*`) — alcance, engagement, rendimiento de campañas
4. **El usuario** — lo que no esté en ningún sistema

Antes de calcular nada, **muestra una tabla con los datos que vas a usar y de dónde
salió cada uno**. Si falta alguno, no lo estimes: márcalo como faltante y regístralo
con `mcp__memoria__registrar_dato_faltante`.

## Paso 2 — Los KPIs y sus nombres canónicos

Usa **exactamente** estos nombres al registrar en memoria, para que la serie sea
comparable:

### Ingresos
| KPI | Nombre canónico | Unidad |
|---|---|---|
| Ingreso total mensual | `ingreso_mensual_cop` | COP |
| Ticket promedio | `ticket_promedio_cop` | COP |
| Cumplimiento de meta | `cumplimiento_meta_pct` | % |
| Ingreso recurrente mensual | `irm_cop` | COP |

### Pipeline
| KPI | Nombre canónico | Unidad |
|---|---|---|
| Prospectos activos | `prospectos_activos` | unidades |
| Tasa de conversión | `tasa_conversion_pct` | % |
| Tiempo promedio de cierre | `dias_cierre_promedio` | días |
| Valor del pipeline | `valor_pipeline_cop` | COP |

### Rentabilidad
| KPI | Nombre canónico | Unidad |
|---|---|---|
| Margen bruto | `margen_bruto_pct` | % |
| Margen neto | `margen_neto_pct` | % |
| Punto de equilibrio | `punto_equilibrio_cop` | COP |

### Social Selling
| KPI | Nombre canónico | Unidad |
|---|---|---|
| SSI de LinkedIn | `ssi_linkedin` | 0-100 |
| Leads generados en LinkedIn | `leads_linkedin` | unidades |
| Costo de adquisición | `cac_cop` | COP |
| ROI de Social Selling | `roi_social_selling_pct` | % |

### Retención
| KPI | Nombre canónico | Unidad |
|---|---|---|
| Clientes recurrentes | `clientes_recurrentes_pct` | % |
| Tasa de renovación | `tasa_renovacion_pct` | % |

Solo incluye en el tablero los KPIs para los que **tengas dato real**. Un tablero con
la mitad de las celdas vacías pero honesto es útil; uno completo con supuestos, no.

## Paso 3 — Semáforo

| Indicador | 🟢 | 🟡 | 🔴 |
|---|---|---|---|
| `margen_bruto_pct` | ≥ 65 | 50–65 | < 50 |
| `margen_neto_pct` | ≥ 35 | 20–35 | < 20 |
| `tasa_conversion_pct` | ≥ 8 | 2–8 | < 2 |
| `ssi_linkedin` | ≥ 70 | 50–70 | < 50 |
| `roi_social_selling_pct` | ≥ 300 | 100–300 | < 100 |
| `cumplimiento_meta_pct` | ≥ 100 | 80–100 | < 80 |
| Flujo de caja | > 3 meses de gastos fijos | 2–3 meses | < 2 meses |

## Paso 4 — Formato del tablero

```markdown
# ⭕ TABLERO IAM™ — <mes año>

## Lectura ejecutiva
<3-5 líneas. Lo que importa, sin rodeos. Qué funciona y qué no.>

## Indicadores
| Indicador | Este mes | Mes anterior | Δ | Estado |
|---|---|---|---|---|

## 🔴 Los tres números que exigen acción
1. <indicador> — <por qué> — <qué hacer> — <para cuándo>
2. ...
3. ...

## Datos que faltaron
<lista, o "ninguno">
```

**Δ (variación)**: solo se calcula si hay dato del mes anterior en la memoria. Si es
el primer mes, dilo: "sin comparativo, es el primer registro de la serie".

## Paso 5 — Registrar la serie

Guarda **cada** KPI calculado con `mcp__memoria__registrar_kpi`, usando:
- `periodo`: el día 1 del mes en formato `AAAA-MM-01`
- `nombre`: el nombre canónico de las tablas de arriba
- `fuente`: de dónde salió el dato

Este paso es lo que hace que el tablero del mes que viene tenga con qué comparar.
No lo saltes.

## Paso 6 — Ofrecer el archivo

Cierra preguntando: *"¿Quieres que deje este tablero en Drive como documento, o en
Excel con las series históricas?"*

Si dice que sí y hay conector de Google, usa `mcp__google__drive_crear_documento`.

## Identidad visual

Cifras críticas en 🔴. Puntos clave con ⭕. Marca escrita como IAM™.
Si se genera un archivo visual: rojo `#C00000`, blanco, negro, tipografía Montserrat.
