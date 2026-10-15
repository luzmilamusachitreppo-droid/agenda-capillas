import streamlit as st
import pandas as pd
import calendar
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
# 1. AGENDA PRINCIPAL - VISTA DE CALENDARIO
# ==========================================
with tab_cal:
    f_sel = st.session_state["fecha_seleccionada"]
    f_sel_str = f_sel.strftime("%Y-%m-%d")
    hoy_real = date.today()

    try:
        eventos_gsheets = ws_eventos.get_all_records()
    except Exception:
        eventos_gsheets = []

    # Fechas con tareas registradas
    fechas_con_tareas = {str(e.get("fecha")) for e in eventos_gsheets if e.get("fecha")}

    mes_act = f_sel.month
    ano_act = f_sel.year

    # Selector y cabecera de mes
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 12px;">
            <h2 style="color: #0284c7; margin:0; font-size:1.6rem; font-weight:700;">
                {MESES_ESP[mes_act - 1].upper()} {ano_act}
            </h2>
        </div>
    """, unsafe_allow_html=True)

    # Dibuja la cuadrícula compacta de 7 columnas igual a la foto
    cal_obj = calendar.Calendar(firstweekday=0)
    matriz_mes = cal_obj.monthdayscalendar(ano_act, mes_act)

    # CSS para forzar las 7 columnas horizontales en el celular sin deformarse
    st.markdown("""
        <style>
        .grid-calendario {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 4px;
            text-align: center;
            background-color: #ffffff;
            padding: 10px;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            margin-bottom: 15px;
        }
        .hdr-dia {
            font-size: 0.75rem;
            font-weight: 700;
            color: #64748b;
            padding-bottom: 6px;
        }
        .celda-dia {
            padding: 6px 0;
            border-radius: 8px;
            font-size: 0.95rem;
            font-weight: 600;
            color: #1e293b;
            min-height: 38px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .celda-hoy {
            border: 2px solid #0284c7;
        }
        .celda-sel {
            background-color: #ef4444 !important;
            color: #ffffff !important;
        }
        .dot-tarea {
            height: 5px;
            width: 5px;
            background-color: #22c55e;
            border-radius: 50%;
            display: inline-block;
            margin-top: 2px;
        }
        .dot-tarea-sel {
            background-color: #ffffff !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Render HTML del calendario
    html_cal = '<div class="grid-calendario">'
    dias_semana_hdr = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    for d in dias_semana_hdr:
        html_cal += f'<div class="hdr-dia">{d}</div>'

    for semana in matriz_mes:
        for d_num in semana:
            if d_num != 0:
                f_check = date(ano_act, mes_act, d_num)
                f_check_str = f_check.strftime("%Y-%m-%d")
                
                clases = ["celda-dia"]
                if f_check == f_sel:
                    clases.append("celda-sel")
                elif f_check == hoy_real:
                    clases.append("celda-hoy")

                tiene_dot = f_check_str in fechas_con_tareas
                dot_class = "dot-tarea dot-tarea-sel" if f_check == f_sel else "dot-tarea"
                dot_html = f'<span class="{dot_class}"></span>' if tiene_dot else '<span style="height:5px;"></span>'

                html_cal += f'<div class="{" ".join(clases)}">{d_num}{dot_html}</div>'
            else:
                html_cal += '<div></div>'
    
    html_cal += '</div>'
    st.markdown(html_cal, unsafe_allow_html=True)

    # Selector táctil simple para elegir el día exacto sin que se estire verticalmente
    dias_del_mes = list(range(1, calendar.monthrange(ano_act, mes_act)[1] + 1))
    dia_actual_idx = f_sel.day - 1 if f_sel.month == mes_act else 0
    
    c_sel_dia, c_btn_hoy = st.columns([2, 1])
    with c_sel_dia:
        dia_elegido = st.selectbox(
            "Ver tareas del día:",
            options=dias_del_mes,
            index=dia_actual_idx,
            key="select_dia_cal"
        )
        if dia_elegido != f_sel.day:
            st.session_state["fecha_seleccionada"] = date(ano_act, mes_act, dia_elegido)
            st.rerun()

    with c_btn_hoy:
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
        if st.button("📍 Hoy", use_container_width=True):
            st.session_state["fecha_seleccionada"] = date.today()
            st.rerun()

    st.divider()

    # Botón para añadir tarea
    with st.popover("➕ Cargar nueva tarea a este día", use_container_width=True):
        with st.form("form_add_evento", clear_on_submit=True):
            tit_t = st.text_input("Título / Capilla", placeholder="Ej: Jardinería Barrio 1")
            nota_t = st.text_input("Detalle", placeholder="Notas de la tarea")
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
                    st.success("¡Guardado!")
                    st.rerun()

    # Listado de actividades del día elegido
    st.markdown(f"#### 📋 Tareas del {f_sel.strftime('%d/%m/%Y')}:")
    evs_dia = [e for e in eventos_gsheets if str(e.get("fecha")) == f_sel_str]
    
    if not evs_dia:
        st.info("No hay tareas programadas para este día.")
    else:
        for ev in evs_dia:
            st.markdown(f"""
                <div style="background-color: #d1e7dd; border-left: 5px solid #0f5132; padding: 12px; border-radius: 8px; margin-bottom: 8px; color: #0f5132;">
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
