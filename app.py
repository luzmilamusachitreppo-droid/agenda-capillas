import streamlit as st
import pandas as pd
from datetime import datetime, date
from streamlit_calendar import calendar

# Configuración de página
st.set_page_config(
    page_title="Calendario Jardinería y Limpieza",
    page_icon="🌿",
    layout="wide"
)

# Estilos CSS con paleta Verde y Celeste
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1e293b; }
    
    /* Cambiar botones del calendario (flechas, hoy, semana) a Celeste */
    .fc-button-primary {
        background-color: #0288d1 !important;
        border-color: #0288d1 !important;
        color: white !important;
    }
    .fc-button-primary:hover {
        background-color: #01579b !important;
        border-color: #01579b !important;
    }
    .fc-button-active {
        background-color: #01579b !important;
        border-color: #01579b !important;
    }
    
    /* Cambiar la pestaña seleccionada de Streamlit a Celeste */
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #0288d1 !important;
        border-bottom-color: #0288d1 !important;
    }

    .card-rotacion {
        background-color: #e0f7fa;
        border-left: 5px solid #0288d1;
        padding: 10px 15px;
        margin-bottom: 8px;
        border-radius: 6px;
    }
    .card-rotacion h4 { margin: 0; color: #006064; }
    
    .stForm .stButton > button {
        background-color: #2e7d32 !important;
        color: white !important;
        font-weight: bold !important;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌿 Calendario Jardinería y Limpieza")

CAPILLAS_INFO = [
    {"nombre": "Barrio 1", "dia": "LUNES", "horario": "Turno Completo"},
    {"nombre": "Barrio 3", "dia": "MARTES", "horario": "Turno Completo"},
    {"nombre": "Alberdi", "dia": "MIÉRCOLES", "horario": "Mañana (08:00 - 12:00 hs)"},
    {"nombre": "Barrio 2", "dia": "MIÉRCOLES", "horario": "Tarde (12:00 - 16:00 hs)"},
    {"nombre": "Güiraldes", "dia": "JUEVES", "horario": "Mañana (08:00 - 12:00 hs)"},
    {"nombre": "Puerto Tirol", "dia": "JUEVES", "horario": "Tarde (12:00 - 16:00 hs)"},
    {"nombre": "Barrio 4", "dia": "VIERNES / SÁBADO", "horario": "Turno Completo y Remates"}
]

ROTACION_SEMANAL = {
    "Lunes": [{"nombre": "Barrio 1", "horario": "Turno Completo"}],
    "Martes": [{"nombre": "Barrio 3", "horario": "Turno Completo"}],
    "Miércoles": [
        {"nombre": "Alberdi", "horario": "Mañana (08:00 - 12:00 hs)"},
        {"nombre": "Barrio 2", "horario": "Tarde (12:00 - 16:00 hs)"}
    ],
    "Jueves": [
        {"nombre": "Güiraldes", "horario": "Mañana (08:00 - 12:00 hs)"},
        {"nombre": "Puerto Tirol", "horario": "Tarde (12:00 - 16:00 hs)"}
    ],
    "Viernes": [{"nombre": "Barrio 4", "horario": "Turno Completo (2 patios)"}],
    "Sábado": [{"nombre": "Barrio 4 (Remates)", "horario": "Mañana"}]
}

DIAS_ESP = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

if "eventos_calendar" not in st.session_state:
    st.session_state["eventos_calendar"] = []

if "fecha_seleccionada" not in st.session_state:
    st.session_state["fecha_seleccionada"] = date.today().strftime("%Y-%m-%d")

if "estados_capillas" not in st.session_state:
    st.session_state["estados_capillas"] = {c["nombre"]: "Pendiente / Todavía no" for c in CAPILLAS_INFO}

tab_cal, tab_capillas = st.tabs(["📅 Calendario", "⛪ Capillas y Estados"])

with tab_cal:
    col_main_cal, col_side_note = st.columns([3, 1])
    
    with col_main_cal:
        calendar_options = {
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek"
            },
            "initialView": "dayGridMonth",
            "selectable": True,
            "editable": True,
            "height": 650,
            "locale": "es"
        }
        
        cal_data = calendar(
            events=st.session_state["eventos_calendar"],
            options=calendar_options,
            key="custom_fullcalendar"
        )
        
        if cal_data.get("dateClick"):
            st.session_state["fecha_seleccionada"] = cal_data["dateClick"]["date"].split("T")[0]
        elif cal_data.get("select"):
            st.session_state["fecha_seleccionada"] = cal_data["select"]["start"].split("T")[0]

    with col_side_note:
        f_sel_str = st.session_state["fecha_seleccionada"]
        f_obj = datetime.strptime(f_sel_str, "%Y-%m-%d").date()
        nombre_dia_esp = DIAS_ESP[f_obj.weekday()]
        
        st.subheader(f"📋 Trabajos: {f_obj.strftime('%d/%m/%Y')}")
        st.caption(f"Día: **{nombre_dia_esp}**")
        
        rot_dia = ROTACION_SEMANAL.get(nombre_dia_esp, [])
        if rot_dia:
            st.write("<b>Rutina Fija:</b>", unsafe_allow_html=True)
            for r in rot_dia:
                st.info(f"• **{r['nombre']}** ({r['horario']})")

        st.write("<b>Tareas Agendadas:</b>", unsafe_allow_html=True)
        evs_dia = [e for e in st.session_state["eventos_calendar"] if e["start"].startswith(f_sel_str)]
        if evs_dia:
            for e in evs_dia:
                hora_show = e["start"].split("T")[1] if "T" in e["start"] else "Todo el día"
                st.success(f"📌 **[{hora_show}]** {e['title']}")
        else:
            st.caption("No hay actividades extras anotadas.")
            
        st.divider()
        st.markdown("### AGREGAR ACTIVIDAD")
        with st.form("form_lateral_tarea"):
            tit_act = st.text_input("Título de la actividad")
            hora_act = st.time_input("Hora de inicio", value=datetime.strptime("08:00", "%H:%M").time())
            
            btn_guardar_act = st.form_submit_button("+ Guardar en Fecha Seleccionada")
            if btn_guardar_act and tit_act.strip() != "":
                inicio_iso = f"{f_sel_str}T{hora_act.strftime('%H:%M:%00')}"
                st.session_state["eventos_calendar"].append({
                    "title": tit_act,
                    "start": inicio_iso,
                    "backgroundColor": "#0288d1",
                    "borderColor": "#01579b"
                })
                st.success("Actividad guardada.")
                st.rerun()

with tab_capillas:
    st.header("Control de Estado de Capillas")
    st.write("Actualizá el estado del trabajo según el día asignado:")
    
    cols_cap = st.columns(2)
    for idx, c in enumerate(CAPILLAS_INFO):
        cap_nombre = c["nombre"]
        cap_dia = c["dia"]
        cap_horario = c["horario"]
        estado_act = st.session_state["estados_capillas"][cap_nombre]
        
        with cols_cap[idx % 2]:
            st.markdown(f"""
            <div class="card-rotacion">
                <h4>{cap_nombre} — <span style="font-size: 15px; color: #0288d1;">{cap_dia}</span></h4>
                <p style="margin:0; font-size: 13px; color: #555;"><b>Horario:</b> {cap_horario}</p>
            </div>
            """, unsafe_allow_html=True)
            
            nuevo_est = st.selectbox(
                f"Estado actual de {cap_nombre}:",
                ["Pendiente / Todavía no", "En Proceso", "Completado / Ya se hizo"],
                index=0 if "Pendiente" in estado_act else (1 if "Proceso" in estado_act else 2),
                key=f"est_{cap_nombre}"
            )
            st.session_state["estados_capillas"][cap_nombre] = nuevo_est
            st.divider()
