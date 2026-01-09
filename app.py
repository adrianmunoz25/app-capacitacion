import streamlit as st
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials # <--- Librería Moderna
from datetime import datetime

# --- CONFIGURACIÓN ---
NOMBRE_SHEET = "Resultados Capacitacion" 

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

# --- SECCIÓN 1: LOS 3 PILARES ---
st.markdown("---")
st.subheader("1. Experiencia de Servicio")

col1, col2 = st.columns(2)
with col1:
    st.write("**📡 Comunicación y Cercanía**")
    st.caption("¿Hubo errores? ¿Sentiste apoyo y claridad en las dudas?")
    pilar_comunicacion = st.slider("Comunicación", 1, 5, 3, label_visibility="collapsed", key="com")

with col2:
    st.write("**⚡ Gestión y Rapidez**")
    st.caption("Visibilidad del estatus, seguimiento y tiempos de respuesta.")
    pilar_gestion = st.slider("Gestión", 1, 5, 3, label_visibility="collapsed", key="ges")

st.write("**🛠️ Proceso y Calidad**")
st.caption("Claridad del proceso de trabajo y calidad del material final.")
pilar_calidad = st.slider("Calidad", 1, 5, 3, label_visibility="collapsed", key="cal")

promedio = (pilar_comunicacion + pilar_gestion + pilar_calidad) / 3

# --- SECCIÓN 2: FEEDBACK INTELIGENTE ---
st.markdown("---")
st.subheader("2. Comentarios Finales")

pregunta_dinamica = ""
if promedio <= 3:
    st.warning("Notamos que hubo fricción en el proceso.")
    pregunta_dinamica = "¿Qué obstáculo específico debemos eliminar?"
elif promedio < 5:
    st.info("Gracias por tu evaluación.")
    pregunta_dinamica = "¿Qué detalle nos faltó para el 10?"
else:
    st.success("¡Nos alegra haber superado expectativas!")
    st.balloons()
    pregunta_dinamica = "¿Qué fortaleza deberíamos mantener?"

comentario = st.text_area(pregunta_dinamica)

# --- BOTÓN DE ENVÍO ---
if st.button("Enviar Evaluación 🚀", type="primary"):
    with st.spinner("Guardando respuestas..."):
        
        # 1. ANÁLISIS DE IA (INTENTO)
        analisis_ia = "Sin análisis (Error IA)"
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=api_key)
            
            # Selector automático de modelo
            modelo_a_usar = "models/gemini-1.5-flash"
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name:
                        modelo_a_usar = m.name
                        break
            except: pass

            model = genai.GenerativeModel(modelo_a_usar)
            prompt = f"Resume este feedback en 5 palabras. Comentario: {comentario}"
            
            if comentario:
                response = model.generate_content(prompt)
                analisis_ia = response.text
            else:
                analisis_ia = "Sin comentario escrito"
                
        except Exception as e:
            # Si falla la IA, no detenemos la app, solo avisamos
            print(f"Error IA: {e}")
            analisis_ia = "Error conectando con IA"

        # 2. GUARDAR EN GOOGLE SHEETS (CONEXIÓN MODERNA)
        try:
            # Definimos el alcance correcto
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            
            # Usamos la librería nueva 'google-auth'
            credentials = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=scopes
            )
            
            client = gspread.authorize(credentials)
            sheet = client.open(NOMBRE_SHEET).sheet1
            
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([
                fecha, pilar_comunicacion, pilar_gestion, pilar_calidad, 
                round(promedio, 2), comentario, analisis_ia
            ])
            
            st.toast("¡Guardado exitosamente!", icon="✅")
            st.success("Gracias, tu opinión ha sido registrada.")
            
        except Exception as e:
            st.error("⚠️ Error al guardar en Excel.")
            st.write("Detalle del error técnico:")
            st.code(e)
