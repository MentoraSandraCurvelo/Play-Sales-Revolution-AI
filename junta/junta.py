"""Orquestador de la Junta Directiva Agéntica IAM™."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any, AsyncIterator

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ThinkingBlock,
    ToolUseBlock,
)

from junta.conectores import construir_conectores
from junta.config import Settings, cargar_settings
from junta.consejeros import PROMPT_PRESIDENCIA, construir_consejeros
from junta.contexto import cargar_contexto
from junta.memoria.repositorio import RepositorioMemoria, crear_repositorio

# Herramientas internas que la junta puede usar sin pedir permiso. `Bash` queda fuera
# a propósito: una junta directiva no necesita ejecutar comandos, y concederlo abriría
# una superficie de acción muy superior a la que el trabajo requiere.
HERRAMIENTAS_BASE = [
    "Read",
    "Glob",
    "Grep",
    "Write",
    "Edit",
    "Agent",  # convocatoria de consejeros (subagentes)
    "Task",   # nombre alternativo de la misma herramienta según versión del SDK
    "Skill",
    "TodoWrite",
]

HERRAMIENTAS_CONVOCATORIA = {"Agent", "Task"}


@dataclass
class EventoJunta:
    """Un hecho observable durante la deliberación, para la UI y los logs."""

    tipo: str  # sistema | convocatoria | herramienta | pensamiento | texto | cierre
    contenido: str
    consejero: str | None = None
    datos: dict[str, Any] | None = None


class JuntaDirectiva:
    """Sesión de junta directiva.

    Uso típico:

        async with JuntaDirectiva() as junta:
            async for evento in junta.deliberar("¿Subo el precio del programa?"):
                print(evento.contenido)
    """

    def __init__(
        self,
        settings: Settings | None = None,
        reanudar: str | None = None,
        sesion_memoria_id: str | None = None,
    ) -> None:
        """
        Args:
            settings: configuración; si se omite se lee del entorno.
            reanudar: id de sesión del SDK a continuar, para mantener el hilo de la
                conversación entre invocaciones (lo usa la UI de Streamlit).
            sesion_memoria_id: id de la sesión ya abierta en Supabase, para seguir
                escribiendo en la misma en lugar de abrir una nueva.
        """
        self.settings = settings or cargar_settings()
        self.contexto = cargar_contexto(self.settings.dir_contexto)
        self.repo: RepositorioMemoria | None = crear_repositorio(self.settings)
        self.conectores = construir_conectores(self.settings, self.repo)
        self.consejeros = construir_consejeros(self.settings)

        self._cliente: ClaudeSDKClient | None = None
        self._reanudar = reanudar
        self._sesion_memoria_id: str | None = sesion_memoria_id
        self._sdk_session_id: str | None = reanudar
        self._orden_mensaje = 0
        self._sesion_abierta_aqui = False

        if sesion_memoria_id and self.conectores.fijar_sesion_memoria:
            self.conectores.fijar_sesion_memoria(sesion_memoria_id)

    @property
    def sdk_session_id(self) -> str | None:
        """Id de sesión del SDK, disponible tras la primera deliberación."""
        return self._sdk_session_id

    @property
    def sesion_memoria_id(self) -> str | None:
        """Id de la sesión en Supabase, si la memoria está activa."""
        return self._sesion_memoria_id

    # ------------------------------------------------------------------
    # Configuración del agente
    # ------------------------------------------------------------------
    def _prompt_sistema(self) -> str:
        hoy = dt.date.today().isoformat()
        estado_conectores = (
            ", ".join(self.conectores.activos) if self.conectores.activos else "ninguno"
        )
        modo = "LECTURA (no ejecuta acciones hacia el exterior)" if self.settings.modo_lectura else "EJECUCIÓN"

        cabecera = (
            f"{PROMPT_PRESIDENCIA}\n\n"
            f"## Estado de esta sesión\n\n"
            f"- Fecha: {hoy}\n"
            f"- Conectores disponibles: {estado_conectores}\n"
            f"- Modo: {modo}\n"
            f"- Memoria persistente: {'activa' if self.repo else 'NO disponible'}\n"
        )

        if self.settings.modo_lectura:
            cabecera += (
                "\nEn modo lectura puedes **leer** de todos los conectores, pero los "
                "envíos hacia afuera (WhatsApp, correo, publicar en Meta) están "
                "bloqueados. Cuando la decisión implique uno de ellos, redacta el "
                "contenido propuesto y entrégalo para revisión de Sandra.\n"
            )

        if self.conectores.avisos:
            avisos = "\n".join(f"- {a}" for a in self.conectores.avisos)
            cabecera += (
                f"\n### Limitaciones de esta sesión\n{avisos}\n"
                "Cuando una de estas limitaciones te impida sostener una afirmación "
                "con datos, dilo explícitamente en tu respuesta.\n"
            )

        return f"{cabecera}\n\n{self.contexto.como_bloque()}"

    def _skills_del_proyecto(self) -> list[str]:
        """Nombres de las skills de `.claude/skills`.

        Se listan explícitamente en vez de usar `skills="all"`: eso último arrastra
        también las skills integradas de Claude Code (revisión de código, dataviz,
        configuración…), que son ruido para una junta de negocio y compiten por el
        contexto. Al leer el directorio, cualquier skill nueva entra sola.
        """
        directorio = self.settings.raiz / ".claude" / "skills"
        if not directorio.is_dir():
            return []
        return sorted(
            d.name for d in directorio.iterdir() if (d / "SKILL.md").is_file()
        )

    def _opciones(self) -> ClaudeAgentOptions:
        return ClaudeAgentOptions(
            system_prompt=self._prompt_sistema(),
            tools={"type": "preset", "preset": "claude_code"},
            agents=self.consejeros,
            mcp_servers=self.conectores.servidores,
            allowed_tools=HERRAMIENTAS_BASE + self.conectores.herramientas_permitidas,
            # `project` es lo que hace visibles las skills de `.claude/skills`. Los
            # conectores MCP se pasan por `mcp_servers`, no por un `.mcp.json`: si
            # añades uno al repo, sus servidores se sumarían a estos en lugar de
            # sustituirlos.
            setting_sources=["project"],
            skills=self._skills_del_proyecto(),
            model=self.settings.modelo_presidencia,
            effort=self.settings.esfuerzo,
            thinking={"type": "adaptive", "display": "summarized"},
            permission_mode="acceptEdits",
            cwd=str(self.settings.raiz),
            max_turns=self.settings.max_turnos,
            resume=self._reanudar,
        )

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------
    async def __aenter__(self) -> "JuntaDirectiva":
        self._cliente = ClaudeSDKClient(options=self._opciones())
        await self._cliente.connect()
        return self

    async def __aexit__(self, *_exc: object) -> None:
        # La sesión de memoria NO se cierra aquí a propósito. La UI de Streamlit crea
        # una instancia por turno reanudando la misma sesión: cerrarla al salir del
        # contexto la marcaría como terminada tras el primer mensaje. El cierre es
        # explícito, con `cerrar_sesion_memoria()`.
        if self._cliente:
            await self._cliente.disconnect()
            self._cliente = None

    def cerrar_sesion_memoria(self) -> None:
        """Marca la sesión de Supabase como cerrada.

        La llama quien sabe que la conversación terminó: el CLI al salir, o la UI
        cuando el usuario pulsa «Nueva sesión».
        """
        if self.repo and self._sesion_memoria_id:
            try:
                self.repo.cerrar_sesion(self._sesion_memoria_id)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Memoria
    # ------------------------------------------------------------------
    def _abrir_sesion_memoria(self, asunto: str) -> None:
        if not self.repo or self._sesion_memoria_id:
            return
        try:
            titulo = asunto.strip().splitlines()[0][:120] or "Sesión de junta"
            fila = self.repo.abrir_sesion(
                titulo=titulo,
                tema=asunto[:2000],
                sdk_session_id=self._sdk_session_id,
                metadata={
                    "conectores": self.conectores.activos,
                    "modo_lectura": self.settings.modo_lectura,
                    "modelo": self.settings.modelo_presidencia,
                },
            )
            self._sesion_memoria_id = fila["id"]
            self._sesion_abierta_aqui = True
            if self.conectores.fijar_sesion_memoria:
                self.conectores.fijar_sesion_memoria(self._sesion_memoria_id)
        except Exception:
            # Sin memoria se puede deliberar; sin junta, no.
            self._sesion_memoria_id = None

    def _guardar(self, rol: str, contenido: str, consejero: str | None = None) -> None:
        if not (self.repo and self._sesion_memoria_id and contenido.strip()):
            return
        self._orden_mensaje += 1
        try:
            self.repo.registrar_mensaje(
                sesion_id=self._sesion_memoria_id,
                orden=self._orden_mensaje,
                rol=rol,
                contenido=contenido,
                consejero=consejero,
            )
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Deliberación
    # ------------------------------------------------------------------
    async def deliberar(self, asunto: str) -> AsyncIterator[EventoJunta]:
        """Somete un asunto a la junta y emite los eventos de la deliberación."""
        if self._cliente is None:
            raise RuntimeError(
                "La junta no está conectada. Úsala con `async with JuntaDirectiva()`."
            )

        self._abrir_sesion_memoria(asunto)
        self._guardar("usuario", asunto)

        await self._cliente.query(asunto)

        respuesta_final: list[str] = []

        async for mensaje in self._cliente.receive_response():
            if isinstance(mensaje, SystemMessage):
                if mensaje.subtype == "init":
                    self._sdk_session_id = mensaje.data.get("session_id")
                    fallidos = [
                        s
                        for s in mensaje.data.get("mcp_servers", [])
                        if s.get("status") in ("failed", "needs-auth")
                    ]
                    if fallidos:
                        nombres = ", ".join(
                            f"{s.get('name')} ({s.get('status')})" for s in fallidos
                        )
                        yield EventoJunta(
                            tipo="sistema",
                            contenido=f"Conectores no disponibles: {nombres}",
                            datos={"servidores": fallidos},
                        )
                continue

            if isinstance(mensaje, AssistantMessage):
                for bloque in mensaje.content:
                    if isinstance(bloque, ThinkingBlock):
                        yield EventoJunta(tipo="pensamiento", contenido=bloque.thinking)

                    elif isinstance(bloque, TextBlock):
                        respuesta_final.append(bloque.text)
                        yield EventoJunta(tipo="texto", contenido=bloque.text)

                    elif isinstance(bloque, ToolUseBlock):
                        yield self._evento_de_herramienta(bloque)
                continue

            if isinstance(mensaje, ResultMessage):
                texto = "".join(respuesta_final).strip()
                self._guardar("presidencia", texto)
                yield EventoJunta(
                    tipo="cierre",
                    contenido=texto,
                    datos={
                        "terminal_reason": getattr(mensaje, "terminal_reason", None),
                        "sesion_memoria_id": self._sesion_memoria_id,
                    },
                )

    def _evento_de_herramienta(self, bloque: ToolUseBlock) -> EventoJunta:
        """Traduce una llamada a herramienta en algo legible para la UI."""
        if bloque.name in HERRAMIENTAS_CONVOCATORIA:
            consejero = bloque.input.get("subagent_type", "consejero")
            encargo = str(
                bloque.input.get("description") or bloque.input.get("prompt", "")
            )[:400]
            return EventoJunta(
                tipo="convocatoria",
                contenido=f"Se convoca a **{consejero}**",
                consejero=consejero,
                datos={"encargo": encargo},
            )

        if bloque.name.startswith("mcp__"):
            partes = bloque.name.split("__")
            servidor = partes[1] if len(partes) > 1 else "?"
            herramienta = partes[2] if len(partes) > 2 else "?"
            return EventoJunta(
                tipo="herramienta",
                contenido=f"Consulta a {servidor}: {herramienta}",
                datos={"entrada": bloque.input},
            )

        return EventoJunta(
            tipo="herramienta",
            contenido=f"Herramienta: {bloque.name}",
            datos={"entrada": bloque.input},
        )

    # ------------------------------------------------------------------
    # Atajo síncrono en texto
    # ------------------------------------------------------------------
    async def responder(self, asunto: str) -> str:
        """Delibera y devuelve solo el texto final."""
        final = ""
        async for evento in self.deliberar(asunto):
            if evento.tipo == "cierre":
                final = evento.contenido
        return final

    # ------------------------------------------------------------------
    # Diagnóstico
    # ------------------------------------------------------------------
    def diagnostico(self) -> dict[str, Any]:
        """Estado de la junta antes de arrancar. Útil para la UI y el CLI."""
        return {
            "contexto": self.contexto.resumen(),
            "documentos": sorted(self.contexto.documentos),
            "datos_faltantes": self.contexto.pendientes,
            "consejeros": sorted(self.consejeros),
            "conectores_activos": self.conectores.activos,
            "conectores_faltantes": self.settings.conectores_faltantes(),
            "avisos": self.conectores.avisos,
            "memoria": bool(self.repo),
            "modo_lectura": self.settings.modo_lectura,
            "modelo": self.settings.modelo_presidencia,
        }
