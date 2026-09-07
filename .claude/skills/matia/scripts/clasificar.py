#!/usr/bin/env python3
"""
matIA, clasificador determinista de correo para Sandra Curvelo.

Entrada: JSON (lista de correos) por archivo o por stdin.
Salida:  JSON con puntaje, prioridad, categoria y grupos armados. Con --markdown
         imprime ademas el informe listo para pegar.

Esquema minimo de cada correo de entrada:
{
  "id": "hilo_123",              # obligatorio, id del hilo
  "buzon": "gmail",              # gmail | outlook
  "remitente_correo": "a@b.com", # obligatorio
  "remitente_nombre": "Ana B",
  "asunto": "...",
  "snippet": "...",
  "cuerpo": "...",               # opcional, mejora la precision
  "fecha": "2026-09-05T10:00:00",
  "sin_leer": true,
  "sandra_respondio": false,
  "es_respuesta": false,
  "cuerpo_completo_leido": false
}

Todo campo ausente se trata como desconocido, nunca se inventa.
"""

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CONFIG_POR_DEFECTO = RAIZ / "config" / "matia.config.json"

ORDEN_CATEGORIAS = [
    "AGENDAR",
    "FACTURAS_Y_PAGOS",
    "CLIENTES_Y_OPORTUNIDADES",
    "MARCA_Y_CONTENIDO",
    "OPERACION",
    "RUIDO",
    "SIN_CLASIFICAR",
]

NOMBRES_VISIBLES = {
    "AGENDAR": "AGENDAR",
    "FACTURAS_Y_PAGOS": "FACTURAS Y PAGOS",
    "CLIENTES_Y_OPORTUNIDADES": "Clientes y oportunidades",
    "MARCA_Y_CONTENIDO": "Marca y contenido",
    "OPERACION": "Operación",
    "RUIDO": "Ruido",
    "SIN_CLASIFICAR": "Sin clasificar",
}


def normalizar(texto):
    """Minusculas, sin tildes, espacios colapsados. Comparar manzanas con manzanas."""
    if not texto:
        return ""
    texto = unicodedata.normalize("NFD", str(texto))
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", texto.lower()).strip()


def dominio_de(correo):
    correo = normalizar(correo)
    if "@" not in correo:
        return ""
    return correo.split("@")[-1].strip().strip(">").strip()


def coincide(texto, palabras):
    """Devuelve la lista de palabras clave encontradas en el texto."""
    return [p for p in palabras if normalizar(p) in texto]


def cargar_config(ruta):
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def horas_desde(fecha_iso):
    if not fecha_iso:
        return None
    try:
        f = datetime.fromisoformat(str(fecha_iso).replace("Z", "+00:00"))
    except ValueError:
        return None
    if f.tzinfo is None:
        f = f.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - f).total_seconds() / 3600.0


def clasificar_correo(correo, cfg):
    pts = cfg["puntajes"]
    texto = " ".join(
        normalizar(correo.get(c, ""))
        for c in ("asunto", "snippet", "cuerpo", "remitente_nombre")
    )
    asunto_norm = normalizar(correo.get("asunto", ""))
    remitente = normalizar(correo.get("remitente_correo", ""))
    dominio = dominio_de(remitente)

    puntaje = 0
    razones = []
    banderas = []

    # --- Identidad del remitente. La lista de clientes le gana a todo. ---
    clientes = cfg["clientes_conocidos"]
    prospectos = cfg["prospectos"]
    es_cliente = dominio in [normalizar(d) for d in clientes["dominios"]] or \
        remitente in [normalizar(c) for c in clientes["correos"]]
    es_prospecto = dominio in [normalizar(d) for d in prospectos["dominios"]] or \
        remitente in [normalizar(c) for c in prospectos["correos"]]
    es_interno = dominio in [normalizar(d) for d in cfg["dominios_propios"]]
    es_gratuito = dominio in [normalizar(d) for d in cfg["dominios_gratuitos"]]
    es_automatico = any(m in remitente for m in [normalizar(x) for x in cfg["remitentes_automaticos"]])

    if es_cliente:
        puntaje += pts["cliente_conocido"]
        razones.append(f"cliente conocido ({dominio})")
        tipo_remitente = "CLIENTE"
    elif es_prospecto:
        puntaje += pts["prospecto"]
        razones.append(f"prospecto en conversacion ({dominio})")
        tipo_remitente = "PROSPECTO"
    elif es_interno:
        razones.append(f"correo interno ({dominio})")
        tipo_remitente = "INTERNO"
    elif es_gratuito:
        puntaje += pts["dominio_gratuito"]
        razones.append(f"dominio gratuito ({dominio}), baja un nivel por regla de Sandra")
        tipo_remitente = "PERSONAL"
    elif dominio:
        puntaje += pts["dominio_corporativo"]
        razones.append(f"dominio corporativo ({dominio})")
        tipo_remitente = "CORPORATIVO"
    else:
        tipo_remitente = "DESCONOCIDO"
        banderas.append("remitente sin dominio legible")

    if es_automatico and not es_cliente:
        puntaje += pts["remitente_automatico"]
        razones.append("remitente automatico o no-reply")
        tipo_remitente = "AUTOMATICO"

    # --- Categoria por asunto. Gana la categoria con mas coincidencias. ---
    conteos = {}
    evidencia = {}
    for nombre, datos in cfg["categorias"].items():
        halladas = coincide(texto, datos["palabras"])
        # El asunto pesa doble frente al cuerpo, ahi esta la intencion real.
        en_asunto = coincide(asunto_norm, datos["palabras"])
        conteos[nombre] = len(halladas) + len(en_asunto)
        if halladas:
            evidencia[nombre] = halladas[:5]

    mejor = max(conteos, key=lambda k: conteos[k]) if conteos else None
    if not mejor or conteos[mejor] == 0:
        categoria = "SIN_CLASIFICAR"
        banderas.append("sin palabras clave reconocibles")
    else:
        categoria = mejor
        segundo = sorted(conteos.values(), reverse=True)[1] if len(conteos) > 1 else 0
        if segundo == conteos[mejor]:
            banderas.append("empate entre categorias, revisar")

    if categoria == "FACTURAS_Y_PAGOS":
        puntaje += pts["categoria_facturas"]
        razones.append("asunto de dinero")
    elif categoria == "AGENDAR":
        puntaje += pts["categoria_agendar"]
        razones.append("asunto de agenda")
    elif categoria == "CLIENTES_Y_OPORTUNIDADES":
        puntaje += pts["categoria_oportunidades"]
        razones.append("asunto de oportunidad comercial")

    # --- Urgencia y ruido ---
    urgencias = coincide(texto, cfg["senales_urgencia"])
    if urgencias:
        puntaje += pts["senal_urgencia"]
        razones.append(f"senal de urgencia: {urgencias[0]}")

    ruido = coincide(texto, cfg["ruido"])
    if ruido and not es_cliente:
        puntaje += pts["coincide_ruido"]
        razones.append(f"marca de ruido: {ruido[0]}")

    # --- Estado del hilo ---
    if correo.get("sin_leer"):
        puntaje += pts["sin_leer"]
        razones.append("sin leer")

    if correo.get("es_respuesta"):
        puntaje += pts["es_respuesta_a_hilo_de_sandra"]
        razones.append("responde un hilo tuyo")

    horas = horas_desde(correo.get("fecha"))
    if (horas is not None and horas > 48
            and not correo.get("sandra_respondio")
            and tipo_remitente in ("CLIENTE", "PROSPECTO", "CORPORATIVO")):
        puntaje += pts["sandra_no_ha_respondido_48h"]
        razones.append(f"lleva {int(horas)} horas sin respuesta tuya")

    # --- Nivel ---
    u = cfg["umbrales"]
    if puntaje >= u["P1"]:
        prioridad = "P1"
    elif puntaje >= u["P2"]:
        prioridad = "P2"
    elif puntaje >= u["P3"]:
        prioridad = "P3"
    else:
        prioridad = "P4"

    # Zona de duda, dentro de 6 puntos de un umbral. Se manda a REVISAR.
    for nivel, corte in u.items():
        if abs(puntaje - corte) <= 6:
            banderas.append(f"puntaje {puntaje} al filo del umbral {nivel} ({corte})")
            break

    if tipo_remitente == "CORPORATIVO" and categoria in ("FACTURAS_Y_PAGOS", "CLIENTES_Y_OPORTUNIDADES"):
        banderas.append("posible cliente no registrado, confirmar con Sandra")

    # El ruido evidente no ensucia los grupos de trabajo, tiene su propio cajon.
    if prioridad == "P4" and (es_automatico or ruido) and not es_cliente:
        categoria = "RUIDO"

    if not correo.get("cuerpo_completo_leido"):
        banderas.append("solo snippet, cuerpo no leido")

    return {
        "id": correo.get("id"),
        "buzon": correo.get("buzon", "desconocido"),
        "remitente": correo.get("remitente_correo", ""),
        "nombre": correo.get("remitente_nombre", ""),
        "dominio": dominio,
        "asunto": correo.get("asunto", "(sin asunto)"),
        "fecha": correo.get("fecha"),
        "horas_transcurridas": round(horas, 1) if horas is not None else None,
        "tipo_remitente": tipo_remitente,
        "categoria": categoria,
        "evidencia_categoria": evidencia.get(categoria, []),
        "puntaje": puntaje,
        "prioridad": prioridad,
        "razones": razones,
        "banderas": banderas,
        "requiere_revision": bool(banderas) and prioridad in ("P1", "P2"),
    }


def construir_salida(correos, cfg):
    resultados = [clasificar_correo(c, cfg) for c in correos]
    resultados.sort(key=lambda r: (-r["puntaje"], r["asunto"]))

    por_prioridad = {n: [r for r in resultados if r["prioridad"] == n]
                     for n in ("P1", "P2", "P3", "P4")}
    por_categoria = {n: [r for r in resultados if r["categoria"] == n]
                     for n in ORDEN_CATEGORIAS}
    revisar = [r for r in resultados if r["requiere_revision"]]

    return {
        "generado": datetime.now(timezone.utc).isoformat(),
        "total": len(resultados),
        "conteo_prioridad": {k: len(v) for k, v in por_prioridad.items()},
        "conteo_categoria": {k: len(v) for k, v in por_categoria.items()},
        "por_prioridad": por_prioridad,
        "por_categoria": por_categoria,
        "revisar": revisar,
        "detalle": resultados,
    }


def linea(r):
    edad = f"{int(r['horas_transcurridas'])}h" if r["horas_transcurridas"] is not None else "fecha ND"
    quien = r["nombre"] or r["remitente"]
    return f"- **{quien}** ({r['dominio'] or 'sin dominio'}), {edad}, puntaje {r['puntaje']}\n  {r['asunto']}"


def a_markdown(salida, cfg):
    p = salida["conteo_prioridad"]
    c = salida["conteo_categoria"]
    L = []
    L.append("# matIA, informe de bandeja")
    L.append("")
    L.append(f"**{salida['total']} hilos analizados.** "
             f"P1 {p['P1']}, P2 {p['P2']}, P3 {p['P3']}, ruido {p['P4']}.")
    L.append("")

    if p["P1"]:
        L.append("## 🚨 ALERTA P1, hoy mismo")
        L.append("")
        for r in salida["por_prioridad"]["P1"]:
            L.append(linea(r))
            L.append(f"  _Por qué: {', '.join(r['razones'][:3])}_")
        L.append("")

    if p["P2"]:
        L.append("## ⚡ P2, 24 a 48 horas")
        L.append("")
        for r in salida["por_prioridad"]["P2"]:
            L.append(linea(r))
        L.append("")

    L.append("## 📅 AGENDAR")
    L.append("")
    L.extend([linea(r) for r in salida["por_categoria"]["AGENDAR"]] or ["Nada pendiente de agenda en esta ventana."])
    L.append("")
    L.append("## 💰 FACTURAS Y PAGOS")
    L.append("")
    L.extend([linea(r) for r in salida["por_categoria"]["FACTURAS_Y_PAGOS"]] or ["Nada de facturación en esta ventana."])
    L.append("")

    for cat in ("CLIENTES_Y_OPORTUNIDADES", "MARCA_Y_CONTENIDO", "OPERACION"):
        if c.get(cat):
            emoji = cfg["categorias"].get(cat, {}).get("emoji", "•")
            L.append(f"## {emoji} {NOMBRES_VISIBLES.get(cat, cat)}")
            L.append("")
            L.extend([linea(r) for r in salida["por_categoria"][cat]])
            L.append("")

    if salida["revisar"]:
        L.append("## ❓ REVISAR, matIA no está segura")
        L.append("")
        for r in salida["revisar"]:
            L.append(linea(r))
            L.append(f"  _Duda: {'; '.join(r['banderas'])}_")
        L.append("")

    if c.get("RUIDO"):
        L.append(f"## 🔕 Ruido, {c['RUIDO']} hilos, revisión en bloque")
        L.append("")
        L.extend([linea(r) for r in salida["por_categoria"]["RUIDO"]])
        L.append("")

    if c.get("SIN_CLASIFICAR"):
        L.append(f"## Sin clasificar, {c['SIN_CLASIFICAR']} hilos")
        L.append("")
        L.extend([linea(r) for r in salida["por_categoria"]["SIN_CLASIFICAR"]])
        L.append("")

    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="matIA, clasificador de correo")
    ap.add_argument("--entrada", help="Archivo JSON con la lista de correos. Sin esto, lee stdin.")
    ap.add_argument("--config", default=str(CONFIG_POR_DEFECTO))
    ap.add_argument("--salida", help="Archivo donde escribir el JSON de resultados")
    ap.add_argument("--markdown", action="store_true", help="Imprime el informe en markdown")
    args = ap.parse_args()

    cfg = cargar_config(args.config)
    crudo = Path(args.entrada).read_text(encoding="utf-8") if args.entrada else sys.stdin.read()
    correos = json.loads(crudo)
    if isinstance(correos, dict):
        correos = correos.get("correos", [])

    salida = construir_salida(correos, cfg)

    if args.salida:
        Path(args.salida).write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.markdown:
        print(a_markdown(salida, cfg))
    else:
        print(json.dumps(salida, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
