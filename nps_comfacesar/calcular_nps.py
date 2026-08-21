"""
Calculadora de NPS — IAM(TM) Intelligence / Comfacesar

Dos fuentes de datos:

  1) Reacciones de Slack (Opcion A) — se pasan como "nota:cantidad"
     python3 calcular_nps.py --slack "10:2,9:1,8:2,6:1"

  2) Respuestas de la app web (Opcion B)
     python3 calcular_nps.py --csv nps_comfacesar/respuestas_nps.csv

  Desglose por area (21 areas del programa en Comfacesar):
     python3 calcular_nps.py --csv nps_comfacesar/respuestas_nps.csv --por-area

Devuelve el NPS, la lectura estrategica y un resumen listo para pegar en Slack.
"""

import argparse
import csv
import sys


def clasificar(notas):
    total = len(notas)
    if total == 0:
        return None
    promotores = sum(1 for n in notas if n >= 9)
    pasivos = sum(1 for n in notas if 7 <= n <= 8)
    detractores = sum(1 for n in notas if n <= 6)
    return {
        "total": total,
        "promotores": promotores,
        "pasivos": pasivos,
        "detractores": detractores,
        "nps": round((promotores - detractores) / total * 100),
    }


def lectura(nps):
    if nps > 50:
        return "Excelente — el grupo es embajador del programa. Momento de pedir testimonio y referidos internos."
    if nps >= 20:
        return "Bueno — base solida. La palanca esta en convertir pasivos en promotores: preguntarles que les falta."
    if nps >= 0:
        return "A mejorar — revisar ritmo, nivel y acompanamiento antes de la siguiente sesion."
    return "Alerta — conversacion 1:1 con los detractores esta misma semana, antes de la proxima sesion."


def parse_slack(texto):
    notas = []
    for parte in texto.split(","):
        parte = parte.strip()
        if not parte:
            continue
        nota, _, cantidad = parte.partition(":")
        nota = int(nota)
        if not 0 <= nota <= 10:
            raise ValueError(f"Nota fuera de rango 0-10: {nota}")
        notas.extend([nota] * int(cantidad or 1))
    return notas


def parse_csv(ruta):
    with open(ruta, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    return [int(fila["nps"]) for fila in filas if str(fila.get("nps", "")).strip()]


def por_area(ruta):
    """Agrupa las notas NPS por area y devuelve el desglose ordenado."""
    with open(ruta, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    grupos = {}
    for fila in filas:
        area = (fila.get("area") or "Sin area").strip() or "Sin area"
        if str(fila.get("nps", "")).strip():
            grupos.setdefault(area, []).append(int(fila["nps"]))
    desglose = [(area, clasificar(notas)) for area, notas in grupos.items()]
    return sorted(desglose, key=lambda x: x[1]["nps"], reverse=True)


def deltas_confianza(ruta):
    with open(ruta, newline="", encoding="utf-8") as f:
        filas = [r for r in csv.DictReader(f) if str(r.get("confianza_hoy", "")).strip()]
    if not filas:
        return None
    antes = sum(int(r["confianza_antes"]) for r in filas) / len(filas)
    hoy = sum(int(r["confianza_hoy"]) for r in filas) / len(filas)
    return antes, hoy


def main():
    p = argparse.ArgumentParser(description="Calculadora de NPS IAM Intelligence")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--slack", help='Conteo de reacciones, formato "10:2,9:1,7:3"')
    g.add_argument("--csv", help="Ruta al CSV de respuestas de la app web")
    p.add_argument("--por-area", action="store_true",
                   help="Anade el desglose de NPS por area (solo con --csv)")
    args = p.parse_args()

    if args.por_area and not args.csv:
        p.error("--por-area requiere --csv")

    if args.slack:
        notas = parse_slack(args.slack)
        confianza = None
    else:
        notas = parse_csv(args.csv)
        confianza = deltas_confianza(args.csv)

    r = clasificar(notas)
    if r is None:
        print("No hay respuestas para calcular.")
        return 1

    pct = lambda n: round(n / r["total"] * 100)
    print()
    print("  PULSO NPS — IAM(TM) Intelligence / Comfacesar")
    print("  " + "-" * 46)
    print(f"  Respuestas .... {r['total']}")
    print(f"  Promotores .... {r['promotores']}  ({pct(r['promotores'])}%)   notas 9-10")
    print(f"  Pasivos ....... {r['pasivos']}  ({pct(r['pasivos'])}%)   notas 7-8")
    print(f"  Detractores ... {r['detractores']}  ({pct(r['detractores'])}%)   notas 0-6")
    print("  " + "-" * 46)
    print(f"  NPS ........... {r['nps']:+d}")
    print(f"  Lectura ....... {lectura(r['nps'])}")
    if confianza:
        antes, hoy = confianza
        print(f"  Confianza IA .. {antes:.1f} -> {hoy:.1f}  ({hoy - antes:+.1f} puntos)")
    if args.csv and args.por_area:
        print()
        print("  DESGLOSE POR AREA")
        print("  " + "-" * 46)
        print(f"  {'Area':<24}{'Resp':>5}{'NPS':>7}")
        for area, r_area in por_area(args.csv):
            print(f"  {area:<24}{r_area['total']:>5}{r_area['nps']:>+7d}")
        print()
        criticas = [a for a, r_a in por_area(args.csv) if r_a["nps"] < 0]
        if criticas:
            print(f"  Areas en alerta (NPS negativo): {', '.join(criticas)}")
            print("  -> Conversacion 1:1 con esas areas antes de la siguiente sesion.")

    print()
    print("  --- Resumen para pegar en Slack ---")
    print()
    linea = (f"  *NPS del grupo: {r['nps']:+d}* — {r['promotores']} promotores, "
             f"{r['pasivos']} pasivos, {r['detractores']} detractores sobre {r['total']} respuestas.")
    print(linea)
    if confianza:
        antes, hoy = confianza
        print(f"  *Confianza usando IA:* pasamos de {antes:.1f} a {hoy:.1f} "
              f"— *{hoy - antes:+.1f} puntos en lo que va del programa.*")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
