# COPIA Y PEGA ESTE CÓDIGO COMPLETO EN app.py

import streamlit as st
import time

# --- Configuración de la Página ---
# Usaremos el logo como ícono de la pestaña. Asegúrate de que tu logo se llame 'logo.png'
st.set_page_config(
    page_title="Sales Revolution AI: El Desafío",
    page_icon="logo.png", 
    layout="centered"
)

# --- Código CSS para personalización avanzada ---
st.markdown("""
<style>
/* Importar fuente desde Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&display=swap');

/* Aplicar la fuente a toda la app */
html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif;
}

/* Estilo para los botones principales, usando tu color rojo */
.stButton > button {
    border-radius: 5px;
    height: 3em;
    width: 100%;
    font-weight: 600; /* Letra un poco más gruesa */
}
</style>
""", unsafe_allow_html=True)

# --- Mostramos el logo en la parte superior de la app ---
st.image("logo.png", width=200)

# --- Lógica del Juego ---
def mentor_quote(quote):
    st.markdown(f"""
    <div style="border-left: 5px solid #E50914; padding-left: 20px; margin: 20px 0; font-style: italic; color: #E5E5E5;">
        <p style="font-size: 1.1em;">MENTORA SANDRA CURVELO DICE:</p>
        <p>"{quote}"</p>
    </div>
    """, unsafe_allow_html=True)

if 'stage' not in st.session_state:
    st.session_state.stage = 'intro'
    st.session_state.score = 0
    st.session_state.feedback = ""

if st.session_state.stage == 'intro':
    st.title("🚀 Sales Revolution AI: El Desafío")
    st.write("Bienvenido/a al mundo de las ventas B2B de alto impacto. Estás a punto de cerrar el trimestre y tienes una meta ambiciosa. El mercado es competitivo, pero tienes un as bajo la manga: la Inteligencia Artificial.")
    mentor_quote("Como siempre digo, lo que no se mide, no se puede mejorar. Hoy, vamos a demostrar que la IA no es una amenaza, es el copiloto más potente que puedes tener. ¿Listo/a para redefinir el juego?")
    if st.button("Comenzar mi Jornada"):
        st.session_state.stage = 'prospecting'
        st.experimental_rerun()

elif st.session_state.stage == 'prospecting':
    st.header("--- ETAPA 1: PROSPECCIÓN INTELIGENTE ---")
    st.write("Tu pipeline necesita leads de calidad, ¡y rápido! Necesitas encontrar prospectos que encajen perfectamente con tu Perfil de Cliente Ideal (ICP).")
    mentor_quote("La IA analiza miles de datos para identificar prospectos entendiendo el timing, las necesidades y las señales de compra. Es como un GPS que nos guía por el camino más corto.")
    st.write("**¿Cómo encuentras a los tomadores de decisión?**")
    if st.button("Buscar manualmente en LinkedIn y directorios"):
        st.session_state.feedback = "Has pasado dos días buscando y solo has encontrado 10 contactos. El tiempo es oro y lo estás perdiendo en tareas manuales."
        st.session_state.stage = 'qualification'
        st.experimental_rerun()
    if st.button("Usar una herramienta de IA como Lusha o Apollo.io"):
        st.session_state.score = 1
        st.session_state.feedback = "¡DECISIÓN CORRECTA! Has utilizado Lusha para obtener datos de 50 tomadores de decisión en menos de una hora."
        st.session_state.stage = 'qualification'
        st.experimental_rerun()
    if st.button("Comprar una base de datos genérica"):
        st.session_state.feedback = "La base de datos está desactualizada. Muchos correos rebotan y has gastado presupuesto en información de baja calidad."
        st.session_state.stage = 'qualification'
        st.experimental_rerun()
        
elif st.session_state.stage == 'qualification':
    st.info(f"Feedback Etapa 1: {st.session_state.feedback}")
    st.header("--- ETAPA 2: CUALIFICACIÓN DE LEADS ---")
    st.write("Ahora tienes 100 leads nuevos. Pero... ¿cuáles están realmente listos para comprar? Tu tiempo es limitado.")
    mentor_quote("¡Se acabaron las corazonadas! Los modelos de IA asignan una puntuación a cada lead basándose en su probabilidad real de conversión.")
    st.write("**¿Cómo priorizas tus esfuerzos?**")
    if st.button("Llamar a los leads en orden alfabético"):
        st.session_state.feedback = "Has perdido la mañana hablando con leads que solo estaban curioseando."
        st.session_state.stage = 'personalization'
        st.experimental_rerun()
    if st.button("Utilizar la IA de tu CRM para un 'Lead Score'"):
        st.session_state.score += 1
        st.session_state.feedback = "¡EXCELENTE ESTRATEGIA! La IA te presenta un ranking y te enfocas en el Top 20. Estás trabajando de forma inteligente."
        st.session_state.stage = 'personalization'
        st.experimental_rerun()
    if st.button("Revisar manualmente el historial de cada lead"):
        st.session_state.feedback = "Te toma un día entero. Mientras lo hacías, el lead más 'caliente' agendó una reunión con tu competencia."
        st.session_state.stage = 'personalization'
        st.experimental_rerun()

elif st.session_state.stage == 'personalization':
    st.info(f"Feedback Etapa 2: {st.session_state.feedback}")
    st.header("--- ETAPA 3: PERSONALIZACIÓN A ESCALA ---")
    st.write("Estás a punto de enviar un correo clave a la CEO de una empresa objetivo. Un mensaje genérico será ignorado.")
    mentor_quote("La IA te ayuda a romper las barreras del 'No' antes de que aparezcan. Es como tener un asesor de Chris Voss susurrándote al oído.")
    st.write("**¿Cómo preparas tu comunicación?**")
    if st.button("Usar un asistente de redacción (IA) para analizar su perfil"):
        st.session_state.score += 1
        st.session_state.feedback = "¡JUGADA MAESTRA! En segundos, la IA te sugiere un ángulo hiper-relevante. Recibes una respuesta en menos de una hora."
        st.session_state.stage = 'conclusion'
        st.experimental_rerun()
    if st.button("Pasar horas investigando manualmente sus publicaciones"):
        st.session_state.feedback = "Encuentras un buen ángulo, pero tardas tanto que otro vendedor, armado con IA, ya ha iniciado la conversación."
        st.session_state.stage = 'conclusion'
        st.experimental_rerun()
    if st.button("Usar la misma plantilla de correo de siempre"):
        st.session_state.feedback = "Tu correo es eliminado sin ser leído. Parecía spam. Perdiste una gran oportunidad."
        st.session_state.stage = 'conclusion'
        st.experimental_rerun()

elif st.session_state.stage == 'conclusion':
    st.info(f"Feedback Etapa 3: {st.session_state.feedback}")
    st.header("--- FIN DEL DESAFÍO: ANÁLISIS DE RESULTADOS ---")
    mentor_quote("Recuerda: los números no mienten. Analicemos tu desempeño.")
    score = st.session_state.score
    if score == 3:
        st.success(f"¡FELICIDADES, CAMPEÓN/A DE VENTAS! (Puntaje: {score}/3)")
        st.write("Has dominado cada etapa utilizando la IA de forma estratégica. Has demostrado que el futuro de las ventas ya está aquí, y es inteligente.")
    elif score >= 1:
        st.warning(f"NO ESTÁ MAL (Puntaje: {score}/3)")
        st.write("Has comenzado a integrar la IA, pero aún hay margen de mejora. Sigue aprendiendo y no tengas miedo de apoyarte más en la tecnología.")
    else:
        st.error(f"OPORTUNIDAD DE MEJORA (Puntaje: {score}/3)")
        st.write("Parece que los métodos antiguos te frenaron. Este no es un fracaso, es un diagnóstico. Ahora sabes qué necesitas mejorar.")
    if st.button("Jugar de Nuevo"):
        st.session_state.clear()
        st.experimental_rerun()
