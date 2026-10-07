# Consola IAM™Hello

**La vista única de Sandra sobre todos los espacios de cliente.**
`https://claude.ai/artifact/YMFNSMn2Hn2B37mQ4JDv6w`

No es una app de cliente: es la de ella. _Un cliente nunca recibe este enlace._

## De dónde saca los datos

La consola lee la colección `clientes` de su propia base. **No puede leer las apps de los
clientes**, porque una app publicada no alcanza los datos de otra, y eso es justamente lo
que hace que el espacio cerrado sea cerrado.

**El puente son los agentes.** El agente de cada cliente corre con los permisos de Sandra,
entra al espacio de su cliente y escribe el reporte en el documento de ese cliente aquí:

```
clientes/<slug>  ·  campo reporte: { ts, titular, detalle, pendientes }
```

Y el agente averigua a qué app entrar leyendo `url` del mismo documento, que sale de
`clientes/<slug>.json` en el repositorio.

## Dar de alta un cliente

1. Escribir `clientes/<slug>.json` en el repositorio, que es el directorio que manda
2. Escribir el documento `clientes/<slug>` en la base de la consola, con `nombre`, `sigla`,
   `estado`, `programa`, `url` y `orden`
3. Construir y publicar su app con `publicar.py --cliente <slug>`

## Lo que falta

- **Los logos.** El campo `logo_url` ya está soportado: si trae una dirección, la tarjeta
  muestra el logo en vez de la sigla. _Sin logo sale la sigla sobre el rojo IAM._
- **Que algún agente reporte.** Hoy las dos tarjetas dicen que el agente no ha reportado,
  que es la verdad.
