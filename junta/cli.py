"""CLI de la Junta Directiva Agéntica IAM™.

    python -m junta.cli                      # sesión interactiva
    python -m junta.cli --diagnostico        # revisa configuración y sale
    python -m junta.cli "¿Subo el precio?"   # una sola consulta
    python -m junta.cli --ejecutar "..."     # permite acciones hacia el exterior
"""

from __future__ import annotations

import argparse
import asyncio
import shutil
import sys

from junta.config import cargar_settings
from junta.junta import JuntaDirectiva

ROJO = "\033[38;2;192;0;0m"
GRIS = "\033[90m"
NEGRITA = "\033[1m"
FIN = "\033[0m"


def _banner() -> None:
    print(f"\n{ROJO}{NEGRITA}  JUNTA DIRECTIVA IAM™{FIN}")
    print(f"{GRIS}  Sistema agéntico de decisión para el negocio de Sandra Curvelo{FIN}\n")


def _imprimir_diagnostico(junta: JuntaDirectiva) -> None:
    d = junta.diagnostico()
    print(f"{NEGRITA}Contexto de negocio{FIN}")
    print(f"  {d['contexto']}")
    for doc in d["documentos"]:
        print(f"  {GRIS}·{FIN} {doc}")

    print(f"\n{NEGRITA}Consejeros{FIN}")
    for c in d["consejeros"]:
        print(f"  {GRIS}·{FIN} {c}")

    print(f"\n{NEGRITA}Conectores activos{FIN}")
    if d["conectores_activos"]:
        for c in d["conectores_activos"]:
            print(f"  {GRIS}·{FIN} {c}")
    else:
        print(f"  {GRIS}ninguno{FIN}")

    if d["conectores_faltantes"]:
        print(f"\n{NEGRITA}Conectores sin configurar{FIN}")
        for nombre, variables in d["conectores_faltantes"].items():
            print(f"  {ROJO}·{FIN} {nombre}{GRIS} → falta {variables}{FIN}")

    print(f"\n{NEGRITA}Estado{FIN}")
    print(f"  Memoria persistente: {'sí' if d['memoria'] else 'NO'}")
    print(f"  Modo lectura: {'sí' if d['modo_lectura'] else 'no (puede ejecutar)'}")
    print(f"  Modelo: {d['modelo']}")

    if d["datos_faltantes"]:
        print(f"\n{NEGRITA}Datos de negocio por completar ({len(d['datos_faltantes'])}){FIN}")
        for dato in d["datos_faltantes"][:12]:
            print(f"  {GRIS}·{FIN} {dato}")
        if len(d["datos_faltantes"]) > 12:
            print(f"  {GRIS}… y {len(d['datos_faltantes']) - 12} más{FIN}")
    print()


async def _deliberar(junta: JuntaDirectiva, asunto: str, verboso: bool) -> None:
    async for evento in junta.deliberar(asunto):
        if evento.tipo == "sistema":
            print(f"\n{ROJO}⚠ {evento.contenido}{FIN}\n")
        elif evento.tipo == "convocatoria":
            print(f"\n{ROJO}⭕ {evento.contenido}{FIN}")
        elif evento.tipo == "herramienta" and verboso:
            print(f"{GRIS}   ↳ {evento.contenido}{FIN}")
        elif evento.tipo == "pensamiento" and verboso:
            print(f"{GRIS}   … {evento.contenido[:160]}{FIN}")
        elif evento.tipo == "texto":
            print(evento.contenido, end="", flush=True)
        elif evento.tipo == "cierre":
            print("\n")


async def _sesion_interactiva(junta: JuntaDirectiva, verboso: bool) -> None:
    print(f"{GRIS}Escribe el asunto a tratar. 'salir' para terminar.{FIN}\n")
    while True:
        try:
            asunto = input(f"{ROJO}▸{FIN} ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not asunto:
            continue
        if asunto.lower() in {"salir", "exit", "quit"}:
            return
        await _deliberar(junta, asunto, verboso)


async def _main(args: argparse.Namespace) -> int:
    settings = cargar_settings(modo_lectura=not args.ejecutar)
    junta = JuntaDirectiva(settings)

    # El diagnóstico es una revisión de configuración: debe funcionar sin credenciales.
    if args.diagnostico:
        _banner()
        _imprimir_diagnostico(junta)
        return 0

    if not settings.anthropic_api_key and not shutil.which("claude"):
        print(
            f"{ROJO}Sin credenciales de Anthropic.{FIN} Define ANTHROPIC_API_KEY en "
            "tu .env, o inicia sesión con la CLI de Claude Code (`claude`), que el "
            "SDK reutiliza automáticamente.",
            file=sys.stderr,
        )
        return 1

    if junta.contexto.esta_vacio:
        print(
            f"{ROJO}Aviso:{FIN} la carpeta contexto/ está vacía. La junta no conoce "
            "el negocio y su utilidad será mínima.\n"
        )

    _banner()
    if args.verboso:
        _imprimir_diagnostico(junta)
    elif junta.conectores.avisos:
        print(f"{GRIS}Conectores sin configurar: "
              f"{len(junta.conectores.avisos)}. Usa --diagnostico para el detalle.{FIN}\n")

    if not settings.modo_lectura:
        print(
            f"{ROJO}⚠ MODO EJECUCIÓN:{FIN} la junta puede enviar WhatsApp, correos y "
            "publicar en Meta.\n"
        )

    async with junta:
        try:
            if args.asunto:
                await _deliberar(junta, " ".join(args.asunto), args.verboso)
            else:
                await _sesion_interactiva(junta, args.verboso)
        finally:
            junta.cerrar_sesion_memoria()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="junta",
        description="Junta Directiva Agéntica IAM™",
    )
    parser.add_argument("asunto", nargs="*", help="Asunto a someter a la junta.")
    parser.add_argument(
        "--diagnostico",
        action="store_true",
        help="Muestra el estado de configuración y sale.",
    )
    parser.add_argument(
        "--ejecutar",
        action="store_true",
        help="Permite acciones hacia el exterior (enviar WhatsApp, correo, publicar).",
    )
    parser.add_argument(
        "-v",
        "--verboso",
        action="store_true",
        help="Muestra herramientas consultadas y razonamiento.",
    )
    args = parser.parse_args()

    try:
        return asyncio.run(_main(args))
    except KeyboardInterrupt:
        print("\nSesión interrumpida.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
