# Canales de Slack — mapa de IDs

Para publicar o programar un mensaje hace falta el **ID** del canal, no el nombre.
Normalmente se resuelve buscando el canal, pero la búsqueda de Slack se cae de vez en
cuando y entonces Lucía se queda sin poder mandar un recordatorio a tiempo. Por eso el
mapa vive aquí: se llena una vez y deja de depender de la búsqueda.

## Cómo se saca un ID

En Slack, clic derecho sobre el canal → **Copiar vínculo**. Sale algo así:

```
https://iamteamespacio.slack.com/archives/C0BPDPF4YMD
                                          └── el ID ──┘
```

## Mapa

Sacados el 1 de septiembre de 2026 con `slack_search_public_and_private`. Ojo: la
búsqueda de canales (`slack_search_channels`) lleva días devolviendo vacío incluso para
canales que existen. La de mensajes sí funciona y trae el ID del canal en cada
resultado — ese es el camino que sirve.

| Área | Canal | ID |
|---|---|---|
| Comunicaciones | `#comunicaciones` | `C0BPC33FM9D` |
| Vivienda | `#vivienda` | `C0BPRGLBTUM` |
| Agencia de Empleo | `#agencia-de-empleo` | `C0BPV2YLLBU` |
| Mercadeo | `#mercadeo` | `C0BPT4GE8NS` |
| Jurídica | `#juridica` | `C0BPYQD0UQ4` |
| Educación | `#educacion` | `C0BPDPF4YMD` |
| Talento Humano | `#talento-humano` | `C0BPCQF8GCX` |
| Tecnología | `#tecnologia` | `C0BPV433VSN` |
| Servicios Sociales | `#serivcios-sociales` | `C0BPRGNGLJ1` |
| Planeación | `#planeacion` | `C0BQPDJD0LQ` |
| Contabilidad | `#contabilidad` | `C0BPDN9PKPH` |
| Sub. Operativa y Comercial | `#sub-operativa` | `C0BPYQFRYP6` |
| Sub. Admin y Financiera | `#sub-admin-y-financiera-infraestructura` | `C0BPV3TEKB4` |
| IPS | `#ips` | `C0BPNT6UV8B` |
| Subsidio | `#subsidio` | `C0BPDP5SNMD` |
| Gerencia Financiera | `#gerencia-financiera` | `C0BPV3QQ9SN` |
| Cumplimiento | `#cumplimiento` | `C0BRMUV71UJ` |
| Todo el equipo | `#todo-iamteam` | `C0BN3KV3804` |

Tesorería y Crédito **sí tienen canal** — se localizaron el 7 de septiembre buscando
por contenido y no por nombre: `#tesoreriaa` (`C0BPNSNNGLT`, con doble a) y `#credito`
(`C0BPT65MLNA`). El error anterior venía de buscar el nombre exacto. Se
completan cuando aparezcan.

Los nombres de canal que están sin ID son los que se usan en el tablero; si alguno no
coincide con el nombre real en Slack, se corrige aquí al pegar el enlace.

## Pendiente: Auditoría Interna

El área no tiene canal en Slack (nunca hizo su S1). Con el relevo de representantes
aprobado el 11 de septiembre hay que crearlo e invitar a Aura Sánchez y Eliana Lagos.

