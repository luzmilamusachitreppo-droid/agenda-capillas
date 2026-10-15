import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date, timedelta
import uuid
import gspread
from google.oauth2.service_account import Credentials
import json
import tempfile
import os

# Configuración de la conexión a Google Sheets usando los Secrets de Streamlit de forma segura
@st.cache_resource
def init_connection():
    import re
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    raw = st.secrets["gcp_json"].strip()
    raw = re.sub(r",\s*}", "}", raw)  # tolera una coma de más antes de la llave final
    try:
        creds_dict = json.loads(raw, strict=False)
    except json.JSONDecodeError as e:
        st.error("El JSON de los Secrets tiene un error: " + e.msg + ". Línea " + str(e.lineno) + ", columna " + str(e.colno) + ".")
        st.stop()
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)
    
# Conectarse a la planilla y abrir las solapas
client = init_connection()
sheet = client.open_by_key("12zw7JZ3cHMg7wKZWMTsfJmmWrpP4DDjLN9K2K_w715w")

ws_recordatorios = sheet.worksheet("recordatorios")
ws_eventos = sheet.worksheet("eventos")

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
            margin: 20px auto;
            padding: 20px;
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

c_usr_info, c_logout = st.columns([3, 1])
with c_usr_info:
    st.caption(f"👤 Sesión activa: **{st.session_state['usuario_actual']}**")
with c_logout:
    if st.button("🚪 Cerrar", use_container_width=True):
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

CAPILLAS_DEFAULT = [
    "Barrio 1", "Barrio 2", "Barrio 3", "Barrio 4", 
    "Alberdi", "Güiraldes", "Puerto Tirol"
]

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

if "lista_capillas" not in st.session_state:
    st.session_state["lista_capillas"] = CAPILLAS_DEFAULT.copy()

if "fecha_seleccionada" not in st.session_state:
    st.session_state["fecha_seleccionada"] = date.today()

if "respuestas_checklist" not in st.session_state:
    st.session_state["respuestas_checklist"] = {}

if "observaciones_checklist" not in st.session_state:
    st.session_state["observaciones_checklist"] = {}

if "fotos_checklist" not in st.session_state:
    st.session_state["fotos_checklist"] = {}

if "tareas_personalizadas" not in st.session_state:
    st.session_state["tareas_personalizadas"] = {}

# ESTILOS CSS ADAPTADOS PARA MÓVIL
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    
    .block-evento {
        background-color: #d1e7dd;
        border-left: 5px solid #0f5132;
        color: #0f5132;
        border-radius: 8px;
        padding: 12px;
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
    }

    .card-note {
        background-color: #ffffff;
        border-left: 5px solid #0284c7;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    /* Ajuste táctil para celular */
    @media (max-width: 768px) {
        button {
            min-height: 46px !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
            overflow-x: auto;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 10px;
            font-size: 0.82rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# DEFINICIÓN DE FUNCIONES DE RENDERIZADO
# ==========================================

def render_agenda_mobile():
    f_sel = st.session_state["fecha_seleccionada"]
    f_sel_str = f_sel.strftime("%Y-%m-%d")

    eventos_desde_gsheets = ws_eventos.get_all_records()

    st.markdown("### 📱 Agenda Diaria")
    
    c_prev, c_fecha, c_next = st.columns([1, 2.2, 1])
    if c_prev.button("◄ Día", use_container_width=True, key="m_prev"):
        st.session_state["fecha_seleccionada"] -= timedelta(days=1)
        st.rerun()
    
    with c_fecha:
        nueva_f = st.date_input("Seleccionar Fecha", value=f_sel, label_visibility="collapsed", key="m_date_pick")
        if nueva_f != f_sel:
            st.session_state["fecha_seleccionada"] = nueva_f
            st.rerun()

    if c_next.button("Día ►", use_container_width=True, key="m_next"):
        st.session_state["fecha_seleccionada"] += timedelta(days=1)
        st.rerun()

    if st.button("📍 Ir al día de hoy", use_container_width=True, key="m_hoy"):
        st.session_state["fecha_seleccionada"] = date.today()
        st.rerun()

    st.markdown(f"#### 📅 {f_sel.strftime('%d/%m/%Y')}")

    with st.popover("➕ Agregar Tarea", use_container_width=True):
        with st.form("form_mob_add", clear_on_submit=True):
            tit_t = st.text_input("Título / Capilla", placeholder="Ej: Jardinería Barrio 1")
            nota_t = st.text_input("Detalle", placeholder="Notas de la tarea")
            cat_t = st.selectbox("Categoría", options=list(PALETA_COLORES.keys()))
            
            c1, c2 = st.columns(2)
            h_i = c1.number_input("Hora Inicio", min_value=7, max_value=20, value=8)
            h_f = c2.number_input("Hora Fin", min_value=8, max_value=21, value=12)
            
            if st.form_submit_button("Guardar Tarea", type="primary", use_container_width=True):
                if tit_t.strip():
                    ws_eventos.append_row([
                        str(uuid.uuid4()),
                        tit_t.strip(),
                        f_sel_str,
                        int(h_i),
                        int(h_f),
                        nota_t.strip()
                    ])
                    st.success("¡Agregado a Google Sheets!")
                    st.rerun()

    st.divider()

    evs_dia = [e for e in eventos_desde_gsheets if str(e.get("fecha")) == f_sel_str]
    evs_dia = sorted(evs_dia, key=lambda x: int(x.get("inicio", 0)))

    if not evs_dia:
        st.info("No hay actividades registradas para esta fecha.")
    else:
        for ev in evs_dia:
            with st.container():
                st.markdown(f"""
                    <div class="block-evento">
                        <strong>{ev.get('title', 'Sin Título')}</strong><br>
                        ⏱️ {int(ev.get('inicio', 0)):02d}:00 - {int(ev.get('fin', 0)):02d}:00 hs
                        {f'<br>💬 {ev.get("nota")}' if ev.get("nota") else ''}
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("🗑️ Eliminar Tarea", key=f"del_m_{ev.get('id')}", use_container_width=True):
                    cell = ws_eventos.find(str(ev.get('id')))
                    if cell:
                        ws_eventos.delete_rows(cell.row)
                    st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)

def render_agenda_desktop():
    f_sel = st.session_state["fecha_seleccionada"]
    f_sel_str = f_sel.strftime("%Y-%m-%d")
    hoy_real = date.today()

    eventos_desde_gsheets = ws_eventos.get_all_records()

    col_grilla, col_panel_derecho = st.columns([3.5, 1.1], gap="medium")

    with col_grilla:
        c_act, c_nav_l, c_titulo_m, c_nav_r, _ = st.columns([1, 0.4, 2.5, 0.4, 1])
        
        if c_act.button("Hoy", use_container_width=True, key="btn_hoy_desk"):
            st.session_state["fecha_seleccionada"] = hoy_real
            st.rerun()

        if c_nav_l.button("◄", use_container_width=True, key="btn_prev_desk"):
            st.session_state["fecha_seleccionada"] -= timedelta(days=7)
            st.rerun()

        inicio_semana = f_sel - timedelta(days=f_sel.weekday())
        dias_semana = [inicio_semana + timedelta(days=i) for i in range(7)]
        
        mes_principal = dias_semana[3]
        titulo_semana = f"{MESES_ESP[mes_principal.month - 1]} {mes_principal.year}"

        c_titulo_m.markdown(f"<h3 style='margin:0; text-align:center;'>{titulo_semana}</h3>", unsafe_allow_html=True)

        if c_nav_r.button("►", use_container_width=True, key="btn_next_desk"):
            st.session_state["fecha_seleccionada"] += timedelta(days=7)
            st.rerun()

        st.divider()

        cols_hdr = st.columns([0.6] + [1.8]*7)
        cols_hdr[0].write("")
        
        dias_nombres = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        for idx, d_f in enumerate(dias_semana):
            es_hoy = (d_f == hoy_real)
            es_seleccionado = (d_f == f_sel)
            
            clase_num = "day-num-selected" if es_seleccionado else ("day-num-hoy" if es_hoy else "day-num-inactive")
            
            cols_hdr[idx+1].markdown(
                f"<div style='text-align:center;'><strong>{dias_nombres[idx]}</strong><br>{d_f.day}</div>", 
                unsafe_allow_html=True
            )

        st
