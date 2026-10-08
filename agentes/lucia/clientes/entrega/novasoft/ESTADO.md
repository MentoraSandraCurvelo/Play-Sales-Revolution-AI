# Dónde está todo, a 8 de octubre de 2026

**Esto es lo que existe hoy.** Si algo cambia, se cambia aquí.

## Las dos direcciones

| Qué | Dónde |
|---|---|
| **La app de Novasoft** | `https://claude.ai/artifact/4LqxApF3bEi8gzJXiy6mgM` |
| **La consola de Sandra** | `https://claude.ai/artifact/YMFNSMn2Hn2B37mQ4JDv6w` |

_La de Novasoft también está en `novasoft.json`, en el campo `url`._ **Léela de ahí, no la
memorices.**

## Cómo se entra

**Con la cuenta de Sandra.** Ella es la dueña de las dos apps, así que no hay llave que
pedir ni permiso que configurar. Lo que sí hay es una frontera: **la cuenta de Sandra abre
las apps de todos sus clientes, y tú solo tocas la de Novasoft.**

## Qué hay dentro de la app de Novasoft

| Colección | Qué guarda |
|---|---|
| `mensajes` | La conversación. Cada mensaje con `texto`, `autor` y `ts` |

**Hoy está vacía.** Nadie ha escrito todavía.

## Qué hay dentro de la consola

| Colección | Qué guarda |
|---|---|
| `clientes` | Un documento por cliente. El de Novasoft es `clientes/novasoft` |

**Ahí escribes tu reporte**, en el bloque `reporte`, con `ts`, `titular`, `detalle` y
`pendientes`. _No toques el documento de ningún otro cliente._

## Lo que todavía no está

- **La app de Novasoft es la primera versión**, hecha a mano antes de que existiera el
  molde. _Tiene la conversación funcionando pero la cara no es la definitiva._ Hay una
  versión nueva construida desde la plantilla de Comfacesar que todavía no se ha publicado
  porque le falta encender la escritura.
- **No hay actas ni grabaciones todavía**, porque el proyecto no ha arrancado.
- **No hay carpetas de Dropbox enlazadas.** Cuando Sandra las dé, van en `novasoft.json`.

## Quién hace qué

| Trabajo | Quién |
|---|---|
| Construir y publicar la app | El equipo de IAM™, desde el repositorio |
| Leer la conversación y responder | **Tú** |
| Subir las actas y el material a la app | **Tú** |
| Reportar en la consola | **Tú** |
| Aprobar lo que se le dice al cliente | Sandra |
