"""Persistencia en SQLite: historial de conversaciones, leads y control de duplicados.

Meta reintenta los webhooks, así que guardar los IDs ya procesados es lo que
evita que el agente conteste dos veces al mismo mensaje.
"""

import asyncio
import json
import sqlite3
import threading
import time
from typing import Any

from . import config

_lock = threading.Lock()
_conexion: sqlite3.Connection | None = None


def _db() -> sqlite3.Connection:
    global _conexion
    if _conexion is None:
        _conexion = sqlite3.connect(config.DB_PATH, check_same_thread=False)
        _conexion.execute("PRAGMA journal_mode=WAL")
        _conexion.executescript(
            """
            CREATE TABLE IF NOT EXISTS conversaciones (
                wa_id       TEXT PRIMARY KEY,
                nombre      TEXT,
                historial   TEXT NOT NULL DEFAULT '[]',
                pausada     INTEGER NOT NULL DEFAULT 0,
                actualizado REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS mensajes_vistos (
                message_id TEXT PRIMARY KEY,
                visto_en   REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS leads (
                wa_id       TEXT PRIMARY KEY,
                nombre      TEXT,
                empresa     TEXT,
                cargo       TEXT,
                necesidad   TEXT,
                urgencia    TEXT,
                temperatura TEXT,
                notas       TEXT,
                actualizado REAL NOT NULL
            );
            """
        )
        _conexion.commit()
    return _conexion


# --- Duplicados -------------------------------------------------------------

def _marcar_visto(message_id: str) -> bool:
    """Devuelve True si es la primera vez que vemos este mensaje."""
    with _lock:
        db = _db()
        try:
            db.execute(
                "INSERT INTO mensajes_vistos (message_id, visto_en) VALUES (?, ?)",
                (message_id, time.time()),
            )
        except sqlite3.IntegrityError:
            return False
        # Limpieza: no guardamos IDs de más de 3 días.
        db.execute("DELETE FROM mensajes_vistos WHERE visto_en < ?", (time.time() - 259200,))
        db.commit()
        return True


async def es_mensaje_nuevo(message_id: str) -> bool:
    return await asyncio.to_thread(_marcar_visto, message_id)


# --- Conversaciones ---------------------------------------------------------

def _leer_conversacion(wa_id: str) -> dict[str, Any]:
    with _lock:
        fila = _db().execute(
            "SELECT nombre, historial, pausada FROM conversaciones WHERE wa_id = ?", (wa_id,)
        ).fetchone()
    if fila is None:
        return {"nombre": None, "historial": [], "pausada": False}
    return {"nombre": fila[0], "historial": json.loads(fila[1]), "pausada": bool(fila[2])}


async def leer_conversacion(wa_id: str) -> dict[str, Any]:
    return await asyncio.to_thread(_leer_conversacion, wa_id)


def _guardar_conversacion(wa_id: str, nombre: str | None, historial: list, pausada: bool) -> None:
    recorte = historial[-config.MAX_TURNOS_HISTORIAL:]
    with _lock:
        db = _db()
        db.execute(
            """
            INSERT INTO conversaciones (wa_id, nombre, historial, pausada, actualizado)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(wa_id) DO UPDATE SET
                nombre      = COALESCE(excluded.nombre, conversaciones.nombre),
                historial   = excluded.historial,
                pausada     = excluded.pausada,
                actualizado = excluded.actualizado
            """,
            (wa_id, nombre, json.dumps(recorte, ensure_ascii=False), int(pausada), time.time()),
        )
        db.commit()


async def guardar_conversacion(wa_id: str, nombre: str | None, historial: list, pausada: bool) -> None:
    await asyncio.to_thread(_guardar_conversacion, wa_id, nombre, historial, pausada)


def _pausar(wa_id: str, pausada: bool) -> None:
    with _lock:
        db = _db()
        db.execute(
            """
            INSERT INTO conversaciones (wa_id, historial, pausada, actualizado)
            VALUES (?, '[]', ?, ?)
            ON CONFLICT(wa_id) DO UPDATE SET pausada = excluded.pausada, actualizado = excluded.actualizado
            """,
            (wa_id, int(pausada), time.time()),
        )
        db.commit()


async def pausar(wa_id: str, pausada: bool = True) -> None:
    await asyncio.to_thread(_pausar, wa_id, pausada)


# --- Leads ------------------------------------------------------------------

def _guardar_lead(wa_id: str, datos: dict[str, Any]) -> None:
    with _lock:
        db = _db()
        db.execute(
            """
            INSERT INTO leads (wa_id, nombre, empresa, cargo, necesidad, urgencia, temperatura, notas, actualizado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(wa_id) DO UPDATE SET
                nombre      = COALESCE(NULLIF(excluded.nombre, ''), leads.nombre),
                empresa     = COALESCE(NULLIF(excluded.empresa, ''), leads.empresa),
                cargo       = COALESCE(NULLIF(excluded.cargo, ''), leads.cargo),
                necesidad   = COALESCE(NULLIF(excluded.necesidad, ''), leads.necesidad),
                urgencia    = excluded.urgencia,
                temperatura = excluded.temperatura,
                notas       = COALESCE(NULLIF(excluded.notas, ''), leads.notas),
                actualizado = excluded.actualizado
            """,
            (
                wa_id,
                datos.get("nombre", ""),
                datos.get("empresa", ""),
                datos.get("cargo", ""),
                datos.get("necesidad", ""),
                datos.get("urgencia", "desconocida"),
                datos.get("temperatura", "frio"),
                datos.get("notas", ""),
                time.time(),
            ),
        )
        db.commit()


async def guardar_lead(wa_id: str, datos: dict[str, Any]) -> None:
    await asyncio.to_thread(_guardar_lead, wa_id, datos)


def _listar_leads(limite: int) -> list[dict[str, Any]]:
    with _lock:
        filas = _db().execute(
            """
            SELECT wa_id, nombre, empresa, cargo, necesidad, urgencia, temperatura, notas, actualizado
            FROM leads ORDER BY actualizado DESC LIMIT ?
            """,
            (limite,),
        ).fetchall()
    campos = ("wa_id", "nombre", "empresa", "cargo", "necesidad", "urgencia", "temperatura", "notas", "actualizado")
    return [dict(zip(campos, fila)) for fila in filas]


async def listar_leads(limite: int = 50) -> list[dict[str, Any]]:
    return await asyncio.to_thread(_listar_leads, limite)
