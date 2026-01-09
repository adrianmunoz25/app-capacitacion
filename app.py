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
    .stSlider [data-baseweb="slider"] { padding-top: 15px; }
    div[data-testid="stCaptionContainer"] { min-height: 40px; }
    </style>
    """, unsafe_allow_html=True)

# 1️⃣ HEADER / INICIO
st.title("Evaluación del Servicio de Diseño de Curso")
st.markdown("Tu feedback nos ayuda a mejorar la forma en que diseñamos y entregamos cursos.")
st.caption("⏱ Tiempo estimado: 2–3 minutos")
st.markdown("---")

# Guía de escala visual
st.info("ℹ️ **Guía de calificación:** \n1️⃣ = **Muy Deficiente** 😡 ... 3️⃣ = **Adecuado** 😐 ... 5️⃣ = **Excelente** 🤩")

# 2️⃣ SECCIÓN 1: PROCESO
st.subheader("1. Experiencia durante el proceso")
st.caption("Evalúa cómo fue trabajar con nosotros durante el desarrollo del curso.")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**🗣️ Comunicación y acompañamiento**")
    st.caption("¿Qué tan clara y cercana fue la comunicación durante el proyecto?")
    s1_comunicacion = st.slider("Comunicación", 1, 5, 3, label_visibility="collapsed", key="s1_com")

with col2:
    st.markdown("**⚡ Gestión y tiempos**")
    st.caption("¿Qué tan oportuno fue el seguimiento y la atención a solicitudes?")
    s1_gestion = st.slider("Gestión", 1, 5, 3, label_visibility="collapsed", key="s1_ges")

st.markdown("**🗺️ Claridad del proceso**")
st.caption("¿Qué tan claro fue el proceso de trabajo de inicio a cierre?")
s1_proceso = st.slider("Proceso", 1, 5, 3, label_visibility="collapsed", key="s1_proc")

# 3️⃣ SECCIÓN 2: CALIDAD (NUEVA)
st.markdown("---")
st.subheader("2. Calidad del curso")
st.caption("Evalúa el resultado final del curso entregado.")

col3, col4 = st.columns(2)
with col3:
    st.markdown("**📚 Calidad del contenido**")
    st.caption("El contenido del curso cumple con lo esperado.")
    s2_contenido = st.slider("Contenido", 1, 5, 3, label_visibility="collapsed", key="s2_cont")

with col4:
    st.markdown("**🎯 Adecuación a la necesidad**")
    st.caption("El curso responde a la necesidad planteada inicialmente.")
    s2_adecuacion = st.slider("Adecuación", 1, 5, 3, label_visibility="collapsed", key="s2_adec")

st.markdown("**🛠️ Aplicación práctica**")
st.caption("El contenido es aplicable al contexto real del equipo.")
s2_aplicacion = st.slider("Aplicación", 1, 5, 3, label_visibility="collapsed", key="s2_app")

# 4️⃣ SECCIÓN 3: VALOR E IMPACTO (NUEVA)
st.markdown("---")
st.subheader("3. Valor e impacto")

st.markdown("**💎 Valor del servicio**")
st.caption("¿Qué tanto valor aporta este curso al equipo o negocio?")
s3_valor = st.slider("Valor", 1, 5, 3, label_visibility="collapsed", key="s3_val")

st.markdown("**🌟 Recomendación (NPS)**")
st.caption("¿Qué tan probable es que recomiendes este servicio a otros equipos? (0-10)")
s3_recomendacion = st.slider("Recomendación", 0, 10, 8, label_visibility="collapsed", key="s3_rec")

# Cálculo de promedio (excluyendo NPS que es escala 10)
promedio = (s1_comunicacion + s1_gestion + s1_proceso + s2_contenido + s2_adecuacion + s2_aplicacion + s3_valor) / 7

# 5️⃣ SECCIÓN 4: COMENTARIOS (MEJORADA)
st.markdown("---")
st.subheader("4. Comentarios finales")

c_fortalezas = st.text_area("Fortalezas: ¿Qué fue lo más valioso del servicio o del curso?")
c_mejoras = st.text_area("Oportunidades: ¿Qué podríamos mejorar en futuros proyectos?")
c_otros = st.text_area("Comentario adicional (opcional)")

# --- BOTÓN DE ENVÍO ---
st.markdown("---")
if st.button("Enviar evaluación 🚀", type="primary"):
    with st.spinner("Guardando tu feedback..."):
        
        # 1. ANÁLISIS IA (Actualizado con nuevos campos)
        analisis_ia = "Sin análisis"
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=api_key)
            
            modelo_a_usar = "models/gemini-1.5-flash"
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name:
                        modelo_a_usar = m.name
                        break
            except: pass

            model = genai.GenerativeModel(modelo_a_usar)
            
            # Prompt enriquecido con toda la data nueva
            prompt = f"""
            Analiza esta evaluación de capacitación.
            Datos cuantitativos (1-5): Proc={s1_proceso}, Contenido={s2_contenido}, Valor={s3_valor}. NPS(0-10)={s3_recomendacion}.
            Comentarios:
            - Fortalezas: {c_fortalezas}
            - Mejoras: {c_mejoras}
            - Otros: {c_otros}
            
            Tarea: Resume en UNA frase de máximo 10 palabras el sentimiento principal del cliente.
            """
            
            # Solo analizamos si escribió algo
            if len(c_fortalezas) > 2 or len(c_mejoras) > 2:
                response = model.generate_content(prompt)
                analisis_ia = response.text
            else:
                analisis_ia = "Sin comentarios textuales"
                
        except Exception as e:
            print(f"IA Error: {e}")

        # 2. GUARDAR EN SHEETS
        try:
            scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
            client = gspread.authorize(credentials)
            sheet = client.open(NOMBRE_SHEET).sheet1
            
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Guardamos TODAS las columnas nuevas
            sheet.append_row([
                fecha, 
                s1_comunicacion, s1_gestion, s1_proceso,       # Sección 1
                s2_contenido, s2_adecuacion, s2_aplicacion,    # Sección 2
                s3_valor, s3_recomendacion,                    # Sección 3
                round(promedio, 2),                            # Promedio
                c_fortalezas, c_mejoras, c_otros,              # Textos
                analisis_ia                                    # IA
            ])
            
            st.success("✅ Gracias por tomarte el tiempo de compartir tu feedback. Tu opinión nos ayuda a mejorar.")
            st.balloons()
            
        except Exception as e:
            st.error("⚠️ Error al guardar.")
            st.write("Por favor avisa al administrador. Detalle:", e)
