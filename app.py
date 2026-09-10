import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date, timedelta
import uuid

# Configuración de página
st.set_page_config(
    page_title="Calendario Jardinería y Limpieza",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Paleta de colores
PALETA_COLORES = {
    "🩵 Celeste": {"bg": "#e0f7fa", "border": "#29b6f6", "text": "#006064"},
    "💚 Verde": {"bg": "#e8f5e9", "border": "#4caf50", "text": "#1b5e20"},
    "💜 Violeta": {"bg": "#f3e5f5", "border": "#ab47bc", "text": "#4a148c"},
    "🩷 Rosa": {"bg": "#fce4ec", "border": "#ec407a", "text": "#880e4f"},
    "💛 Amarillo": {"bg": "#fffde7", "border": "#fbc02d", "text": "#f57f17"},
    "🧡 Naranja": {"bg": "#fff3e0", "border": "#ffa726", "text": "#e65100"},
    "❤️ Rojo": {"bg": "#ffebee", "border": "#ef5350", "text": "#b71c1c"}
}

COLOR_JARDINERIA_BASE = {"bg": "#e8f5e9", "border": "#2e7d32", "text": "#1b5e20"}

CAPILLAS_BASE = [
    "Barrio 1", "Barrio 2", "Barrio 3", "Barrio 4", 
    "Alberdi", "Güiraldes", "Puerto Tirol"
]

ROTACION_JARDINERIA = {
    0: [{"nombre": "Barrio 1", "inicio": "08:00", "fin": "16:00"}],
    1: [{"nombre": "Barrio 3", "inicio": "08:00", "fin": "16:00"}],
    2: [{"nombre": "Barrio 2", "inicio": "12:00", "fin": "16:00"}],
    3: [{"nombre": "Puerto Tirol", "inicio": "12:00", "fin": "16:00"}],
    4: [{"nombre": "Barrio 4", "inicio": "08:00", "fin": "16:00"}]
}

MESES_ESP = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

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
                    "title": f"🌱 Jardinería: {tarea['nombre']}",
                    "fecha": curr.strftime("%Y-%m-%d"),
                    "inicio": tarea['inicio'],
                    "fin": tarea['fin'],
                    "estilo": COLOR_JARDINERIA_BASE
                })
        curr += delta
    return eventos

# Estado global
if "eventos_calendar" not in st.session_state:
    st.session_state["eventos_calendar"] = generar_eventos_jardineria(2026)

if "fecha_seleccionada" not in st.session_state or not isinstance(st.session_state["fecha_seleccionada"], date):
    st.session_state["fecha_seleccionada"] = date(2026, 9, 10)

if "mes_visita" not in st.session_state:
    st.session_state["mes_visita"] = 9

if "anio_visita" not in st.session_state:
    st.session_state["anio_visita"] = 2026

if "estados_capillas" not in st.session_state:
    st.session_state["estados_capillas"] = {c: "Pendiente" for c in CAPILLAS_BASE}

# Estilos optimizados para celular
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    
    .mini-cal-card {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 15px;
    }
    
    .mini-cal-header {
        font-weight: 700;
        font-size: 1.1rem;
        text-align: center;
        color: #1e293b;
    }

    /* Ajustes compactos para los botones de números en celular */
    .stButton > button {
        padding: 4px 0px !important;
        font-size: 0.85rem !important;
        min-height: 38px !important;
    }
    </style>
""", unsafe_allow_html=True)

tab_cal, tab_capillas = st.tabs(["📅 Calendario", "⛪ Capillas y Estados"])

with tab_cal:
    # NAVEGADOR DE MES
    c_nav1, c_nav2, c_nav3 = st.columns([1, 2, 1])
    if c_nav1.button("◄", key="m_prev", use_container_width=True):
        if st.session_state["mes_visita"] == 1:
            st.session_state["mes_visita"] = 12
            st.session_state["anio_visita"] -= 1
        else:
            st.session_state["mes_visita"] -= 1
        st.rerun()
        
    c_nav2.markdown(f"<div class='mini-cal-header'>{MESES_ESP[st.session_state['mes_visita']-1]} {st.session_state['anio_visita']}</div>", unsafe_allow_html=True)
    
    if c_nav3.button("►", key="m_next", use_container_width=True):
        if st.session_state["mes_visita"] == 12:
            st.session_state["mes_visita"] = 1
            st.session_state["anio_visita"] += 1
        else:
            st.session_state["mes_visita"] += 1
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------ MINI CALENDARIO TÁCTIL PARA CELULAR ------------------
    st.markdown("<div class='mini-cal-card'>", unsafe_allow_html=True)
    
    cols_hdr = st.columns(7)
    for i, d in enumerate(["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]):
        cols_hdr[i].caption(f"**{d}**")

    cal_mat = calendar.monthcalendar(st.session_state["anio_visita"], st.session_state["mes_visita"])

    for semana in cal_mat:
        cols_sem = st.columns(7)
        semana_rot = [semana[-1]] + semana[:-1]
        for i, dia_num in enumerate(semana_rot):
            if dia_num != 0:
                fecha_iter = date(st.session_state["anio_visita"], st.session_state["mes_visita"], dia_num)
                f_str_iter = fecha_iter.strftime("%Y-%m-%d")
                
                es_sel = (fecha_iter == st.session_state["fecha_seleccionada"])
                
                # Revisa si hay tareas agendadas en esta fecha
                tiene_eventos = any(e.get("fecha") == f_str_iter for e in st.session_state["eventos_calendar"])
                
                # Etiqueta con punto verde si tiene tareas
                label_btn = f"• {dia_num}" if tiene_eventos else str(dia_num)
                tipo_btn = "primary" if es_sel else "secondary"
                
                if cols_sem[i].button(label_btn, key=f"btn_cel_{st.session_state['mes_visita']}_{dia_num}", type=tipo_btn, use_container_width=True):
                    st.session_state["fecha_seleccionada"] = fecha_iter
                    st.rerun()
            else:
                cols_sem[i].write("")
                
    st.markdown("</div>", unsafe_allow_html=True)

    # ------------------ DETALLE Y FORMULARIO (ABAJO DEL MINI CALENDARIO) ------------------
    f_obj = st.session_state["fecha_seleccionada"]
    if isinstance(f_obj, str):
        f_obj = datetime.strptime(f_obj, "%Y-%m-%d").date()
        st.session_state["fecha_seleccionada"] = f_obj

    f_str_sel = f_obj.strftime("%Y-%m-%d")

    st.subheader(f"📋 Tareas: {f_obj.strftime('%d/%m/%Y')}")
    evs_dia = [e for e in st.session_state["eventos_calendar"] if e.get("fecha") == f_str_sel]
    
    if evs_dia:
        for e in evs_dia:
            st.info(f"📌 **[{e.get('inicio', '08:00')} - {e.get('fin', '12:00')}]** {e.get('title', '')}")
    else:
        st.caption("No hay tareas registradas para esta fecha.")

    with st.expander("➕ Agregar Actividad para este día", expanded=False):
        with st.form("form_actividad_móvil", clear_on_submit=True):
            nombre_act = st.text_input("Título", placeholder="Ej: Limpieza Barrio 1")
            color_nom = st.selectbox("Color", options=list(PALETA_COLORES.keys()))
            
            c1, c2 = st.columns(2)
            h_in = c1.time_input("Inicio", value=datetime.strptime("08:00", "%H:%M").time())
            h_fi = c2.time_input("Fin", value=datetime.strptime("12:00", "%H:%M").time())
            
            if st.form_submit_button("Guardar Actividad", use_container_width=True, type="primary"):
                if nombre_act.strip():
                    estilo = PALETA_COLORES[color_nom]
                    st.session_state["eventos_calendar"].append({
                        "id": str(uuid.uuid4()),
                        "title": nombre_act,
                        "fecha": f_str_sel,
                        "inicio": h_in.strftime("%H:%M"),
                        "fin": h_fi.strftime("%H:%M"),
                        "estilo": estilo
                    })
                    st.success("¡Actividad registrada correctamente!")
                    st.rerun()

with tab_capillas:
    st.header("Control de Estado de Capillas")
    for c in CAPILLAS_BASE:
        estado_act = st.session_state["estados_capillas"][c]
        st.subheader(c)
        nuevo_est = st.selectbox(
            f"Estado para {c}:",
            ["Pendiente", "En Proceso", "Completado"],
            index=0 if estado_act == "Pendiente" else (1 if estado_act == "En Proceso" else 2),
            key=f"est_{c}"
        )
        st.session_state["estados_capillas"][c] = nuevo_est
        st.divider()
