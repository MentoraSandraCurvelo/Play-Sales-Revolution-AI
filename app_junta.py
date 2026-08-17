"""Interfaz de la Junta Directiva Agéntica IAM™.

    streamlit run app_junta.py
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import streamlit as st

from junta.config import cargar_settings
from junta.junta import EventoJunta, JuntaDirectiva

ROJO = "#C00000"
RAIZ = Path(__file__).resolve().parent
LOGO = RAIZ / "logo.png"

st.set_page_config(
    page_title="Junta Directiva IAM™",
    page_icon=str(LOGO) if LOGO.exists() else "⭕",
    layout="wide",
)

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
html, body, [class*="css"] {{ font-family: 'Montserrat', sans-serif; }}
.stButton > button {{ border-radius: 4px; font-weight: 600; }}
.iam-titulo {{
    font-weight: 700; font-size: 1.9rem; letter-spacing: -0.02em; margin: 0;
}}
.iam-sub {{ color: #8a8a8a; font-size: 0.9rem; margin-top: .15rem; }}
.iam-regla {{ border: none; border-top: 3px solid {ROJO}; margin: .8rem 0 1.4rem 0; }}
.iam-consejero {{
    display: inline-block; background: {ROJO}; color: #fff; padding: 2px 10px;
    border-radius: 3px; font-size: .74rem; font-weight: 600; letter-spacing: .04em;
    text-transform: uppercase;
}}
.iam-chip {{
    display: inline-block; border: 1px solid #d0d0d0; border-radius: 3px;
    padding: 1px 8px; margin: 2px 3px 2px 0; font-size: .74rem; color: #555;
}}
.iam-chip-on {{ border-color: {ROJO}; color: {ROJO}; font-weight: 600; }}
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Estado
# ---------------------------------------------------------------------------
def _init_estado() -> None:
    st.session_state.setdefault("historial", [])
    st.session_state.setdefault("sdk_session_id", None)
    st.session_state.setdefault("sesion_memoria_id", None)
    st.session_state.setdefault("modo_ejecucion", False)


_init_estado()


@st.cache_resource(show_spinner=False)
def _diagnostico(modo_ejecucion: bool) -> dict:
    """Diagnóstico de configuración. Cacheado: no depende de la conversación."""
    settings = cargar_settings(modo_lectura=not modo_ejecucion)
    return JuntaDirectiva(settings).diagnostico()


def _cerrar_sesion_memoria(sesion_id: str | None) -> None:
    """Marca en Supabase que la sesión terminó, al empezar una nueva."""
    if not sesion_id:
        return
    try:
        junta = JuntaDirectiva(cargar_settings(), sesion_memoria_id=sesion_id)
        junta.cerrar_sesion_memoria()
    except Exception:
        pass  # cerrar el registro nunca debe impedir empezar una sesión nueva


# ---------------------------------------------------------------------------
# Deliberación
# ---------------------------------------------------------------------------
async def _deliberar(asunto: str, contenedor) -> tuple[str, str | None, str | None]:
    """Ejecuta una deliberación pintando los eventos a medida que llegan."""
    settings = cargar_settings(modo_lectura=not st.session_state.modo_ejecucion)
    junta = JuntaDirectiva(
        settings,
        reanudar=st.session_state.sdk_session_id,
        sesion_memoria_id=st.session_state.sesion_memoria_id,
    )

    proceso = contenedor.status("La junta está deliberando…", expanded=True)
    hueco_texto = contenedor.empty()
    partes: list[str] = []
    convocados: list[str] = []

    async with junta:
        async for evento in junta.deliberar(asunto):
            _pintar_evento(evento, proceso, hueco_texto, partes, convocados)

    proceso.update(
        label=(
            f"Deliberación terminada · {len(convocados)} consejero(s) convocado(s)"
            if convocados
            else "Deliberación terminada"
        ),
        state="complete",
        expanded=False,
    )
    return "".join(partes), junta.sdk_session_id, junta.sesion_memoria_id


def _pintar_evento(
    evento: EventoJunta,
    proceso,
    hueco_texto,
    partes: list[str],
    convocados: list[str],
) -> None:
    if evento.tipo == "sistema":
        proceso.warning(evento.contenido)

    elif evento.tipo == "convocatoria":
        if evento.consejero:
            convocados.append(evento.consejero)
        proceso.markdown(
            f'<span class="iam-consejero">{evento.consejero}</span>',
            unsafe_allow_html=True,
        )
        if evento.datos and evento.datos.get("encargo"):
            proceso.caption(evento.datos["encargo"])

    elif evento.tipo == "herramienta":
        proceso.caption(f"↳ {evento.contenido}")

    elif evento.tipo == "pensamiento":
        proceso.caption(f"… {evento.contenido[:220]}")

    elif evento.tipo == "texto":
        partes.append(evento.contenido)
        hueco_texto.markdown("".join(partes))


# ---------------------------------------------------------------------------
# Barra lateral
# ---------------------------------------------------------------------------
with st.sidebar:
    if LOGO.exists():
        st.image(str(LOGO), width=140)
    st.markdown("### Estado de la junta")

    diag = _diagnostico(st.session_state.modo_ejecucion)

    st.markdown("**Consejeros**")
    st.markdown(
        " ".join(f'<span class="iam-chip iam-chip-on">{c}</span>' for c in diag["consejeros"]),
        unsafe_allow_html=True,
    )

    st.markdown("**Conectores**")
    todos = ["airtable", "notion", "google", "whatsapp", "meta", "memoria"]
    activos = set(diag["conectores_activos"])
    st.markdown(
        " ".join(
            f'<span class="iam-chip{" iam-chip-on" if c in activos else ""}">{c}</span>'
            for c in todos
        ),
        unsafe_allow_html=True,
    )

    if diag["conectores_faltantes"]:
        with st.expander(f"Sin configurar ({len(diag['conectores_faltantes'])})"):
            for nombre, variables in diag["conectores_faltantes"].items():
                st.caption(f"**{nombre}** → falta `{variables}`")

    st.divider()

    st.markdown("**Contexto de negocio**")
    st.caption(diag["contexto"])
    if diag["datos_faltantes"]:
        with st.expander(f"Datos por completar ({len(diag['datos_faltantes'])})"):
            for dato in diag["datos_faltantes"]:
                st.caption(f"· {dato}")

    st.divider()

    modo = st.toggle(
        "Modo ejecución",
        value=st.session_state.modo_ejecucion,
        help=(
            "Desactivado, la junta solo lee y recomienda. Activado, puede enviar "
            "WhatsApp y correos, y publicar en Meta."
        ),
    )
    if modo != st.session_state.modo_ejecucion:
        st.session_state.modo_ejecucion = modo
        _diagnostico.clear()
        st.rerun()

    if st.session_state.modo_ejecucion:
        st.error("La junta puede ejecutar acciones hacia el exterior.", icon="⚠️")

    if not diag["memoria"]:
        st.warning("Sin memoria: cada sesión empieza de cero.", icon="⚠️")

    st.divider()
    if st.button("Nueva sesión", use_container_width=True):
        _cerrar_sesion_memoria(st.session_state.sesion_memoria_id)
        st.session_state.historial = []
        st.session_state.sdk_session_id = None
        st.session_state.sesion_memoria_id = None
        st.rerun()


# ---------------------------------------------------------------------------
# Cabecera
# ---------------------------------------------------------------------------
st.markdown('<p class="iam-titulo">⭕ Junta Directiva IAM™</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="iam-sub">Ocho consejeros especializados deliberan sobre tu negocio '
    "con tus datos reales.</p>",
    unsafe_allow_html=True,
)
st.markdown('<hr class="iam-regla">', unsafe_allow_html=True)

if diag["contexto"].startswith("0 "):
    st.error(
        "La carpeta `contexto/` está vacía. La junta no conoce el negocio y sus "
        "respuestas serán genéricas. Completa los archivos de contexto primero."
    )

# ---------------------------------------------------------------------------
# Sugerencias de arranque
# ---------------------------------------------------------------------------
if not st.session_state.historial:
    st.markdown("**Asuntos para llevar a la junta**")
    sugerencias = [
        "Revisemos el pipeline y dime a quién debo hacer seguimiento esta semana.",
        "¿Debería subir el precio del programa de Social Selling? Analízalo a fondo.",
        "Arma el tablero de KPIs de este mes con lo que haya disponible.",
        "Tengo tiempo para un solo pilar el próximo trimestre. ¿Cuál y por qué?",
    ]
    columnas = st.columns(2)
    for i, sugerencia in enumerate(sugerencias):
        if columnas[i % 2].button(sugerencia, use_container_width=True, key=f"sug{i}"):
            st.session_state.pendiente = sugerencia
            st.rerun()

# ---------------------------------------------------------------------------
# Historial
# ---------------------------------------------------------------------------
for turno in st.session_state.historial:
    with st.chat_message(turno["rol"], avatar="⭕" if turno["rol"] == "assistant" else None):
        st.markdown(turno["contenido"])

# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------
asunto = st.chat_input("¿Qué asunto lleva a la junta?")
if not asunto and "pendiente" in st.session_state:
    asunto = st.session_state.pop("pendiente")

if asunto:
    st.session_state.historial.append({"rol": "user", "contenido": asunto})
    with st.chat_message("user"):
        st.markdown(asunto)

    with st.chat_message("assistant", avatar="⭕"):
        contenedor = st.container()
        try:
            respuesta, sdk_id, memoria_id = asyncio.run(_deliberar(asunto, contenedor))
        except Exception as exc:
            respuesta = ""
            sdk_id = memoria_id = None
            st.error(f"La deliberación falló: {exc}")

    if respuesta:
        st.session_state.historial.append({"rol": "assistant", "contenido": respuesta})
        st.session_state.sdk_session_id = sdk_id or st.session_state.sdk_session_id
        st.session_state.sesion_memoria_id = (
            memoria_id or st.session_state.sesion_memoria_id
        )
        st.rerun()
