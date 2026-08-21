"""
Encuesta NPS interactiva — IAM(TM) Intelligence / Comfacesar
Autora: Sandra Curvelo — Founder & CSO, IAM(TM) LATAM

Ejecutar en local:
    pip install streamlit pandas
    streamlit run nps_comfacesar/app_nps.py

Panel de resultados: agregar ?admin=1 a la URL e ingresar la clave.
"""

import csv
import os
from datetime import datetime

import pandas as pd
import streamlit as st

# --- Identidad IAM ---
ROJO = "#C00000"
NEGRO = "#0B0C0F"
GRIS = "#1A1C23"
BLANCO = "#FAFAFA"

RUTA_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "respuestas_nps.csv")
COLUMNAS = [
    "timestamp", "nps", "metodologia", "aplicacion",
    "ritmo", "nivel", "confianza_antes", "confianza_hoy", "necesidad",
]

st.set_page_config(page_title="Pulso IAM™ Intelligence · Comfacesar", page_icon="🔴", layout="centered")

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');
html, body, [class*="css"] {{ font-family: 'Montserrat', sans-serif; }}
.stButton > button {{
    border-radius: 6px; height: 3em; width: 100%; font-weight: 600;
    background: {ROJO}; color: {BLANCO}; border: none;
}}
.stButton > button:hover {{ background: #9E0000; color: {BLANCO}; }}
.iam-kicker {{ color: {ROJO}; font-weight: 800; letter-spacing: .18em; font-size: .78em; }}
.iam-quote {{ border-left: 5px solid {ROJO}; padding-left: 18px; margin: 18px 0; font-style: italic; opacity: .9; }}
.iam-progress {{ font-size: .82em; opacity: .65; margin-bottom: .4em; }}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------- almacenamiento
def guardar(respuesta: dict) -> None:
    nuevo = not os.path.exists(RUTA_CSV)
    with open(RUTA_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNAS)
        if nuevo:
            w.writeheader()
        w.writerow(respuesta)


def leer() -> pd.DataFrame:
    if not os.path.exists(RUTA_CSV):
        return pd.DataFrame(columns=COLUMNAS)
    return pd.read_csv(RUTA_CSV)


def calcular_nps(notas) -> dict:
    notas = [int(n) for n in notas]
    total = len(notas)
    if total == 0:
        return {"nps": None, "promotores": 0, "pasivos": 0, "detractores": 0, "total": 0}
    promotores = sum(1 for n in notas if n >= 9)
    pasivos = sum(1 for n in notas if 7 <= n <= 8)
    detractores = sum(1 for n in notas if n <= 6)
    nps = round((promotores / total) * 100 - (detractores / total) * 100)
    return {"nps": nps, "promotores": promotores, "pasivos": pasivos,
            "detractores": detractores, "total": total}


def lectura_nps(valor: int) -> str:
    if valor > 50:
        return "Excelente — el grupo es embajador del programa."
    if valor >= 20:
        return "Bueno — hay base sólida, con margen para convertir pasivos en promotores."
    if valor >= 0:
        return "A mejorar — revisar ritmo, nivel y acompañamiento antes de la siguiente sesión."
    return "Alerta — conversación 1:1 con los detractores esta misma semana."


# ---------------------------------------------------------------- panel admin
def panel_admin() -> None:
    st.markdown('<p class="iam-kicker">IAM™ INTELLIGENCE · PANEL DE RESULTADOS</p>', unsafe_allow_html=True)
    st.title("Pulso Comfacesar — Comunicaciones")

    clave_real = st.secrets.get("admin_key", "IAM2026") if hasattr(st, "secrets") else "IAM2026"
    if st.text_input("Clave de acceso", type="password") != clave_real:
        st.info("Ingresa la clave para ver los resultados.")
        return

    df = leer()
    if df.empty:
        st.warning("Todavía no hay respuestas registradas.")
        return

    r = calcular_nps(df["nps"].tolist())
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("NPS", r["nps"])
    c2.metric("Promotores", r["promotores"])
    c3.metric("Pasivos", r["pasivos"])
    c4.metric("Detractores", r["detractores"])
    st.caption(f"{r['total']} respuestas · {lectura_nps(r['nps'])}")

    st.divider()
    a = df["confianza_antes"].mean()
    h = df["confianza_hoy"].mean()
    c1, c2, c3 = st.columns(3)
    c1.metric("Confianza en IA — antes", f"{a:.1f}")
    c2.metric("Confianza en IA — hoy", f"{h:.1f}", f"{h - a:+.1f}")
    c3.metric("Metodología", f"{df['metodologia'].mean():.1f} / 5")

    st.divider()
    st.subheader("Distribución de notas NPS")
    st.bar_chart(df["nps"].value_counts().reindex(range(11), fill_value=0))

    st.subheader("Ritmo y nivel")
    c1, c2 = st.columns(2)
    c1.write(df["ritmo"].value_counts())
    c2.write(df["nivel"].value_counts())

    st.subheader("Qué están aplicando")
    for texto in df["aplicacion"].dropna():
        if str(texto).strip():
            st.markdown(f"> {texto}")

    st.subheader("Qué necesitan del programa")
    for texto in df["necesidad"].dropna():
        if str(texto).strip():
            st.markdown(f"> {texto}")

    st.divider()
    st.download_button("Descargar respuestas (CSV)", df.to_csv(index=False).encode("utf-8"),
                       "respuestas_nps_comfacesar.csv", "text/csv")


# ---------------------------------------------------------------- encuesta
def encuesta() -> None:
    if "paso" not in st.session_state:
        st.session_state.paso = 0
        st.session_state.datos = {}

    paso = st.session_state.paso
    total_pasos = 6

    if paso == 0:
        st.markdown('<p class="iam-kicker">IAM™ INTELLIGENCE · COMFACESAR</p>', unsafe_allow_html=True)
        st.title("Pulso del programa")
        st.write("Dos sesiones hechas, dos meses por delante. Tomo el pulso **ahora**, "
                 "cuando todavía se puede ajustar — no al final, cuando ya solo sirve para el informe.")
        st.markdown('<div class="iam-quote">"Lo que no se mide, no se puede mejorar. '
                    'Y esto lo estamos midiendo juntos."<br>— Sandra Curvelo</div>', unsafe_allow_html=True)
        st.caption("6 preguntas · 2 minutos · respuestas anónimas")
        if st.button("Empezar"):
            st.session_state.paso = 1
            st.rerun()
        return

    if 1 <= paso <= total_pasos:
        st.markdown(f'<p class="iam-progress">Pregunta {paso} de {total_pasos}</p>', unsafe_allow_html=True)
        st.progress(paso / total_pasos)

    if paso == 1:
        st.subheader("¿Qué tan probable es que lo recomiendes?")
        st.write("En una escala de **0 a 10**, ¿qué tan probable es que recomiendes IAM™ Intelligence "
                 "a un colega de otra área de Comfacesar?")
        nota = st.slider("0 = nada probable · 10 = totalmente probable", 0, 10, 8)
        if st.button("Siguiente"):
            st.session_state.datos["nps"] = nota
            st.session_state.paso = 2
            st.rerun()

    elif paso == 2:
        st.subheader("La metodología")
        st.write("La metodología del programa — **sesiones en vivo + ejercicios prácticos + "
                 "documentación y actas en Slack** — me resulta clara y fácil de seguir.")
        valor = st.radio("Tu valoración", [1, 2, 3, 4, 5], index=3, horizontal=True,
                         format_func=lambda x: {1: "1 · Nada", 2: "2", 3: "3", 4: "4", 5: "5 · Total"}[x])
        if st.button("Siguiente"):
            st.session_state.datos["metodologia"] = valor
            st.session_state.paso = 3
            st.rerun()

    elif paso == 3:
        st.subheader("Lo que ya estás aplicando")
        st.write("De lo visto en las sesiones 1 y 2, ¿qué ya aplicaste — o vas a aplicar **esta semana** — "
                 "en tu trabajo de comunicaciones?")
        texto = st.text_area("Sé concreto/a: esta es la respuesta que más sirve.", height=130)
        if st.button("Siguiente"):
            st.session_state.datos["aplicacion"] = texto.strip()
            st.session_state.paso = 4
            st.rerun()

    elif paso == 4:
        st.subheader("Ritmo y nivel")
        ritmo = st.radio("¿Cómo sientes el ritmo del programa?",
                         ["Muy lento", "Adecuado", "Muy rápido"], index=1)
        nivel = st.radio("¿Y el nivel de profundidad técnica?",
                         ["Muy básico", "En el punto", "Muy avanzado"], index=1)
        if st.button("Siguiente"):
            st.session_state.datos["ritmo"] = ritmo
            st.session_state.datos["nivel"] = nivel
            st.session_state.paso = 5
            st.rerun()

    elif paso == 5:
        st.subheader("Tu confianza usando IA")
        st.write("Aquí medimos el avance real del programa.")
        antes = st.slider("Antes de empezar el programa", 0, 10, 4)
        hoy = st.slider("Hoy", 0, 10, 7)
        if st.button("Siguiente"):
            st.session_state.datos["confianza_antes"] = antes
            st.session_state.datos["confianza_hoy"] = hoy
            st.session_state.paso = 6
            st.rerun()

    elif paso == 6:
        st.subheader("Qué necesitas")
        st.write("¿Qué necesitas de mí o del programa para que las próximas sesiones "
                 "te generen aún más valor?")
        texto = st.text_area("Con total confianza — esto es anónimo.", height=130)
        if st.button("Enviar mis respuestas"):
            st.session_state.datos["necesidad"] = texto.strip()
            st.session_state.datos["timestamp"] = datetime.now().isoformat(timespec="seconds")
            guardar({c: st.session_state.datos.get(c, "") for c in COLUMNAS})
            st.session_state.paso = 7
            st.rerun()

    elif paso == 7:
        st.balloons()
        st.success("¡Listo! Tus respuestas quedaron registradas.")
        delta = st.session_state.datos["confianza_hoy"] - st.session_state.datos["confianza_antes"]
        if delta > 0:
            st.write(f"Tu confianza usando IA subió **{delta} puntos** desde que empezamos. "
                     "Eso es exactamente lo que venimos a construir.")
        st.markdown('<div class="iam-quote">"Los resultados del grupo — y los ajustes que voy a hacer — '
                    'los comparto en el canal el lunes."<br>— Sandra Curvelo</div>', unsafe_allow_html=True)
        st.caption("IAM™ Intelligence · Comfacesar · agosto–octubre 2026")


# ---------------------------------------------------------------- router
if st.query_params.get("admin") == "1":
    panel_admin()
else:
    encuesta()
