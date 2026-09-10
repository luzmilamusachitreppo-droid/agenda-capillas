import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import calendar as cal_lib
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
    
    /* Botones del calendario en Celeste */
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
    
    /* Pestañas en Celeste */
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
    0: [{"nombre": "Barrio 1", "hora": "08:00", "tipo": "Jardinería"}],
    1: [{"nombre": "Barrio 3", "hora": "08:00", "tipo": "Jardinería"}],
    2: [
        {"nombre": "Alberdi", "hora": "08:00", "tipo": "Limpieza"},
        {"nombre": "Barrio 2", "hora": "12:00", "tipo": "Jardinería"}
    ],
    3: [
        {"nombre": "Güiraldes", "hora": "08:00", "tipo": "Limpieza"},
        {"nombre": "Puerto Tirol", "hora": "12:00", "tipo": "Jardinería"}
    ],
    4: [{"nombre": "Barrio 4", "hora": "08:00", "tipo": "Jardinería"}],
    5: [{"nombre": "Barrio 4 (Remates)", "hora": "08:00", "tipo": "Limpieza"}]
}

DIAS_ESP = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# Colores según tipo de trabajo
COLOR_JARDINERIA = "#2e7d32" # Verde
COLOR_LIMPIEZA = "#0288d1"   # Celeste

# Función para generar los eventos recurrentes en el mes visualizado
def generar_eventos_base(anio=2026):
    eventos = []
    fecha_inicio = date(anio, 1, 1)
    fecha_fin = date(anio, 12, 31)
    delta = timedelta(days=1)
    
    curr = fecha_inicio
    while curr <= fecha_fin:
        dia_num = curr.weekday()
        if dia_num in ROTACION_SEMANAL:
            for tarea in ROTACION_SEMANAL[dia_num]:
                bg_col = COLOR_LIMPIEZA if tarea["tipo"] == "Limpieza" else COLOR_JARDINERIA
                eventos.append({
                    "title": f"[{tarea['tipo']}] {tarea['nombre']}",
                    "start": f"{curr.strftime('%Y-%m-%d')}T{tarea['hora']}:00",
                    "backgroundColor": bg_col,
                    "borderColor": bg_col,
                    "textColor": "#ffffff"
                })
        curr += delta
    return eventos

if "eventos_calendar" not in st.session_state:
    st.session_state["eventos_calendar"] = generar_eventos_base(2026)

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
            "height": 700,
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

        st.write("<b>Tareas Agendadas:</b>", unsafe_allow_html=True)
        evs_dia = [e for e in st.session_state["eventos_calendar"] if e["start"].startswith(f_sel_str)]
        if evs_dia:
            for e in evs_dia:
                hora_show = e["start"].split("T")[1][:5] if "T" in e["start"] else "Todo el día"
                col_badge = "🟢" if e["backgroundColor"] == COLOR_JARDINERIA else "🔵"
                st.write(f"{col_badge} **[{hora_show}]** {e['title']}")
        else:
            st.caption("No hay actividades extras anotadas.")
            
        st.divider()
        st.markdown("### AGREGAR ACTIVIDAD EXTRA")
        with st.form("form_lateral_tarea"):
            tit_act = st.text_input("Título de la actividad")
            tipo_trabajo = st.radio("Rubro / Color", ["Jardinería (Verde)", "Limpieza (Celeste)"])
            hora_act = st.time_input("Hora de inicio", value=datetime.strptime("08:00", "%H:%M").time())
            
            btn_guardar_act = st.form_submit_button("+ Guardar en Fecha Seleccionada")
            if btn_guardar_act and tit_act.strip() != "":
                color_elegido = COLOR_JARDINERIA if "Jardinería" in tipo_trabajo else COLOR_LIMPIEZA
                tag_tipo = "Jardinería" if "Jardinería" in tipo_trabajo else "Limpieza"
                inicio_iso = f"{f_sel_str}T{hora_act.strftime('%H:%M:%00')}"
                
                st.session_state["eventos_calendar"].append({
                    "title": f"[{tag_tipo}] {tit_act}",
                    "start": inicio_iso,
                    "backgroundColor": color_elegido,
                    "borderColor": color_elegido,
                    "textColor": "#ffffff"
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
