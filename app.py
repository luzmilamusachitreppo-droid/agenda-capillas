import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import uuid
import gspread
from google.oauth2.service_account import Credentials
import json

# Configuración de página
st.set_page_config(
    page_title="Agenda de Capillas",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Conexión a Google Sheets
@st.cache_resource
def init_connection():
    import re
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    raw = st.secrets["gcp_json"].strip()
    raw = re.sub(r",\s*}", "}", raw)
    creds_dict = json.loads(raw, strict=False)
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

client = init_connection()
sheet = client.open_by_key("12zw7JZ3cHMg7wKZWMTsfJmmWrpP4DDjLN9K2K_w715w")

ws_recordatorios = sheet.worksheet("recordatorios")
ws_eventos = sheet.worksheet("eventos")

# Autenticación
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
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("## 🔒 Acceso Restringido")
        st.write("Sistema Interno de Gestión de Capillas")
        with st.form("form_login_privado"):
            usr_input = st.text_input("👤 Usuario")
            pass_input = st.text_input("🔑 Contraseña", type="password")
            if st.form_submit_button("Ingresar al Sistema", type="primary", use_container_width=True):
                if usr_input.strip() in USUARIOS_AUTORIZADOS and USUARIOS_AUTORIZADOS[usr_input.strip()] == pass_input.strip():
                    st.session_state["usuario_autenticado"] = True
                    st.session_state["usuario_actual"] = usr_input.strip()
                    st.success("¡Acceso concedido!")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")
    st.stop()

# Encabezado
c_usr, c_out = st.columns([3, 1])
with c_usr:
    st.caption(f"👤 Sesión activa: **{st.session_state['usuario_actual']}**")
with c_out:
    if st.button("🚪 Cerrar", use_container_width=True):
        st.session_state["usuario_autenticado"] = False
        st.rerun()

st.divider()

CAPILLAS_DEFAULT = ["Barrio 1", "Barrio 2", "Barrio 3", "Barrio 4", "Alberdi", "Güiraldes", "Puerto Tirol"]
MESES_ESP = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

PALETA_COLORES = {
    "💚 Verde - Confirmado": {"bg": "#d1e7dd", "border": "#0f5132", "text": "#0f5132"},
    "💙 Azul - En proceso": {"bg": "#cff4fc", "border": "#055160", "text": "#055160"},
    "💜 Violeta - Especial": {"bg": "#e2d9f3", "border": "#593196", "text": "#593196"},
    "💛 Amarillo - Pendiente": {"bg": "#fff3cd", "border": "#664d03", "text": "#664d03"},
    "🩷 Rosa - Alerta": {"bg": "#f8d7da", "border": "#842029", "text": "#842029"}
}

if "lista_capillas" not in st.session_state:
    st.session_state["lista_capillas"] = CAPILLAS_DEFAULT.copy()
if "fecha_seleccionada" not in st.session_state:
    st.session_state["fecha_seleccionada"] = date.today()

tab_cal, tab_check, tab_capillas, tab_notes = st.tabs([
    "📅 1. Agenda Principal", 
    "📝 2. Checklist Digital", 
    "⛪ 3. Resumen de Capillas",
    "📌 4. Recordatorios Rápidos"
])

# ==========================================
# 1. AGENDA PRINCIPAL
# ==========================================
with tab_cal:
    f_sel = st.session_state["fecha_seleccionada"]
    f_sel_str = f_sel.strftime("%Y-%m-%d")
    hoy_real = date.today()

    try:
        eventos_gsheets = ws_eventos.get_all_records()
    except Exception:
        eventos_gsheets = []

    fechas_con_tareas = {str(e.get("fecha")) for e in eventos_gsheets if e.get("fecha")}

    st.markdown(f"<h3 style='text-align: center; color: #0284c7; margin-bottom: 5px;'>📅 Semana del {f_sel.strftime('%d/%m/%Y')}</h3>", unsafe_allow_html=True)

    # Botones de navegación de semana
    col_nav1, col_hoy, col_nav2 = st.columns([1, 1, 1])
    if col_nav1.button("◄ Semana", use_container_width=True):
        st.session_state["fecha_seleccionada"] -= timedelta(days=7)
        st.rerun()
    if col_hoy.button("📍 Hoy", use_container_width=True):
        st.session_state["fecha_seleccionada"] = date.today()
        st.rerun()
    if col_nav2.button("Semana ►", use_container_width=True):
        st.session_state["fecha_seleccionada"] += timedelta(days=7)
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Barra horizontal de los 7 días de la semana seleccionada (entra perfecto en celular)
    inicio_semana = f_sel - timedelta(days=f_sel.weekday())
    dias_semana = [inicio_semana + timedelta(days=i) for i in range(7)]
    nombres_cortos = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

    cols_semana = st.columns(7)
    for idx, d_f in enumerate(dias_semana):
        d_str = d_f.strftime("%Y-%m-%d")
        tiene_tarea = d_str in fechas_con_tareas
        etiqueta = f"{nombres_cortos[idx]}\n{d_f.day}" + (" •" if tiene_tarea else "")
        
        es_seleccionado = (d_f == f_sel)
        tipo_btn = "primary" if es_seleccionado else "secondary"
        
        if cols_semana[idx].button(etiqueta, key=f"btn_semana_{d_str}", type=tipo_btn, use_container_width=True):
            st.session_state["fecha_seleccionada"] = d_f
            st.rerun()

    st.divider()

    # Contenedores para tareas del día y formulario de carga
    col_izq, col_der = st.columns([1.2, 1], gap="medium")

    with col_izq:
        st.markdown(f"#### 📋 Tareas del {f_sel.strftime('%d/%m/%Y')}")
        evs_dia = [e for e in eventos_gsheets if str(e.get("fecha")) == f_sel_str]
        
        if not evs_dia:
            st.info("No hay tareas programadas para este día.")
        else:
            for ev in evs_dia:
                cat_ev = ev.get("categoria", "💚 Verde - Confirmado")
                estilo = PALETA_COLORES.get(cat_ev, PALETA_COLORES["💚 Verde - Confirmado"])
                
                st.markdown(f"""
                    <div style="background-color: {estilo['bg']}; border-left: 5px solid {estilo['border']}; padding: 10px; border-radius: 8px; margin-bottom: 8px; color: {estilo['text']};">
                        <strong>{ev.get('title', 'Sin Título')}</strong><br>
                        ⏱️ {int(ev.get('inicio', 0)):02d}:00 - {int(ev.get('fin', 0)):02d}:00 hs
                        {f'<br>💬 {ev.get("nota")}' if ev.get("nota") else ''}
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("🗑️ Borrar", key=f"del_ev_{ev.get('id')}", use_container_width=True):
                    cell = ws_eventos.find(str(ev.get('id')))
                    if cell:
                        ws_eventos.delete_rows(cell.row)
                    st.rerun()

    with col_der:
        st.markdown("#### ➕ Agregar Tarea")
        with st.form("form_add_evento_col", clear_on_submit=True):
            f_tarea = st.date_input("Fecha:", value=f_sel)
            tit_t = st.text_input("Título / Capilla", placeholder="Ej: Jardinería Barrio 1")
            cat_t = st.selectbox("Situación / Color:", options=list(PALETA_COLORES.keys()))
            nota_t = st.text_area("Detalle adicional", placeholder="Notas...", height=68)
            
            c1, c2 = st.columns(2)
            h_i = c1.number_input("Inicio", min_value=7, max_value=20, value=8)
            h_f = c2.number_input("Fin", min_value=8, max_value=21, value=12)
            
            if st.form_submit_button("Guardar en Agenda", type="primary", use_container_width=True):
                if tit_t.strip():
                    ws_eventos.append_row([
                        str(uuid.uuid4()),
                        tit_t.strip(),
                        f_tarea.strftime("%Y-%m-%d"),
                        int(h_i),
                        int(h_f),
                        nota_t.strip(),
                        cat_t
                    ])
                    st.session_state["fecha_seleccionada"] = f_tarea
                    st.success("¡Agregado con éxito!")
                    st.rerun()

# ==========================================
# 2. CHECKLIST DIGITAL
# ==========================================
with tab_check:
    st.header("📝 Checklist Digital")
    capilla_sel = st.selectbox("Capilla:", st.session_state["lista_capillas"])
    tipo_insp = st.radio("Tipo:", ["🧹 Limpieza", "🌿 Jardinería"], horizontal=True)

# ==========================================
# 3. RESUMEN DE CAPILLAS
# ==========================================
with tab_capillas:
    st.header("⛪ Capillas")
    for c in st.session_state["lista_capillas"]:
        st.subheader(c)
        st.selectbox(f"Estado {c}:", ["Pendiente", "En Proceso", "Completado"], key=f"est_{c}")
        st.divider()

# ==========================================
# 4. RECORDATORIOS RÁPIDOS
# ==========================================
with tab_notes:
    st.header("📌 Recordatorios")
    with st.form("form_nueva_nota_libre", clear_on_submit=True):
        titulo_nota = st.text_input("Nota:")
        detalle_nota = st.text_area("Detalle:")
        prioridad_nota = st.selectbox("Prioridad:", ["💛 Normal", "🩷 Urgente", "💚 Idea"])
        if st.form_submit_button("➕ Añadir", type="primary", use_container_width=True):
            if titulo_nota.strip():
                ws_recordatorios.append_row([
                    str(uuid.uuid4()),
                    titulo_nota.strip(),
                    detalle_nota.strip(),
                    prioridad_nota,
                    st.session_state["usuario_actual"],
                    datetime.now().strftime("%d/%m/%Y %H:%M")
                ])
                st.success("Guardado")
                st.rerun()

    st.divider()
    recs = ws_recordatorios.get_all_records()
    for idx, nota in enumerate(recs):
        st.markdown(f"**{nota.get('titulo')}**: {nota.get('detalle')}")
        if st.button("Borrar", key=f"del_n_{idx}_{nota.get('id')}"):
            cell = ws_recordatorios.find(str(nota.get('id')))
            if cell:
                ws_recordatorios.delete_rows(cell.row)
            st.rerun()
