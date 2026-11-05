"""Corre una jornada de MATIA desde la terminal y guarda los 10 correos como HTML en salida_matia/.

Uso:  python run_matia.py [dias_a_simular]
Todo es simulado: no se envía ningún correo real.
"""

import json
import sys
from datetime import date, timedelta
from pathlib import Path

from matia.agente import ejecutar_dia
from matia.crm_simulado import crear_pipeline


def main(dias: int = 1) -> None:
    hoy = date.today()
    deals = crear_pipeline(hoy)
    salida = Path("salida_matia")
    salida.mkdir(exist_ok=True)
    for i in range(dias):
        dia = hoy + timedelta(days=i)
        jornada = ejecutar_dia(deals, dia)
        carpeta = salida / dia.isoformat()
        carpeta.mkdir(exist_ok=True)
        for n, c in enumerate(jornada["enviados"], start=1):
            (carpeta / f"{n:02d}_deal{c['deal_id']}.html").write_text(c["html"], encoding="utf-8")
        resumen = [{k: v for k, v in c.items() if k != "html"} for c in jornada["enviados"]]
        (carpeta / "bitacora.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{dia}: {len(resumen)} correos simulados -> {carpeta}")
    demo = next(d for d in deals if d.demo)
    print(f"Cliente Demo quedó en etapa: {demo.etapa} con {demo.toques_matia} toques")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
