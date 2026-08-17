"""Repositorio de memoria de la junta sobre Supabase.

Encapsula todo el acceso a las tablas `junta_*`. Si Supabase no está configurado,
`crear_repositorio` devuelve None y la junta funciona sin memoria persistente (lo
avisa en el arranque).
"""

from __future__ import annotations

import datetime as dt
from typing import Any

from junta.config import Settings


class MemoriaNoDisponible(RuntimeError):
    """Se intentó usar la memoria sin Supabase configurado o accesible."""


class RepositorioMemoria:
    """Acceso a la memoria de la junta.

    Todos los métodos devuelven estructuras Python simples (dict/list) para que el
    servidor MCP pueda serializarlas sin conocer detalles de Supabase.
    """

    def __init__(self, cliente: Any) -> None:
        self._db = cliente

    # ------------------------------------------------------------------
    # Sesiones
    # ------------------------------------------------------------------
    def abrir_sesion(
        self,
        titulo: str,
        tema: str | None = None,
        sdk_session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        fila = {
            "titulo": titulo,
            "tema": tema,
            "sdk_session_id": sdk_session_id,
            "metadata": metadata or {},
        }
        resp = self._db.table("junta_sesiones").insert(fila).execute()
        return resp.data[0]

    def cerrar_sesion(self, sesion_id: str) -> None:
        self._db.table("junta_sesiones").update(
            {"estado": "cerrada", "cerrada_en": dt.datetime.now(dt.UTC).isoformat()}
        ).eq("id", sesion_id).execute()

    def sesiones_recientes(self, limite: int = 10) -> list[dict[str, Any]]:
        resp = (
            self._db.table("junta_sesiones")
            .select("id, titulo, tema, estado, creada_en")
            .order("creada_en", desc=True)
            .limit(limite)
            .execute()
        )
        return resp.data or []

    # ------------------------------------------------------------------
    # Transcripción
    # ------------------------------------------------------------------
    def registrar_mensaje(
        self,
        sesion_id: str,
        orden: int,
        rol: str,
        contenido: str,
        consejero: str | None = None,
    ) -> None:
        self._db.table("junta_mensajes").insert(
            {
                "sesion_id": sesion_id,
                "orden": orden,
                "rol": rol,
                "consejero": consejero,
                "contenido": contenido,
            }
        ).execute()

    def transcripcion(self, sesion_id: str) -> list[dict[str, Any]]:
        resp = (
            self._db.table("junta_mensajes")
            .select("orden, rol, consejero, contenido, creado_en")
            .eq("sesion_id", sesion_id)
            .order("orden")
            .execute()
        )
        return resp.data or []

    # ------------------------------------------------------------------
    # Decisiones
    # ------------------------------------------------------------------
    def registrar_decision(
        self,
        asunto: str,
        decision: str,
        fundamento: str | None = None,
        consejeros: list[str] | None = None,
        desacuerdos: str | None = None,
        sesion_id: str | None = None,
    ) -> dict[str, Any]:
        resp = (
            self._db.table("junta_decisiones")
            .insert(
                {
                    "sesion_id": sesion_id,
                    "asunto": asunto,
                    "decision": decision,
                    "fundamento": fundamento,
                    "consejeros_convocados": consejeros or [],
                    "desacuerdos": desacuerdos,
                }
            )
            .execute()
        )
        return resp.data[0]

    def buscar_decisiones(
        self, consulta: str | None = None, limite: int = 10
    ) -> list[dict[str, Any]]:
        q = self._db.table("junta_decisiones").select(
            "id, asunto, decision, fundamento, desacuerdos, "
            "consejeros_convocados, creada_en"
        )
        if consulta:
            # `or_` con ilike sobre asunto y decisión: búsqueda simple y predecible.
            patron = f"%{consulta}%"
            q = q.or_(f"asunto.ilike.{patron},decision.ilike.{patron}")
        resp = q.order("creada_en", desc=True).limit(limite).execute()
        return resp.data or []

    # ------------------------------------------------------------------
    # Acuerdos
    # ------------------------------------------------------------------
    def registrar_acuerdo(
        self,
        acuerdo: str,
        responsable: str,
        fecha_limite: str | None = None,
        metrica: str | None = None,
        sesion_id: str | None = None,
        decision_id: str | None = None,
    ) -> dict[str, Any]:
        resp = (
            self._db.table("junta_acuerdos")
            .insert(
                {
                    "sesion_id": sesion_id,
                    "decision_id": decision_id,
                    "acuerdo": acuerdo,
                    "responsable": responsable,
                    "fecha_limite": fecha_limite,
                    "metrica": metrica,
                }
            )
            .execute()
        )
        return resp.data[0]

    def acuerdos(
        self, estado: str | None = "abierto", limite: int = 50
    ) -> list[dict[str, Any]]:
        q = self._db.table("junta_acuerdos").select(
            "id, acuerdo, responsable, fecha_limite, metrica, estado, creado_en"
        )
        if estado and estado != "todos":
            q = q.eq("estado", estado)
        resp = q.order("fecha_limite", desc=False).limit(limite).execute()
        return resp.data or []

    def actualizar_acuerdo(self, acuerdo_id: str, estado: str) -> dict[str, Any] | None:
        resp = (
            self._db.table("junta_acuerdos")
            .update({"estado": estado})
            .eq("id", acuerdo_id)
            .execute()
        )
        return resp.data[0] if resp.data else None

    # ------------------------------------------------------------------
    # KPIs
    # ------------------------------------------------------------------
    def registrar_kpi(
        self,
        periodo: str,
        nombre: str,
        valor: float,
        unidad: str | None = None,
        fuente: str | None = None,
        nota: str | None = None,
    ) -> dict[str, Any]:
        resp = (
            self._db.table("junta_kpis")
            .upsert(
                {
                    "periodo": periodo,
                    "nombre": nombre,
                    "valor": valor,
                    "unidad": unidad,
                    "fuente": fuente,
                    "nota": nota,
                },
                on_conflict="periodo,nombre",
            )
            .execute()
        )
        return resp.data[0]

    def kpis(
        self, nombre: str | None = None, limite: int = 60
    ) -> list[dict[str, Any]]:
        q = self._db.table("junta_kpis").select(
            "periodo, nombre, valor, unidad, fuente, nota"
        )
        if nombre:
            q = q.eq("nombre", nombre)
        resp = q.order("periodo", desc=True).limit(limite).execute()
        return resp.data or []

    # ------------------------------------------------------------------
    # Datos faltantes
    # ------------------------------------------------------------------
    def registrar_dato_faltante(
        self,
        dato: str,
        para_que: str | None = None,
        sesion_id: str | None = None,
    ) -> dict[str, Any]:
        resp = (
            self._db.table("junta_datos_faltantes")
            .insert({"sesion_id": sesion_id, "dato": dato, "para_que": para_que})
            .execute()
        )
        return resp.data[0]

    def datos_faltantes(self, incluir_resueltos: bool = False) -> list[dict[str, Any]]:
        q = self._db.table("junta_datos_faltantes").select(
            "id, dato, para_que, resuelto, creado_en"
        )
        if not incluir_resueltos:
            q = q.eq("resuelto", False)
        resp = q.order("creado_en", desc=True).limit(100).execute()
        return resp.data or []

    # ------------------------------------------------------------------
    # Vista de arranque
    # ------------------------------------------------------------------
    def informe_apertura(self) -> dict[str, Any]:
        """Lo que la junta debe saber antes de empezar una sesión nueva."""
        return {
            "acuerdos_abiertos": self.acuerdos(estado="abierto", limite=20),
            "ultimas_decisiones": self.buscar_decisiones(limite=5),
            "datos_faltantes": self.datos_faltantes(),
            "sesiones_recientes": self.sesiones_recientes(limite=5),
        }


def crear_repositorio(settings: Settings) -> RepositorioMemoria | None:
    """Crea el repositorio si Supabase está configurado; si no, devuelve None."""
    if not settings.tiene_supabase:
        return None
    try:
        from supabase import create_client
    except ImportError as exc:  # pragma: no cover
        raise MemoriaNoDisponible(
            "Falta el paquete `supabase`. Instala con: pip install supabase"
        ) from exc

    cliente = create_client(settings.supabase_url, settings.supabase_key)  # type: ignore[arg-type]
    return RepositorioMemoria(cliente)
