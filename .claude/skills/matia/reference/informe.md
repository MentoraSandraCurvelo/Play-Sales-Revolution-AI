# Formato del informe de matIA

Regla de diseño: Sandra decide en la primera pantalla. Lo urgente arriba, el
inventario abajo. Nada de preámbulos.

## Estructura

```markdown
# matIA · Bandeja del {fecha}, {hora} Colombia

**{N} hilos analizados** en {ventana}. Gmail {n1}, Outlook {n2}.
P1 {a} · P2 {b} · P3 {c} · Ruido {d}

---

## 🚨 P1 CRÍTICO · hoy mismo

**1. {Nombre} · {empresa}** · hace {X}h · sin responder
{Asunto}
> Qué pide: {una línea, solo si se leyó el hilo completo}
> Por qué es P1: {razones del motor}
> Acción sugerida: {una línea}

---

## ⚡ P2 ALTO · 24 a 48 horas
{lista compacta, una línea por hilo}

---

## 📅 AGENDAR · {n} hilos
{Quién, qué fecha propone, si ya hay evento en calendario o no}

## 💰 FACTURAS Y PAGOS · {n} hilos
{Quién, concepto, monto solo si aparece textual en el correo, estado}

## 🎯 Oportunidades · {n}
## 📣 Marca y contenido · {n}
## ⚙️ Operación · {n}

---

## ❓ REVISAR · matIA no está segura
{hilo y la duda concreta}

---

## 🏷️ Etiquetado
{X} hilos etiquetados. {Y} fallos. {Z} etiquetas nuevas creadas.

## 📊 Lectura de la semana
{2 o 3 líneas de patrón real, con conteos reales, no impresiones}
```

## Reglas de redacción

- **Montos.** Solo si aparecen textualmente en el correo. Nunca calcular ni
  deducir un monto. Si el correo dice "según lo acordado" sin cifra, se
  escribe "sin monto explícito".
- **Fechas.** Igual, solo las que están en el texto. Si dice "la próxima
  semana", se transcribe así, no se convierte a una fecha inventada.
- **Resúmenes.** La línea "Qué pide" solo se escribe si se llamó `get_thread`
  y se leyó el cuerpo. Si no, se omite y se marca "solo snippet".
- **Nombres de personas.** Como aparecen en el remitente. Nada de suponer
  cargos ni empresas que el correo no diga.
- **Sin adjetivos vacíos.** "Importante", "relevante", "clave" no informan.
  El número de horas sin responder y el nombre del cliente sí.
- **La lectura de la semana** se construye con conteos reales del clasificador.
  Si matIA quiere señalar una tendencia que no puede contar, escribe "esto es
  aproximado, verifícalo".
