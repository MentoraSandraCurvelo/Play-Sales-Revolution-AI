"""MATIA: demo para clase. CRM simulado tipo Pipedrive + 10 toques de valor diarios (envío de mentira)."""

import sys
from datetime import date, timedelta
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from matia.agente import CORREOS_POR_DIA, ejecutar_dia, puntaje_prioridad, seleccionar_del_dia  # noqa: E402
from matia.contenido import DOLORES, MARCA  # noqa: E402
from matia.crm_simulado import ETAPAS, crear_pipeline  # noqa: E402

st.set_page_config(page_title="MATIA · Agente de Correos", page_icon="logo.png", layout="wide")

ROJO = MARCA["rojo"]
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');
html, body, [class*="css"] {{ font-family: 'Montserrat', sans-serif; }}
.card {{ background:#1a1c23; border-radius:6px; padding:10px 12px; margin-bottom:8px; border-left:3px solid #2a2d36; font-size:13px; }}
.card.demo {{ border-left:3px solid {ROJO}; box-shadow:0 0 0 1px {ROJO}55; }}
.card b {{ color:#FAFAFA; }}
.muted {{ color:#9aa0ad; font-size:12px; }}
.col-head {{ font-weight:800; font-size:13px; letter-spacing:.5px; border-bottom:2px solid {ROJO}; padding-bottom:6px; margin-bottom:10px; }}
.kpi {{ background:#1a1c23; border-radius:6px; padding:14px 16px; }}
.kpi .v {{ font-size:26px; font-weight:800; color:#FAFAFA; }}
.kpi .l {{ font-size:12px; color:#9aa0ad; letter-spacing:.5px; }}
.badge {{ background:{ROJO}; color:#fff; font-size:10px; font-weight:700; padding:2px 6px; border-radius:3px; }}
</style>
""", unsafe_allow_html=True)


def cop(v: int) -> str:
    return "$" + f"{v:,.0f}".replace(",", ".")


# ---------- Estado ----------
ss = st.session_state
if "matia_login" not in ss:
    ss.matia_login = False
    ss.matia_hoy = date.today()
    ss.matia_deals = crear_pipeline(ss.matia_hoy)
    ss.matia_bitacora = []  # lista de jornadas
    ss.matia_ultima = None

# ---------- Login simulado ----------
if not ss.matia_login:
    st.image("logo.png", width=160)
    st.title("Conectar CRM")
    st.caption("Simulación para clase. No se conecta a ningún CRM real y no se guarda ninguna credencial.")
    with st.form("login"):
        st.selectbox("CRM", ["Pipedrive (simulado)"])
        st.text_input("Dominio de la empresa", value="iam-demo.pipedrive.com")
        st.text_input("API token", value="demo-token-0000", type="password")
        if st.form_submit_button("Conectar y sincronizar pipeline"):
            with st.spinner("Sincronizando deals del pipeline..."):
                ss.matia_login = True
            st.rerun()
    st.stop()

deals = ss.matia_deals
hoy = ss.matia_hoy

# ---------- Encabezado ----------
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown(f"## MATIA <span style='color:{ROJO}'>●</span> agente de toques de valor", unsafe_allow_html=True)
    st.caption(f"Conectado a: iam-demo.pipedrive.com (simulado) · Fecha de la simulación: {hoy.isoformat()}")
with c2:
    if st.button("Reiniciar demo"):
        for k in [k for k in ss.keys() if k.startswith("matia_")]:
            del ss[k]
        st.rerun()

total = sum(d.valor_cop for d in deals)
ponderado = sum(d.valor_ponderado for d in deals)
enviados_total = sum(len(j["enviados"]) for j in ss.matia_bitacora)
respuestas = sum(1 for j in ss.matia_bitacora for e in j["enviados"] if e["estado"].startswith("Respondió"))
k = st.columns(4)
for col, (valor, etiqueta) in zip(k, [
    (len(deals), "DEALS ABIERTOS"), (cop(total), "VALOR PIPELINE COP"),
    (cop(ponderado), "VALOR PONDERADO COP"), (f"{enviados_total} / {respuestas}", "CORREOS / RESPUESTAS (SIM.)"),
]):
    col.markdown(f"<div class='kpi'><div class='v'>{valor}</div><div class='l'>{etiqueta}</div></div>", unsafe_allow_html=True)
st.write("")

tab_pipe, tab_demo, tab_matia, tab_log = st.tabs(["Pipeline", "Cliente Demo", "MATIA: jornada de hoy", "Bandeja de enviados"])

# ---------- Pipeline kanban ----------
with tab_pipe:
    cols = st.columns(len(ETAPAS))
    for col, etapa in zip(cols, ETAPAS):
        en_etapa = [d for d in deals if d.etapa == etapa]
        with col:
            st.markdown(f"<div class='col-head'>{etapa.upper()} · {len(en_etapa)}</div>", unsafe_allow_html=True)
            for d in sorted(en_etapa, key=lambda x: (not x.demo, -x.valor_cop)):
                tag = "<span class='badge'>DEMO</span> " if d.demo else ""
                st.markdown(
                    f"<div class='card {'demo' if d.demo else ''}'>{tag}<b>{d.empresa}</b><br>{d.contacto}<br>"
                    f"<span class='muted'>{cop(d.valor_cop)} · {d.dias_sin_toque(hoy)} días sin toque · {d.toques_matia} toques MATIA</span></div>",
                    unsafe_allow_html=True,
                )

# ---------- Ficha del Cliente Demo ----------
with tab_demo:
    demo = next(d for d in deals if d.demo)
    a, b = st.columns([1, 2])
    with a:
        st.markdown(f"### {demo.empresa}")
        st.write(f"**Contacto:** {demo.contacto}, {demo.cargo}")
        st.write(f"**Correo:** {demo.email}")
        st.write(f"**Industria:** {demo.industria} · {demo.ciudad}")
        st.write(f"**Valor:** {cop(demo.valor_cop)} COP")
        st.write(f"**Etapa actual:** {demo.etapa} ({int(demo.probabilidad * 100)}% de probabilidad, supuesto didáctico)")
        st.progress((ETAPAS.index(demo.etapa) + 1) / len(ETAPAS))
        st.write(f"**Dolor principal:** {DOLORES[demo.dolor_principal]['titulo']}")
        st.write(f"**Toques de MATIA:** {demo.toques_matia}")
    with b:
        st.markdown("#### Línea de tiempo (se actualiza cada jornada)")
        for act in reversed(demo.actividades):
            st.markdown(
                f"<div class='card {'demo' if act['tipo'] != 'Nota' else ''}'><b>{act['tipo']}</b> "
                f"<span class='muted'>· {act['fecha']}</span><br>{act['detalle']}</div>",
                unsafe_allow_html=True,
            )

# ---------- Jornada de MATIA ----------
with tab_matia:
    st.markdown(f"MATIA elige **{CORREOS_POR_DIA} deals por día**: el Cliente Demo siempre, y el resto por "
                "prioridad = valor ponderado (millones COP) × días sin toque. Nadie recibe 2 correos en menos de 3 días.")
    cola = seleccionar_del_dia(deals, hoy)
    st.dataframe(
        [{"Empresa": d.empresa, "Contacto": d.contacto, "Etapa": d.etapa, "Días sin toque": d.dias_sin_toque(hoy),
          "Prioridad": round(puntaje_prioridad(d, hoy), 1)} for d in cola],
        use_container_width=True, hide_index=True,
    )
    ya_corrio = any(j["fecha"] == hoy.isoformat() for j in ss.matia_bitacora)
    b1, b2 = st.columns(2)
    with b1:
        if st.button(f"Ejecutar MATIA: enviar {len(cola)} correos (simulado)", type="primary", disabled=ya_corrio):
            with st.spinner("MATIA está redactando y enviando..."):
                ss.matia_ultima = ejecutar_dia(deals, hoy)
                ss.matia_bitacora.append(ss.matia_ultima)
            st.rerun()
    with b2:
        if st.button("Avanzar al día siguiente ⏭"):
            ss.matia_hoy = hoy + timedelta(days=1)
            ss.matia_ultima = None
            st.rerun()
    if ya_corrio:
        st.success("Jornada de hoy completada. Avanza al día siguiente para ver la siguiente tanda.")

    if ss.matia_ultima:
        st.markdown("#### Correos de la jornada")
        for c in ss.matia_ultima["enviados"]:
            with st.expander(f"{c['estado']} · {c['empresa']} · {c['asunto']}"):
                st.caption(f"Para: {c['para']} · Etapa: {c['etapa']} · Dolor foco: {c['dolor_foco']}")
                components.html(c["html"], height=1050, scrolling=True)

# ---------- Bitácora ----------
with tab_log:
    if not ss.matia_bitacora:
        st.info("Todavía no hay envíos. Ejecuta MATIA en la pestaña de la jornada.")
    for j in reversed(ss.matia_bitacora):
        st.markdown(f"**{j['fecha']}** · {len(j['enviados'])} correos")
        st.dataframe(
            [{"Hora": e["hora"], "Para": e["para"], "Empresa": e["empresa"], "Asunto": e["asunto"],
              "Dolor foco": e["dolor_foco"], "Estado": e["estado"]} for e in j["enviados"]],
            use_container_width=True, hide_index=True,
        )
