"""Carga del contexto de negocio desde `contexto/`.

Todos los `.md` de la carpeta entran al prompt de sistema, ordenados por nombre de
archivo. No hay registro que mantener: si aparece un archivo nuevo, entra solo.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

MARCADOR_PENDIENTE = re.compile(r"⚠️\s*POR COMPLETAR:\s*(.+)")


@dataclass
class ContextoNegocio:
    """El contexto de negocio ya leído y listo para inyectar."""

    documentos: dict[str, str]
    pendientes: list[str]

    @property
    def esta_vacio(self) -> bool:
        return not self.documentos

    def como_bloque(self) -> str:
        """Serializa el contexto para el prompt de sistema."""
        if self.esta_vacio:
            return (
                "<contexto_negocio>\n"
                "La carpeta contexto/ está vacía. NO tienes información del negocio.\n"
                "Antes de opinar sobre cualquier cosa, dilo explícitamente y pide que\n"
                "se complete contexto/ o que se te den los datos en la conversación.\n"
                "</contexto_negocio>"
            )

        partes = ["<contexto_negocio>"]
        for nombre, texto in self.documentos.items():
            partes.append(f"\n<documento nombre=\"{nombre}\">\n{texto}\n</documento>")

        if self.pendientes:
            lista = "\n".join(f"- {p}" for p in self.pendientes)
            partes.append(
                "\n<datos_faltantes>\n"
                "Estos datos NO existen todavía. No los inventes ni los estimes en "
                "silencio. Si necesitas uno para responder: búscalo primero en los "
                "conectores (Airtable, Supabase, Notion) y, si no aparece, pídelo "
                "explícitamente diciendo qué dato falta y para qué lo necesitas.\n"
                f"{lista}\n"
                "</datos_faltantes>"
            )

        partes.append("\n</contexto_negocio>")
        return "".join(partes)

    def resumen(self) -> str:
        """Línea corta para logs y UI."""
        return (
            f"{len(self.documentos)} documento(s) de contexto, "
            f"{len(self.pendientes)} dato(s) por completar"
        )


def cargar_contexto(directorio: Path) -> ContextoNegocio:
    """Lee `directorio/*.md` y extrae los marcadores de datos faltantes."""
    documentos: dict[str, str] = {}
    pendientes: list[str] = []

    if not directorio.is_dir():
        return ContextoNegocio(documentos={}, pendientes=[])

    for archivo in sorted(directorio.glob("*.md")):
        if archivo.name.upper() == "README.MD":
            continue  # el README explica la carpeta, no describe el negocio
        texto = archivo.read_text(encoding="utf-8").strip()
        if not texto:
            continue
        documentos[archivo.stem] = texto
        for coincidencia in MARCADOR_PENDIENTE.finditer(texto):
            dato = coincidencia.group(1).strip()
            etiqueta = f"[{archivo.stem}] {dato}"
            if etiqueta not in pendientes:
                pendientes.append(etiqueta)

    return ContextoNegocio(documentos=documentos, pendientes=pendientes)
