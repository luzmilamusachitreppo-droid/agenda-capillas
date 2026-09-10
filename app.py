import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date, timedelta
import uuid

# Configuración de página
st.set_page_config(
    page_title="Calendario Jardinería y Limpieza",
    page_icon="🌿",
    layout="wide"
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

# Inicialización y validación de tipos en session_state
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

# Estilos CSS
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    
    .mini-cal-header {
        font-weight: bold; font-size: 1.1rem; text-align: center; margin-bottom: 10px; color: #1e293b;
    }
    
    .day-cell {
        background: white; border: 1px solid #e2e8f0; border-radius: 8px; min-height: 120px; padding: 6px;
    }
    .day-cell-today {
        background: #f0f9ff; border: 2px solid #0288d1;
    }
    .day-number {
        font-weight: bold; font-size: 0.9rem; color: #334155; margin-bottom: 4px;
    }
    
    .event-card {
        border-left: 4px solid; padding: 3px 6px; margin-bottom: 4px; border-radius: 4px; font-size: 0.75rem; font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

tab_cal, tab_capillas = st.tabs(["📅 Calendario", "⛪ Capillas y Estados"])

with tab_cal:
    col_left, col_center, col_right = st.columns([1, 2.8, 1.2])

    # ------------------ PANEL IZQUIERDO ------------------
    with col_left:
        st.markdown("<div style='background:white; padding:15px; border-radius:10px; border:1px solid #e2e8f0;'>", unsafe_allow_html=True)
        
        c_nav1, c_nav2, c_nav3 = st.columns([1, 3, 1])
        if c_nav1.button("◄", key="m_prev"):
            if st.session_state["mes_visita"] == 1:
                st.session_state["mes_visita"] = 12
                st.session_state["anio_visita"] -= 1
            else:
                st.session_state["mes_visita"] -= 1
            st.rerun()
            
        c_nav2.markdown(f"<div class='mini-cal-header'>{MESES_ESP[st.session_state['mes_visita']-1]} {st.session_state['anio_visita']}</div>", unsafe_allow_html=True)
        
        if c_nav3.button("►", key="m_next"):
            if st.session_state["mes_visita"] == 12:
                st.session_state["mes_visita"] = 1
                st.session_state["anio_visita"] += 1
            else:
                st.session_state["mes_visita"] += 1
            st.rerun()

        cal_mat = calendar.monthcalendar(st.session_state["anio_visita"], st.session_state["mes_visita"])
        
        cols_hdr = st.columns(7)
        for i, d in enumerate(["D", "L", "M", "M", "J", "V", "S"]):
            cols_hdr[i].caption(f"**{d}**")

        for semana in cal_mat:
            cols_sem = st.columns(7)
            semana_rot = [semana[-1]] + semana[:-1]
            for i, dia_num in enumerate(semana_rot):
                if dia_num != 0:
                    fecha_iter = date(st.session_state["anio_visita"], st.session_state["mes_visita"], dia_num)
                    es_sel = (fecha_iter == st.session_state["fecha_seleccionada"])
                    btn_label = f"**{dia_num}**" if es_sel else str(dia_num)
                    if cols_sem[i].button(btn_label, key=f"btn_mini_{st.session_state['mes_visita']}_{dia_num}"):
                        st.session_state["fecha_seleccionada"] = fecha_iter
                        st.rerun()
                else:
                    cols_sem[i].write("")
        st.markdown("</div>", unsafe_allow_html=True)

    # ------------------ PANEL CENTRAL ------------------
    with col_center:
        st.markdown(f"### {MESES_ESP[st.session_state['mes_visita']-1]} {st.session_state['anio_visita']}")
        
        headers = st.columns(7)
        dias_hdr = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
        for idx, h in enumerate(dias_hdr):
            headers[idx].markdown(f"**{h}**")

        cal_semanas = calendar.monthcalendar(st.session_state["anio_visita"], st.session_state["mes_visita"])
        
        for semana in cal_semanas:
            cols_dia = st.columns(7)
            semana_rot = [semana[-1]] + semana[:-1]
            for idx, dia_num in enumerate(semana_rot):
                with cols_dia[idx]:
                    if dia_num != 0:
                        f_str = f"{st.session_state['anio_visita']}-{st.session_state['mes_visita']:02d}-{dia_num:02d}"
                        f_curr = date(st.session_state["anio_visita"], st.session_state["mes_visita"], dia_num)
                        
                        es_hoy = (f_curr == st.session_state["fecha_seleccionada"])
                        clase_cell = "day-cell day-cell-today" if es_hoy else "day-cell"
                        
                        st.markdown(f"<div class='{clase_cell}'><div class='day-number'>{dia_num}</div>", unsafe_allow_html=True)
                        
                        evs = [e for e in st.session_state["eventos_calendar"] if e.get("fecha") == f_str]
                        for ev in evs:
                            est = ev.get("estilo", COLOR_JARDINERIA_BASE)
                            st.markdown(
                                f"""<div class='event-card' style='background-color:{est["bg"]}; border-color:{est["border"]}; color:{est["text"]};'>
                                {ev.get("inicio", "08:00")} {ev.get("title", "")}
                                </div>""",
                                unsafe_allow_html=True
                            )
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='day-cell' style='background:#f1f5f9;'></div>", unsafe_allow_html=True)

    # ------------------ PANEL DERECHO ------------------
    with col_right:
        f_obj = st.session_state["fecha_seleccionada"]
        
        # Validación de tipo fecha
        if isinstance(f_obj, str):
            f_obj = datetime.strptime(f_obj, "%Y-%m-%d").date()
            st.session_state["fecha_seleccionada"] = f_obj

        f_str_sel = f_obj.strftime("%Y-%m-%d")
        
        st.subheader(f"📋 {f_obj.strftime('%d/%m/%Y')}")
        st.caption("Día seleccionado")

        st.markdown("**Tareas para esta fecha:**")
        evs_dia = [e for e in st.session_state["eventos_calendar"] if e.get("fecha") == f_str_sel]
        
        if evs_dia:
            for e in evs_dia:
                st.markdown(f"📌 **[{e.get('inicio', '08:00')} - {e.get('fin', '12:00')}]** {e.get('title', '')}")
        else:
            st.caption("Sin tareas adicionales.")

        st.divider()
        st.markdown("### ➕ Agregar Actividad")
        
        with st.form("form_actividad_zoho", clear_on_submit=True):
            nombre_act = st.text_input("Título", placeholder="Ej: Limpieza Alberdi")
            color_nom = st.radio("Color", options=list(PALETA_COLORES.keys()), horizontal=True)
            
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
                    st.success("¡Agregado!")
                    st.rerun()

with tab_capillas:
    st.header("Control de Estado de Capillas")
    cols_cap = st.columns(2)
    for idx, c in enumerate(CAPILLAS_BASE):
        estado_act = st.session_state["estados_capillas"][c]
        with cols_cap[idx % 2]:
            st.subheader(c)
            nuevo_est = st.selectbox(
                f"Estado:",
                ["Pendiente", "En Proceso", "Completado"],
                index=0 if estado_act == "Pendiente" else (1 if estado_act == "En Proceso" else 2),
                key=f"est_{c}"
            )
            st.session_state["estados_capillas"][c] = nuevo_est
            st.divider()
