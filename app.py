import streamlit as st
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- CONFIGURACIÓN ---
# 1. Nombre EXACTO de tu archivo en Google Drive
NOMBRE_SHEET = "Evaluaciones de capacitación" 

# --- INTERFAZ VISUAL ---
st.set_page_config(page_title="Evaluación Capacitación", page_icon="🎓", layout="centered")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stSlider [data-baseweb="slider"] { padding-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 Evaluación de Proyecto")
st.write("¡Hola! Ayúdanos a evaluar la experiencia de creación de este curso.")

# --- GUÍA VISUAL DE LA ESCALA ---
st.info("ℹ️ **Guía de calificación:** \n1️⃣ = **Muy Malo / Deficiente** 😡  \n5️⃣ = **Excelente / Sobresaliente** 🤩")

# --- SECCIÓN 1: EVALUACIÓN (Preguntas Claras) ---
st.markdown("---")
st.subheader("1. Tu Experiencia")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**📡 Comunicación y Apoyo**")
    st.caption("¿Resolvimos tus dudas con claridad y cercanía?")
    pilar_comunicacion = st.slider("Comunicación", 1, 5, 3, format="%d ⭐", label_visibility="collapsed", key="com")
    st.markdown(f"<div style='text-align: center; color: grey;'>Tu calif: {pilar_comunicacion}</div>", unsafe_allow_html=True)

with col2:
    st.markdown("**⚡ Gestión y Tiempos**")
    st.caption("¿Fuimos rápidos y dimos visibilidad del estatus?")
    pilar_gestion = st.slider("Gestión", 1, 5, 3, format="%d ⭐", label_visibility="collapsed", key="ges")
    st.markdown(f"<div style='text-align: center; color: grey;'>Tu calif: {pilar_gestion}</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True) # Espacio
st.markdown("**🛠️ Calidad del Proceso y Entregable**")
st.caption("¿El proceso fue ordenado y el curso final quedó excelente?")
pilar_calidad = st.slider("Calidad", 1, 5, 3, format="%d ⭐", label_visibility="collapsed", key="cal")
st.markdown(f"<div style='text-align: center; color: grey;'>Tu calif: {pilar_calidad}</div>", unsafe_allow_html=True)

promedio = (pilar_comunicacion + pilar_gestion + pilar_calidad) / 3

# --- SECCIÓN 2: FEEDBACK INTELIGENTE ---
st.markdown("---")
st.subheader("2. Comentarios Finales")

pregunta_dinamica = ""
if promedio <= 3:
    st.warning("Lamentamos que la experiencia no fuera ideal.")
    pregunta_dinamica = "Para subir al 5: ¿Qué falló específicamente (tiempos, trato, calidad)?"
elif promedio < 5:
    st.info("¡Gracias! Casi logramos la excelencia.")
    pregunta_dinamica = "¿Qué pequeño detalle nos faltó para obtener un 5 perfecto?"
else:
    st.success("¡Wow! Gracias por la confianza.")
    st.balloons()
    pregunta_dinamica = "¿Qué fue lo que más te gustó para seguir haciéndolo?"

comentario = st.text_area(pregunta_dinamica)

# --- BOTÓN DE ENVÍO ---
if st.button("Enviar Evaluación 🚀", type="primary"):
    with st.spinner("Guardando respuestas..."):
        
        # 1. ANÁLISIS DE IA
        analisis_ia = "Sin análisis"
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=api_key)
            
            # Buscamos modelo disponible
            modelo_a_usar = "models/gemini-1.5-flash"
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name:
                        modelo_a_usar = m.name
                        break
            except: pass

            model = genai.GenerativeModel(modelo_a_usar)
            prompt = f"Resume en 5 palabras este feedback de capacitación: {comentario}"
            
            if comentario:
                response = model.generate_content(prompt)
                analisis_ia = response.text
                
        except Exception as e:
            print(f"IA no disponible: {e}")

        # 2. GUARDAR EN GOOGLE SHEETS
        try:
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            
            credentials = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=scopes
            )
            
            client = gspread.authorize(credentials)
            # AQUI ESTA LA CORRECCION DEL NOMBRE:
            sheet = client.open(NOMBRE_SHEET).sheet1
            
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([
                fecha, pilar_comunicacion, pilar_gestion, pilar_calidad, 
                round(promedio, 2), comentario, analisis_ia
            ])
            
            st.toast("¡Guardado exitosamente!", icon="✅")
            st.success("¡Gracias! Tu opinión ya está en nuestro sistema.")
            
        except Exception as e:
            st.error("⚠️ Error al guardar.")
            st.write("Verifica que el nombre del archivo en Google Drive sea EXACTAMENTE:")
            st.code("Evaluaciones de capacitación")
            st.write("Error técnico:", e)
