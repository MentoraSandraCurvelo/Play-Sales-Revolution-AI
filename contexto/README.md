# Contexto de Negocio — IAM™ / Sandra Curvelo

Esta carpeta es **la fuente de verdad** de la Junta Directiva Agéntica. Todo lo que
escribas aquí lo leen los consejeros antes de opinar. Si un dato no está aquí, el
agente no lo sabe.

## Cómo funciona

`junta/contexto.py` lee **todos** los `.md` de esta carpeta (ordenados por nombre) y
los inyecta en el prompt de sistema de la junta. No hay que registrar nada: si añades
un archivo nuevo, entra automáticamente en la siguiente sesión.

## Archivos

| Archivo | Qué contiene | Estado |
|---|---|---|
| `01-negocio.md` | Quién es el negocio, modelo, filosofía | Sembrado |
| `02-oferta.md` | Los 5 pilares de servicio y su estructura | Sembrado |
| `03-clientes-icp.md` | Audiencias, dolores, lenguaje, clientes referencia | Sembrado |
| `04-operativa.md` | Cómo se opera: canales, herramientas, procesos | Plantilla — completar |
| `05-finanzas.md` | Moneda, márgenes, benchmarks, KPIs financieros | Sembrado + huecos |
| `06-marca-iam.md` | Identidad visual y verbal IAM™ | Sembrado |

## Convención de marcadores

Cuando un dato falta, se marca así:

```
> ⚠️ POR COMPLETAR: precio del programa de mentoría individual
```

Los consejeros están instruidos para **no inventar** valores marcados con
`⚠️ POR COMPLETAR`. Si necesitan uno, lo piden explícitamente en lugar de suponerlo.

## Qué NO poner aquí

- Credenciales, tokens, claves de API → van en `.env` (que está en `.gitignore`)
- Datos personales de clientes → viven en Airtable/Notion y se leen vía conectores
- Cifras que cambian cada mes → viven en Airtable/Supabase, no en un `.md`

Esta carpeta es para lo **estable**: quién eres, qué vendes, a quién, con qué reglas.
