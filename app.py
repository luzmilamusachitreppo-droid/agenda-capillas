import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date, timedelta
import uuid
import gspread
from google.oauth2.service_account import Credentials
import json

# Configuración de página obligatoria al inicio
st.set_page_config(
    page_title="Agenda de Capillas - Sistema Privado",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Conexión segura a Google Sheets
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

# Barra superior con usuario activo y cerrar sesión
c_usr, c_out = st.columns([3, 1])
with c_usr:
    st.caption(f"👤 Sesión activa: **{st.session_state['usuario_actual']}**")
with c_out:
    if st.button("🚪 Cerrar", use_container_width=True):
        st.session_state["usuario_autenticado"] = False
        st.rerun()

st.divider()

# Listas y estados por defecto
CAPILLAS_DEFAULT = ["Barrio 1", "Barrio 2", "Barrio 3", "Barrio 4", "Alberdi", "Güiraldes", "Puerto Tirol"]
MESES_ESP = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

if "lista_capillas" not in st.session_state:
    st.session_state["lista_capillas"] = CAPILLAS_DEFAULT.copy()
if "fecha_seleccionada" not in st.session_state:
    st.session_state["fecha_seleccionada"] = date.today()

# Selector de modo (Celular / Computadora)
st.radio(
    "🖥️ Vista optimizada para:",
    ["📱 Celular", "💻 Computadora"],
    horizontal=True,
    key="selector_modo_dispositivo"
)

# Pestañas principales de la aplicación
tab_cal, tab_check, tab_capillas, tab_notes = st.tabs([
    "📅 1. Agenda Principal", 
    "📝 2. Checklist Digital", 
    "⛪ 3. Resumen de Capillas",
    "📌 4. Recordatorios Rápidos"
])

# ==========================================
# 1. PESTAÑA AGENDA PRINCIPAL (CON CALENDARIO SUPERIOR)
# ==========================================
with tab_cal:
    f_sel = st.session_state["fecha_seleccionada"]
    f_sel_str = f_sel.strftime("%Y-%m-%d")
    hoy_real = date.today()
    
    st.markdown("### 📅 Calendario de Actividades")

    # Traer todos los eventos de Google Sheets para marcar los días con tareas
    try:
        eventos_gsheets = ws_eventos.get_all_records()
    except Exception:
        eventos_gsheets = []

    # Crear conjunto con las fechas que tienen tareas (para marcar en el calendario superior)
    fechas_con_tareas = {str(e.get("fecha")) for e in eventos_gsheets if e.get("fecha")}

    # --- CALENDARIO SUPERIOR INTERACTIVO DEL MES ---
    mes_actual = f_sel.month
    ano_actual = f_sel.year
    st.markdown(f"<h4 style='text-align: center; color: #0284c7; margin-bottom: 5px;'>{MESES_ESP[mes_actual - 1].upper()} {ano_actual}</h4>", unsafe_allow_html=True)

    cal_obj = calendar.Calendar(firstweekday=0) # Comienza en Lunes
    matriz_mes = cal_obj.monthdayscalendar(ano_actual, mes_actual)

    # Cabecera de días de la semana
    cols_dias_hdr = st.columns(7)
    nombres_dias = ["L", "M", "Mi", "J", "V", "S", "D"]
    for i, d_nom in enumerate(nombres_dias):
        cols_dias_hdr[i].markdown(f"<div style='text-align: center; font-size: 0.75rem; font-weight: bold; color: #64748b;'>{d_nom}</div>", unsafe_allow_html=True)

    # Dibujar la grilla del calendario del mes en botones táctiles
    for semana in matriz_mes:
        cols_sem = st.columns(7)
        for i, d_num in enumerate(semana):
            if d_num != 0:
                fecha_iter = date(ano_actual, mes_actual, d_num)
                f_iter_str = fecha_iter.strftime("%Y-%m-%d")
                
                # Verificar si este día tiene tareas agendadas
                tiene_tarea = f_iter_str in fechas_con_tareas
                
                # Definir etiqueta visual del botón según estado
                etiqueta_btn = f"{d_num} •" if tiene_tarea else str(d_num)
                
                # Seleccionar tipo de botón según sea el día seleccionado actualmente
                es_seleccionado = (fecha_iter == f_sel)
                tipo_btn = "primary" if es_seleccionado else "secondary"
                
                if cols_sem[i].button(etiqueta_btn, key=f"cal_dia_{mes_actual}_{d_num}", type=tipo_btn, use_container_width=True):
                    st.session_state["fecha_seleccionada"] = fecha_iter
                    st.rerun()
            else:
                cols_sem[i].write("")

    st.divider()

    # Controles de navegación rápida por día
    c_prev, c_fecha, c_next = st.columns([1, 2.2, 1])
    if c_prev.button("◄ Día", use_container_width=True, key="m_prev"):
        st.session_state["fecha_seleccionada"] -= timedelta(days=1)
        st.rerun()
    with c_fecha:
        nueva_f = st.date_input("Fecha", value=f_sel, label_visibility="collapsed", key="m_date_pick")
        if nueva_f != f_sel:
            st.session_state["fecha_seleccionada"] = nueva_f
            st.rerun()
    if c_next.button("Día ►", use_container_width=True, key="m_next"):
        st.session_state["fecha_seleccionada"] += timedelta(days=1)
        st.rerun()

    if st.button("📍 Ir al día de hoy", use_container_width=True, key="m_hoy"):
        st.session_state["fecha_seleccionada"] = date.today()
        st.rerun()

    with st.popover("➕ Agregar Nueva Tarea", use_container_width=True):
        with st.form("form_add_evento", clear_on_submit=True):
            tit_t = st.text_input("Título / Capilla", placeholder="Ej: Jardinería Barrio 1")
            nota_t = st.text_input("Detalle", placeholder="Notas adicionales")
            c1, c2 = st.columns(2)
            h_i = c1.number_input("Hora Inicio", min_value=7, max_value=20, value=8)
            h_f = c2.number_input("Hora Fin", min_value=8, max_value=21, value=12)
            
            if st.form_submit_button("Guardar en Google Sheets", type="primary", use_container_width=True):
                if tit_t.strip():
                    ws_eventos.append_row([
                        str(uuid.uuid4()),
                        tit_t.strip(),
                        f_sel_str,
                        int(h_i),
                        int(h_f),
                        nota_t.strip()
                    ])
                    st.success("¡Guardado con éxito!")
                    st.rerun()

    st.markdown(f"#### 📋 Actividades del día: {f_sel.strftime('%d/%m/%Y')}")
    
    evs_dia = [e for e in eventos_gsheets if str(e.get("fecha")) == f_sel_str]
    
    if not evs_dia:
        st.info("No hay actividades registradas para esta fecha.")
    else:
        for ev in evs_dia:
            st.markdown(f"""
                <div style="background-color: #d1e7dd; border-left: 5px solid #0f5132; padding: 12px; border-radius: 8px; margin-bottom: 10px; color: #0f5132;">
                    <strong>{ev.get('title', 'Sin Título')}</strong><br>
                    ⏱️ {int(ev.get('inicio', 0)):02d}:00 - {int(ev.get('fin', 0)):02d}:00 hs
                    {f'<br>💬 {ev.get("nota")}' if ev.get("nota") else ''}
                </div>
            """, unsafe_allow_html=True)
            if st.button("🗑️ Eliminar Tarea", key=f"del_ev_{ev.get('id')}", use_container_width=True):
                cell = ws_eventos.find(str(ev.get('id')))
                if cell:
                    ws_eventos.delete_rows(cell.row)
                st.rerun()

# ==========================================
# 2. PESTAÑA CHECKLIST DIGITAL
# ==========================================
with tab_check:
    st.header("📝 Checklist Digital de Control")
    capilla_sel = st.selectbox("Seleccionar Capilla:", st.session_state["lista_capillas"])
    tipo_insp = st.radio("Inspección:", ["🧹 Limpieza", "🌿 Jardinería"], horizontal=True)
    st.info(f"Sección de control para {capilla_sel} ({tipo_insp}).")

# ==========================================
# 3. PESTAÑA RESUMEN DE CAPILLAS
# ==========================================
with tab_capillas:
    st.header("⛪ Resumen de Capillas")
    for c in st.session_state["lista_capillas"]:
        st.subheader(c)
        st.selectbox(f"Estado de {c}:", ["Pendiente", "En Proceso", "Completado"], key=f"est_{c}")
        st.divider()

# ==========================================
# 4. PESTAÑA RECORDATORIOS RÁPIDOS
# ==========================================
with tab_notes:
    st.header("📌 Recordatorios Rápidos")

    with st.form("form_nueva_nota_libre", clear_on_submit=True):
        titulo_nota = st.text_input("📌 Recordatorio / Nota:")
        detalle_nota = st.text_area("✍️ Detalle adicional:")
        prioridad_nota = st.selectbox("Prioridad:", ["💛 Normal", "🩷 Urgente / Importante", "💚 Idea / Nota"])
        
        if st.form_submit_button("➕ Añadir Recordatorio", type="primary", use_container_width=True):
            if titulo_nota.strip():
                ws_recordatorios.append_row([
                    str(uuid.uuid4()),
                    titulo_nota.strip(),
                    detalle_nota.strip(),
                    prioridad_nota,
                    st.session_state["usuario_actual"],
                    datetime.now().strftime("%d/%m/%Y %H:%M")
                ])
                st.success("¡Recordatorio guardado!")
                st.rerun()

    st.divider()
    
    recs = ws_recordatorios.get_all_records()
    st.subheader(f"📋 Recordatorios Guardados ({len(recs)})")

    if not recs:
        st.info("No hay recordatorios pendientes.")
    else:
        for idx, nota in enumerate(recs):
            tit = nota.get("titulo", "Sin título")
            det = nota.get("detalle", "")
            prio = nota.get("prioridad", "💛 Normal")
            autor = nota.get("creado_por", "Sistema")
            fec = nota.get("fecha_creacion", "")
            id_n = str(nota.get("id", ""))

            st.markdown(f"""
                <div style="background-color: #ffffff; border-left: 5px solid #0284c7; padding: 12px; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                    <h4 style="margin:0 0 6px 0; color:#1e293b;">{tit}</h4>
                    <p style="margin:0 0 8px 0; color:#475569; font-size:0.9rem;">{det}</p>
                    <span style="font-size:0.75rem; color:#64748b;">👤 {autor} | 🕒 {fec} ({prio})</span>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("✔️ Marcar como resuelto / Borrar", key=f"btn_del_n_{idx}_{id_n}", use_container_width=True):
                if id_n:
                    cell = ws_recordatorios.find(id_n)
                    if cell:
                        ws_recordatorios.delete_rows(cell.row)
                st.rerun()
