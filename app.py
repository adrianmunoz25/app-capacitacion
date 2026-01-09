import streamlit as st
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- CONFIGURACIÓN ---
NOMBRE_SHEET = "Evaluaciones de capacitación" 

# --- INTERFAZ VISUAL ---
st.set_page_config(page_title="Evaluación de Diseño", page_icon="🎓", layout="centered")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stTextArea textarea {font-size: 14px;}
    /* Ajuste para que el slider de texto se vea bien */
    div[data-testid="stSelectSlider"] > div { padding-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE AYUDA (Convierte texto a número) ---
# Esto sirve para que "5 - Excelente" cuente como un 5 en el promedio
def obtener_numero(texto):
    return int(texto.split(" - ")[0])

# --- OPCIONES DE LA ESCALA ---
ESCALA_5 = [
    "1 - Muy Deficiente", 
    "2 - Deficiente", 
    "3 - Adecuado", 
    "4 - Bueno", 
    "5 - Excelente"
]

# 1️⃣ HEADER / INICIO
st.title("Evaluación del Servicio de Diseño de Curso")
st.markdown("Tu feedback nos ayuda a mejorar la forma en que diseñamos y entregamos cursos.")
st.caption("⏱ Tiempo estimado: 2–3 minutos")
st.markdown("---")

# 2️⃣ SECCIÓN 1: PROCESO
st.subheader("1. Experiencia durante el proceso")
st.caption("Evalúa cómo fue trabajar con nosotros durante el desarrollo del curso.")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**🗣️ Comunicación**")
    st.caption("¿Qué tan clara y cercana fue la comunicación?")
    v1_com = st.select_slider("Comunicación", options=ESCALA_5, value="3 - Adecuado", label_visibility="collapsed", key="s1_com")

with col2:
    st.markdown("**⚡ Gestión y tiempos**")
    st.caption("¿Qué tan oportuno fue el seguimiento?")
    v1_ges = st.select_slider("Gestión", options=ESCALA_5, value="3 - Adecuado", label_visibility="collapsed", key="s1_ges")

st.markdown("**🗺️ Claridad del proceso**")
st.caption("¿Qué tan claro fue el proceso de inicio a cierre?")
v1_proc = st.select_slider("Proceso", options=ESCALA_5, value="3 - Adecuado", label_visibility="collapsed", key="s1_proc")

# 3️⃣ SECCIÓN 2: CALIDAD DEL CURSO
st.markdown("---")
st.subheader("2. Calidad del curso")
st.caption("Evalúa el resultado final del curso entregado.")

col3, col4 = st.columns(2)
with col3:
    st.markdown("**📚 Calidad del contenido**")
    st.caption("El contenido cumple con lo esperado.")
    v2_cont = st.select_slider("Contenido", options=ESCALA_5, value="3 - Adecuado", label_visibility="collapsed", key="s2_cont")

with col4:
    st.markdown("**🎯 Adecuación**")
    st.caption("Responde a la necesidad planteada.")
    v2_adec = st.select_slider("Adecuación", options=ESCALA_5, value="3 - Adecuado", label_visibility="collapsed", key="s2_adec")

st.markdown("**🛠️ Aplicación práctica**")
st.caption("Es aplicable al contexto real del equipo.")
v2_app = st.select_slider("Aplicación", options=ESCALA_5, value="3 - Adecuado", label_visibility="collapsed", key="s2_app")

# 4️⃣ SECCIÓN 3: VALOR E IMPACTO
st.markdown("---")
st.subheader("3. Valor e impacto")

st.markdown("**💎 Valor del servicio**")
st.caption("¿Qué tanto valor aporta este curso al negocio?")
v3_val = st.select_slider("Valor", options=ESCALA_5, value="3 - Adecuado", label_visibility="collapsed", key="s3_val")

st.markdown("**🌟 Recomendación (NPS)**")
st.caption("¿Qué tan probable es que nos recomiendes? (0-10)")
# El NPS se queda numérico porque es estándar 0-10
nps_val = st.slider("Recomendación", 0, 10, 8, label_visibility="collapsed", key="s3_rec")

# --- CÁLCULO DE NÚMEROS REALES ---
# Convertimos el texto "5 - Excelente" a el número 5 para guardar y promediar
n1 = obtener_numero(v1_com)
n2 = obtener_numero(v1_ges)
n3 = obtener_numero(v1_proc)
n4 = obtener_numero(v2_cont)
n5 = obtener_numero(v2_adec)
n6 = obtener_numero(v2_app)
n7 = obtener_numero(v3_val)

promedio = (n1 + n2 + n3 + n4 + n5 + n6 + n7) / 7

# 5️⃣ SECCIÓN 4: COMENTARIOS
st.markdown("---")
st.subheader("4. Comentarios finales")

c_fortalezas = st.text_area("Fortalezas: ¿Qué fue lo más valioso?")
c_mejoras = st.text_area("Oportunidades: ¿Qué podríamos mejorar?")
c_otros = st.text_area("Comentario adicional (opcional)")

# --- BOTÓN DE ENVÍO ---
st.markdown("---")
if st.button("Enviar evaluación 🚀", type="primary"):
    with st.spinner("Guardando tu feedback..."):
        
        # 1. ANÁLISIS IA
        analisis_ia = "Sin análisis"
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=api_key)
            
            # Selector de modelo robusto
            modelo_a_usar = "models/gemini-1.5-flash"
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name:
                        modelo_a_usar = m.name
                        break
            except: pass

            model = genai.GenerativeModel(modelo_a_usar)
            
            prompt = f"""
            Analiza feedback capacitación.
            Puntajes: Promedio={promedio}, NPS={nps_val}.
            Comentarios: {c_fortalezas} | {c_mejoras} | {c_otros}.
            Resume el sentimiento en 1 frase corta.
            """
            
            if len(c_fortalezas) > 2 or len(c_mejoras) > 2:
                response = model.generate_content(prompt)
                analisis_ia = response.text
            else:
                analisis_ia = "Sin texto para analizar"
        except: pass

        # 2. GUARDAR EN SHEETS
        try:
            scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
            client = gspread.authorize(credentials)
            sheet = client.open(NOMBRE_SHEET).sheet1
            
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Guardamos los NÚMEROS (n1, n2...) no el texto largo, para que tu Excel quede limpio
            sheet.append_row([
                fecha, 
                n1, n2, n3,      # Sección 1
                n4, n5, n6,      # Sección 2
                n7, nps_val,     # Sección 3
                round(promedio, 2),
                c_fortalezas, c_mejoras, c_otros,
                analisis_ia
            ])
            
            st.success("✅ ¡Gracias! Tu evaluación ha sido registrada.")
            st.balloons()
            
        except Exception as e:
            st.error("⚠️ Error al guardar.")
            st.write(e)
