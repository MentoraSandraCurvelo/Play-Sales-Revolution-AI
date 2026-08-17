"""Servidor MCP in-process: memoria de la junta sobre Supabase.

Expone la memoria como herramientas `mcp__memoria__*` para que los consejeros puedan
consultar lo que se decidió antes y dejar registro de lo que se decide ahora.
"""

from __future__ import annotations

from typing import Any

from claude_agent_sdk import create_sdk_mcp_server, tool

from junta.conectores._util import datos, error, texto
from junta.memoria.repositorio import RepositorioMemoria


def construir_servidor_memoria(
    repo: RepositorioMemoria,
    sesion_id_actual: str | None = None,
) -> Any:
    """Crea el servidor MCP de memoria ligado a un repositorio y sesión."""

    # `sesion_id_actual` puede fijarse después de crear el servidor, por eso vive en
    # un contenedor mutable en lugar de capturarse por valor.
    estado = {"sesion_id": sesion_id_actual}

    def fijar_sesion(sesion_id: str | None) -> None:
        estado["sesion_id"] = sesion_id

    # ------------------------------------------------------------------
    # Lectura
    # ------------------------------------------------------------------
    @tool(
        "informe_apertura",
        "Devuelve todo lo que la junta debe saber antes de empezar a deliberar: "
        "acuerdos abiertos de sesiones anteriores, últimas decisiones tomadas, datos "
        "que quedaron pendientes y sesiones recientes. Úsalo al INICIO de una sesión.",
        {"type": "object", "properties": {}, "additionalProperties": False},
    )
    async def informe_apertura(_args: dict[str, Any]) -> dict[str, Any]:
        try:
            return datos(repo.informe_apertura(), "Memoria de la junta al abrir sesión")
        except Exception as exc:
            return error(f"no se pudo leer la memoria: {exc}")

    @tool(
        "buscar_decisiones",
        "Busca decisiones anteriores de la junta por texto libre en el asunto o en la "
        "decisión. Úsalo para saber si un tema ya se discutió y qué se resolvió, y "
        "para detectar si lo que se propone hoy contradice algo ya decidido.",
        {
            "type": "object",
            "properties": {
                "consulta": {
                    "type": "string",
                    "description": "Texto a buscar. Omítelo para traer las más recientes.",
                },
                "limite": {"type": "integer", "default": 10, "maximum": 50},
            },
            "additionalProperties": False,
        },
    )
    async def buscar_decisiones(args: dict[str, Any]) -> dict[str, Any]:
        try:
            filas = repo.buscar_decisiones(
                consulta=args.get("consulta"), limite=int(args.get("limite", 10))
            )
            if not filas:
                return texto("No hay decisiones registradas que coincidan.")
            return datos(filas, f"{len(filas)} decisión(es) encontrada(s)")
        except Exception as exc:
            return error(f"no se pudo buscar decisiones: {exc}")

    @tool(
        "listar_acuerdos",
        "Lista los acuerdos de la junta y su estado. Por defecto trae los abiertos, "
        "ordenados por fecha límite. Úsalo para revisar qué quedó pendiente.",
        {
            "type": "object",
            "properties": {
                "estado": {
                    "type": "string",
                    "enum": ["abierto", "en_progreso", "cumplido", "cancelado", "todos"],
                    "default": "abierto",
                },
                "limite": {"type": "integer", "default": 50, "maximum": 100},
            },
            "additionalProperties": False,
        },
    )
    async def listar_acuerdos(args: dict[str, Any]) -> dict[str, Any]:
        try:
            filas = repo.acuerdos(
                estado=args.get("estado", "abierto"), limite=int(args.get("limite", 50))
            )
            if not filas:
                return texto("No hay acuerdos con ese estado.")
            return datos(filas, f"{len(filas)} acuerdo(s)")
        except Exception as exc:
            return error(f"no se pudo listar acuerdos: {exc}")

    @tool(
        "consultar_kpis",
        "Devuelve el histórico de un KPI del negocio (o de todos) por período. "
        "Úsalo antes de afirmar una tendencia: la serie histórica está aquí.",
        {
            "type": "object",
            "properties": {
                "nombre": {
                    "type": "string",
                    "description": "Nombre exacto del KPI. Omítelo para traer todos.",
                },
                "limite": {"type": "integer", "default": 60, "maximum": 200},
            },
            "additionalProperties": False,
        },
    )
    async def consultar_kpis(args: dict[str, Any]) -> dict[str, Any]:
        try:
            filas = repo.kpis(
                nombre=args.get("nombre"), limite=int(args.get("limite", 60))
            )
            if not filas:
                return texto(
                    "No hay KPIs registrados. Regístralos con `registrar_kpi` a medida "
                    "que la junta los calcule, para construir la serie histórica."
                )
            return datos(filas, f"{len(filas)} registro(s) de KPI")
        except Exception as exc:
            return error(f"no se pudo consultar KPIs: {exc}")

    @tool(
        "listar_datos_faltantes",
        "Lista los datos del negocio que la junta ha echado en falta en sesiones "
        "anteriores y siguen sin resolverse.",
        {
            "type": "object",
            "properties": {
                "incluir_resueltos": {"type": "boolean", "default": False}
            },
            "additionalProperties": False,
        },
    )
    async def listar_datos_faltantes(args: dict[str, Any]) -> dict[str, Any]:
        try:
            filas = repo.datos_faltantes(
                incluir_resueltos=bool(args.get("incluir_resueltos", False))
            )
            if not filas:
                return texto("No hay datos faltantes registrados.")
            return datos(filas, f"{len(filas)} dato(s) faltante(s)")
        except Exception as exc:
            return error(f"no se pudo listar datos faltantes: {exc}")

    # ------------------------------------------------------------------
    # Escritura (memoria interna: siempre permitida, no sale del negocio)
    # ------------------------------------------------------------------
    @tool(
        "registrar_decision",
        "Registra una decisión formal de la junta en la memoria. Úsalo al cerrar "
        "una sesión, una decisión por llamada. Incluye los desacuerdos si los hubo: "
        "una decisión sin su disenso registrado pierde su información más valiosa.",
        {
            "type": "object",
            "properties": {
                "asunto": {"type": "string", "description": "Qué se estaba decidiendo."},
                "decision": {"type": "string", "description": "Qué se resolvió."},
                "fundamento": {
                    "type": "string",
                    "description": "Las cifras y razones que sostienen la decisión.",
                },
                "consejeros": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Consejeros convocados en esta decisión.",
                },
                "desacuerdos": {
                    "type": "string",
                    "description": "Quién discrepó y por qué. Vacío si hubo consenso.",
                },
            },
            "required": ["asunto", "decision"],
            "additionalProperties": False,
        },
    )
    async def registrar_decision(args: dict[str, Any]) -> dict[str, Any]:
        try:
            fila = repo.registrar_decision(
                asunto=args["asunto"],
                decision=args["decision"],
                fundamento=args.get("fundamento"),
                consejeros=args.get("consejeros"),
                desacuerdos=args.get("desacuerdos"),
                sesion_id=estado["sesion_id"],
            )
            return texto(f"Decisión registrada con id {fila['id']}.")
        except Exception as exc:
            return error(f"no se pudo registrar la decisión: {exc}")

    @tool(
        "registrar_acuerdo",
        "Registra un acuerdo accionable. Un acuerdo SIEMPRE lleva responsable y, "
        "salvo imposibilidad real, fecha límite y métrica de verificación. Si la "
        "junta no definió responsable o fecha, no inventes: regístralo como dato "
        "faltante con `registrar_dato_faltante`.",
        {
            "type": "object",
            "properties": {
                "acuerdo": {"type": "string", "description": "Qué se va a hacer."},
                "responsable": {"type": "string", "description": "Quién lo hace."},
                "fecha_limite": {
                    "type": "string",
                    "description": "Fecha límite en formato AAAA-MM-DD.",
                },
                "metrica": {
                    "type": "string",
                    "description": "Cómo se verificará que se cumplió.",
                },
                "decision_id": {
                    "type": "string",
                    "description": "Id de la decisión de la que se desprende, si aplica.",
                },
            },
            "required": ["acuerdo", "responsable"],
            "additionalProperties": False,
        },
    )
    async def registrar_acuerdo(args: dict[str, Any]) -> dict[str, Any]:
        try:
            fila = repo.registrar_acuerdo(
                acuerdo=args["acuerdo"],
                responsable=args["responsable"],
                fecha_limite=args.get("fecha_limite"),
                metrica=args.get("metrica"),
                decision_id=args.get("decision_id"),
                sesion_id=estado["sesion_id"],
            )
            return texto(f"Acuerdo registrado con id {fila['id']}.")
        except Exception as exc:
            return error(f"no se pudo registrar el acuerdo: {exc}")

    @tool(
        "actualizar_acuerdo",
        "Cambia el estado de un acuerdo existente (por ejemplo, marcarlo cumplido).",
        {
            "type": "object",
            "properties": {
                "acuerdo_id": {"type": "string"},
                "estado": {
                    "type": "string",
                    "enum": ["abierto", "en_progreso", "cumplido", "cancelado"],
                },
            },
            "required": ["acuerdo_id", "estado"],
            "additionalProperties": False,
        },
    )
    async def actualizar_acuerdo(args: dict[str, Any]) -> dict[str, Any]:
        try:
            fila = repo.actualizar_acuerdo(args["acuerdo_id"], args["estado"])
            if not fila:
                return error(f"no existe un acuerdo con id {args['acuerdo_id']}.")
            return texto(f"Acuerdo {args['acuerdo_id']} → estado '{args['estado']}'.")
        except Exception as exc:
            return error(f"no se pudo actualizar el acuerdo: {exc}")

    @tool(
        "registrar_kpi",
        "Guarda el valor de un KPI para un período, construyendo la serie histórica "
        "del negocio. Si ya existe ese KPI para ese período, lo actualiza. Registra "
        "SIEMPRE la fuente del dato.",
        {
            "type": "object",
            "properties": {
                "periodo": {
                    "type": "string",
                    "description": "Período en formato AAAA-MM-DD (usa el día 1 del mes).",
                },
                "nombre": {
                    "type": "string",
                    "description": "Nombre del KPI, estable en el tiempo. "
                    "Ej: 'ingreso_mensual_cop', 'tasa_conversion_pct', 'ssi_linkedin'.",
                },
                "valor": {"type": "number"},
                "unidad": {"type": "string", "description": "COP, %, días, unidades..."},
                "fuente": {
                    "type": "string",
                    "description": "De dónde salió: Airtable, cálculo del CFO, dato del usuario...",
                },
                "nota": {"type": "string"},
            },
            "required": ["periodo", "nombre", "valor"],
            "additionalProperties": False,
        },
    )
    async def registrar_kpi(args: dict[str, Any]) -> dict[str, Any]:
        try:
            repo.registrar_kpi(
                periodo=args["periodo"],
                nombre=args["nombre"],
                valor=float(args["valor"]),
                unidad=args.get("unidad"),
                fuente=args.get("fuente"),
                nota=args.get("nota"),
            )
            return texto(
                f"KPI '{args['nombre']}' = {args['valor']} guardado para {args['periodo']}."
            )
        except Exception as exc:
            return error(f"no se pudo registrar el KPI: {exc}")

    @tool(
        "registrar_dato_faltante",
        "Deja constancia de un dato del negocio que la junta necesitó y no tenía. "
        "Es la vía correcta cuando falta información: registrarla, no suponerla.",
        {
            "type": "object",
            "properties": {
                "dato": {"type": "string", "description": "Qué dato falta."},
                "para_que": {
                    "type": "string",
                    "description": "Qué decisión mejoraría si se tuviera.",
                },
            },
            "required": ["dato"],
            "additionalProperties": False,
        },
    )
    async def registrar_dato_faltante(args: dict[str, Any]) -> dict[str, Any]:
        try:
            repo.registrar_dato_faltante(
                dato=args["dato"],
                para_que=args.get("para_que"),
                sesion_id=estado["sesion_id"],
            )
            return texto("Dato faltante registrado.")
        except Exception as exc:
            return error(f"no se pudo registrar el dato faltante: {exc}")

    servidor = create_sdk_mcp_server(
        name="memoria",
        version="1.0.0",
        tools=[
            informe_apertura,
            buscar_decisiones,
            listar_acuerdos,
            consultar_kpis,
            listar_datos_faltantes,
            registrar_decision,
            registrar_acuerdo,
            actualizar_acuerdo,
            registrar_kpi,
            registrar_dato_faltante,
        ],
    )
    # La junta necesita poder fijar el id de sesión una vez el SDK lo asigna.
    return servidor, fijar_sesion
