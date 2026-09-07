# Arquitectura de etiquetas de matIA

## Principio

Todo lo que matIA toca vive bajo el prefijo `MATIA/`. Si algún día Sandra
quiere desmontarlo, borra ese árbol y su bandeja queda intacta. Nada de lo que
hace matIA es irreversible.

## Árbol

```
MATIA/
├── 0-Revisar            ❓  matIA dudó, decide tú
├── 1-P1-Critico         🚨  hoy mismo
├── 1-P2-Alto            ⚡  24 a 48 horas
├── 1-P3-Normal          ✅  esta semana
├── 1-P4-Ruido           🔕  bloque semanal
├── 2-Agendar            📅  calendario
├── 3-Facturas           💰  dinero
├── 4-Oportunidades      🎯  propuestas y contratos
├── 5-Marca              📣  LinkedIn, medios, speaking
└── 6-Operacion          ⚙️  proveedores y plataformas
```

Los números fuerzan el orden alfabético de Gmail. Sin ellos, la barra lateral
mostraría Agendar antes que P1, y el ojo de Sandra buscaría en el lugar
equivocado.

Cada hilo recibe **dos etiquetas**, una de prioridad y una de categoría. Así
la bandeja se puede leer de dos formas, por urgencia cuando hay poco tiempo,
por tema cuando toca sentarse a facturar o a agendar.

## Procedimiento

1. `mcp__Gmail__list_labels`, ver qué existe. Nunca duplicar.
2. `mcp__Gmail__create_label` solo para las faltantes.
3. `mcp__Gmail__label_thread` con las dos etiquetas en una sola llamada,
   `labelIds: [prioridad, categoria]`.
4. Reportar el conteo real de éxitos y de fallos.

## Prohibiciones

- No quitar etiquetas que matIA no puso.
- No tocar `INBOX`, `UNREAD`, `IMPORTANT`, `STARRED`, esas son de Sandra.
- No mover a papelera ni a spam. matIA clasifica, no descarta.
- Si un hilo ya tiene una etiqueta `MATIA/` de una corrida anterior y ahora
  cambió de nivel, primero se quita la vieja de prioridad, luego se pone la
  nueva. Esa es la única excepción a la primera prohibición, y solo aplica
  sobre etiquetas del árbol `MATIA/`.

## Equivalencia en Outlook y Microsoft 365

Outlook usa categorías, no etiquetas anidadas. Se replica el mismo árbol con
nombres planos, `MATIA P1 Critico`, `MATIA Agendar`, `MATIA Facturas`, usando
`mcp__Microsoft_365__outlook_create_label` y
`mcp__Microsoft_365__outlook_modify_thread_labels`.

Antes de crear nada en Outlook, verificar con la lista de categorías
existentes. Si el conector no está autorizado, decirlo, no simular que se
etiquetó.
