import streamlit as st
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
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
    pregunta_dinamica = "Para mejorar: ¿Qué obstáculo específico (tiempos, entendimiento, herramientas) debemos eliminar?"
elif promedio < 5:
    st.info("Gracias por tu evaluación.")
    pregunta_dinamica = "¿Qué detalle nos faltó para que la experiencia fuera perfecta?"
else:
    st.success("¡Nos alegra haber superado expectativas!")
    st.balloons()
    pregunta_dinamica = "¿Qué práctica o fortaleza del equipo deberíamos mantener siempre?"

comentario = st.text_area(pregunta_dinamica)

# --- BOTÓN DE ENVÍO ---
if st.button("Enviar Evaluación 🚀", type="primary"):
    with st.spinner("Procesando tu feedback..."):
        try:
            # 1. CONEXIÓN A LA NUBE
            api_key = st.secrets["GEMINI_API_KEY"]
            creds_dict = st.secrets["gcp_service_account"]
            
            # 2. AUTO-SELECCIÓN DE MODELO (Solución al Error 404)
            genai.configure(api_key=api_key)
            
            # Buscamos qué modelos tienes disponibles
            modelo_a_usar = "models/gemini-1.5-flash" # Opción por defecto
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        if 'gemini' in m.name:
                            modelo_a_usar = m.name
                            break # Usamos el primero que encontremos
            except:
                pass # Si falla el listado, usamos el default

            # st.write(f"Debug: Usando modelo {modelo_a_usar}") # Descomenta si quieres ver cuál eligió
            model = genai.GenerativeModel(modelo_a_usar)
            
            prompt_analisis = f"""
            Actúa como experto en RRHH. Analiza este feedback:
            Puntajes (1-5): Com={pilar_comunicacion}, Ges={pilar_gestion}, Cal={pilar_calidad}.
            Comentario: "{comentario}"
            Tarea:
            1. Sentimiento (Positivo/Neutro/Negativo).
            2. Categoría (Atención, Claridad, Rapidez, Proceso o Fortaleza).
            3. Resumen (Max 5 palabras).
            Responde: Sentimiento | Categoría | Resumen
            """
            
            analisis_ia = "Sin análisis"
            if comentario:
                response = model.generate_content(prompt_analisis)
                analisis_ia = response.text
            
            # 3. GUARDAR EN GOOGLE SHEETS
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            sheet = client.open(NOMBRE_SHEET).sheet1
            
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([
                fecha, pilar_comunicacion, pilar_gestion, pilar_calidad, 
                round(promedio, 2), comentario, analisis_ia
            ])
            
            st.toast("¡Evaluación enviada con éxito!", icon="✅")
            
        except Exception as e:
            st.error("Hubo un error técnico.")
            # Esto imprimirá el error exacto en pantalla para que sepamos qué pasó
            st.code(e)
