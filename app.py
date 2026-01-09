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
    div[data-testid="stSelectSlider"] > div { padding-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# Función de ayuda
def obtener_numero(texto):
    return int(texto.split(" - ")[0])

ESCALA_5 = ["1 - Muy Deficiente", "2 - Deficiente", "3 - Adecuado", "4 - Bueno", "5 - Excelente"]

# 1️⃣ HEADER / INICIO
st.title("Evaluación del Servicio de Diseño de Curso")
st.markdown("Tu feedback nos ayuda a mejorar la forma en que diseñamos y entregamos cursos.")
st.caption("⏱ Tiempo estimado: 2–3 minutos")
st.markdown("---")

# --- NUEVOS CAMPOS DE IDENTIFICACIÓN ---
st.subheader("📋 Datos del Proyecto")
col_datos1, col_datos2 = st.columns(2)

with col_datos1:
    proyecto = st.text_input("Nombre del Curso / Proyecto", placeholder="Ej. Onboarding Ventas")

with col_datos2:
    evaluador = st.text_input("Tu Correo / Nombre", placeholder="nombre@empresa.com")

st.markdown("---")

# Guía de escala
st.info("ℹ️ **Guía de calificación:** \n1️⃣ = **Muy Deficiente** 😡 ... 3️⃣ = **Adecuado** 😐 ... 5️⃣ = **Excelente** 🤩")

# 2️⃣ SECCIÓN 1: PROCESO
st.subheader("1. Experiencia durante el proceso")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**🗣️ Comunicación**")
    v1_com = st.select_slider("Comunicación", options=ESCALA_5, value="3 - Adecuado", label_visibility="collapsed", key="s1_com")
with col2:
    st.markdown("**⚡ Gestión y tiempos**")
    v1_ges = st.select_slider("Gestión", options=ESCALA_5, value="3 - Adecuado", label_visibility="collapsed", key="s1_ges")

st.markdown("**🗺️ Claridad del proceso**")
v1_proc = st.select_slider("Proceso", options=ESCALA_5, value="3
