import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date, timedelta
import uuid

# Configuración de página
st.set_page_config(
    page_title="Agenda de Capillas - Sistema Privado",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 🔐 MÓDULO DE AUTENTICACIÓN Y LOGIN SEGURO
# ==========================================
USUARIOS_AUTORIZADOS = {
    "admin": "capillas2026",
    "trabajador1": "clave123",
    "encargado": "parroquia2026",
    "Silvia": "Caceresythomas123"
}

if "usuario_autenticado" not in st.session_state:
    st.session_state["usuario_autenticado"] = False

if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = ""

if not st.session_state["usuario_autenticado"]:
    st.markdown("""
        <style>
        .login-box {
            max-width: 420px;
            margin: 60px auto;
            padding: 30px;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border: 1px solid #cbd5e1;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    with col_l2:
        st.markdown("## 🔒 Acceso Restringido")
        st.write("Sistema Interno de Gestión de Capillas")
        
        with st.form("form_login_privado", clear_on_submit=False):
            usr_input = st.text_input("👤 Usuario", placeholder="Ingrese su usuario")
            pass_input = st.text_input("🔑 Contraseña", type="password", placeholder="Ingrese su contraseña")
            btn_login = st.form_submit_button("Ingresar al Sistema", type="primary", use_container_width=True)
            
            if btn_login:
                usr_clean = usr_input.strip()
                pass_clean = pass_input.strip()
                
                if usr_clean in USUARIOS_AUTORIZADOS and USUARIOS_AUTORIZADOS[usr_clean] == pass_clean:
                    st.session_state["usuario_autenticado"] = True
                    st.session_state["usuario_actual"] = usr_clean
                    st.success("¡Acceso concedido!")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")
                    
    st.stop()

c_usr_info, c_logout = st.columns([4, 1])
with c_usr_info:
    st.caption(f"👤 Sesión activa: **{st.session_state['usuario_actual']}** (Acceso Autorizado)")
with c_logout:
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state["usuario_autenticado"] = False
        st.session_state["usuario_actual"] = ""
        st.rerun()

st.divider()

# ==========================================
# CONFIGURACIÓN GENERAL Y ESTADOS
# ==========================================
PALETA_COLORES = {
    "💚 Verde - Confirmado": {"bg": "#d1e7dd", "border": "#0f5132", "text": "#0f5132"},
    "💙 Azul - En proceso": {"bg": "#cff4fc", "border": "#055160", "text": "#055160"},
    "💜 Violeta - Especial": {"bg": "#e2d9f3", "border": "#593196", "text": "#593196"},
    "💛 Amarillo - Pendiente": {"bg": "#fff3cd", "border": "#664d03", "text": "#664d03"},
    "🩷 Rosa - Alerta": {"bg": "#f8d7da", "border": "#842029", "text": "#842029"}
}

COLOR_DEFAULT = PALETA_COLORES["💚 Verde - Confirmado"]

CAPILLAS_DEFAULT = [
    "Barrio 1", "Barrio 2", "Barrio 3", "Barrio 4", 
    "Alberdi", "Güiraldes", "Puerto Tirol"
]

ROTACION_JARDINERIA = {
    0: [{"nombre": "Barrio 1", "inicio": 8, "fin": 12}],
    1: [{"nombre": "Barrio 3", "inicio": 8, "fin": 12}],
    2: [{"nombre": "Barrio 2", "inicio": 12, "fin": 16}],
    3: [{"nombre": "Puerto Tirol", "inicio": 12, "fin": 16}],
    4: [{"nombre": "Barrio 4", "inicio": 8, "fin": 12}]
}

MESES_ESP = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
MESES_ESP_CORTO = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

PDF_CHECKLIST_ITEMS = {
    "🚶 Pasillos, Naves y Salón": [
        "1. Limpieza y barrido de pisos generales.",
        "2. Lavado y desinfección de pisos con producto adecuado.",
        "3. Limpieza de techos, tirantes y paredes (eliminación de telarañas).",
        "4. Sacudido y limpieza de bancos, sillas y mobiliario principal.",
        "5. Limpieza de vidrios, ventanas y marcos.",
        "6. Limpieza y sacudido de imágenes, altares y elementos litúrgicos.",
        "7. Vaciado y desinfección de papeleros y cestos de basura."
    ],
    "Resto Baños y Sanitarios": [
        "1. Limpieza y desinfección profunda de inodoros y bidet.",
        "2. Limpieza de piletas, lavamanos y griferías.",
        "3. Limpieza y secado de espejos y azulejos.",
        "4. Reposición de insumos (papel higiénico, jabón, toallas de mano).",
        "5. Barrido, trapeado y desinfección de pisos de baño.",
        "6. Vaciado y desinfección de cestos de residuos."
    ],
    "🚪 Accesos y Fachada": [
        "1. Barrido de veredas, veredones y atrio de acceso.",
        "2. Limpieza de puertas principales, picaportes y rejas.",
        "3. Reorganización de afiches, carteleras e informativos.",
        "4. Control visual de luminarias exteriores e internas."
    ]
}

CHECKLIST_JARDINERIA_DEFAULT = [
    "1. Corte de césped en sectores generales y patios.",
    "2. Bordeado, orillado y desmalezado de muros/caminos.",
    "3. Riego de plantas, arbustos y jardines.",
    "4. Podado de mantenimiento de cercos vivos y ramas bajas.",
    "5. Juntado, embolsado y retiro de restos de poda y césped.",
    "6. Control e inspección general del estado del patio/jardín."
]

def generar_eventos_jardineria(anio=2026):
    eventos = []
    curr = date(anio, 1, 1)
    fecha_fin = date(anio, 12, 31)
    delta = timedelta(days=1)
    
    while curr <= fecha_fin:
        dia_num = curr.weekday()
        if dia_num in ROTACION_JARDINERIA:
            for tarea in ROTACION_JARDINERIA[dia_num]:
                eventos.append({
                    "id": str(uuid.uuid4()),
                    "title": f"Jardinería: {tarea['nombre']}",
                    "fecha": curr.strftime("%Y-%m-%d"),
                    "inicio": tarea['inicio'],
                    "fin": tarea['fin'],
                    "estilo": COLOR_DEFAULT,
                    "nota": "Trabajo de jardinería programado"
                })
        curr += delta
    return eventos

if "lista_capillas" not in st.session_state:
    st.session_state["lista_capillas"] = CAPILLAS_DEFAULT.copy()

if "eventos_calendar" not in st.session_state:
    st.session_state["eventos_calendar"] = generar_eventos_jardineria(2026)

if "fecha_seleccionada" not in st.session_state:
    st.session_state["fecha_seleccionada"] = date.today()

if "estados_capillas" not in st.session_state:
    st.session_state["estados_capillas"] = {c: "Pendiente" for c in st.session_state["lista_capillas"]}

if "respuestas_checklist" not in st.session_state:
    st.session_state["respuestas_checklist"] = {}

if "observaciones_checklist" not in st.session_state:
    st.session_state["observaciones_checklist"] = {}

if "fotos_checklist" not in st.session_state:
    st.session_state["fotos_checklist"] = {}

if "tareas_personalizadas" not in st.session_state:
    st.session_state["tareas_personalizadas"] = {}

if "recordatorios_libres" not in st.session_state:
    st.session_state["recordatorios_libres"] = []

# ESTILOS CSS
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    
    .block-evento {
        background-color: #d1e7dd;
        border-left: 4px solid #0f5132;
        color: #0f5132;
        border-radius: 6px;
        padding: 8px 10px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }

    .card-note {
        background-color: #ffffff;
        border-left: 5px solid #0284c7;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .day-header {
        text-align: center;
        font-weight: bold;
        font-size: 0.88rem;
        color: #334155;
    }
    
    .day-num-hoy {
        font-size: 1.1rem;
        font-weight: bold;
