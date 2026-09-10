import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from streamlit_calendar import calendar

# Configuración de página
st.set_page_config(
    page_title="Calendario Jardinería y Limpieza",
    page_icon="🌿",
    layout="wide"
)

# Colores de la empresa
COLOR_JARDINERIA = "#4caf50"  # Verde brillante/suave estilo la imagen
COLOR_LIMPIEZA = "#29b6f6"    # Celeste brillante estilo la imagen

# Estilos CSS avanzados para replicar el look de la imagen
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1e293b; }
    
    /* Estilo de botones superiores */
    .fc-button-primary {
        background-color: #0288d1 !important;
        border-color: #0288d1 !important;
        color: white !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
    }
    .fc-button-primary:hover {
        background-color: #01579b !important;
        border-color: #01579b !important;
    }
    .fc-button-active {
        background-color: #01579b !important;
        border-color: #01579b !important;
    }

    /* Formato de los bloques de tarjetas (eventos) dentro del calendario */
    .fc-timegrid-event {
        border-radius: 6px !important;
        border: none !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08) !important;
        padding: 4px 6px !important;
    }
    .fc-v-event .fc-event-main {
        color: #1a252c !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }
    .fc-event-time {
        font-weight: normal !important;
        font-size: 11px !important;
        opacity: 0.85;
    }
    
    /* Pestañas */
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
    0: [{"nombre": "Barrio 1", "inicio": "08:00", "fin": "16:00", "tipo": "Jardinería"}],
    1: [{"nombre": "Barrio 3", "inicio": "08:00", "fin": "16:00", "tipo": "Jardinería"}],
    2: [
        {"nombre": "Alberdi", "inicio": "08:00", "fin": "12:00", "tipo": "Limpieza"},
        {"nombre": "Barrio 2", "inicio": "12:00", "fin": "16:00", "tipo": "Jardinería"}
    ],
    3: [
        {"nombre": "Güiraldes", "inicio": "08:00", "fin": "12:00", "tipo": "Limpieza"},
        {"nombre": "Puerto Tirol", "inicio": "12:00", "fin": "16:00", "tipo": "Jardinería"}
    ],
    4: [{"nombre": "Barrio 4", "inicio": "08:00", "fin": "16:00", "tipo": "Jardinería"}],
    5: [{"nombre": "Barrio 4 (Remates)", "inicio": "08:00", "fin": "12:00", "tipo": "Limpieza"}]
}

DIAS_ESP = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# Función para generar los bloques grandes en la grilla horaria
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
                border_left = "#0288d1" if tarea["tipo"] == "Limpieza" else "#1b5e20"
                eventos.append({
                    "title": f"{tarea['nombre']}\n{tarea['tipo']}",
                    "start": f"{curr.strftime('%Y-%m-%d')}T{tarea['inicio']}:00",
                    "end": f"{curr.strftime('%Y-%m-%d')}T{tarea['fin']}:00",
                    "backgroundColor": bg_col,
                    "borderColor": border_left,
                    "textColor": "#0f172a"
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
                "right": "timeGridWeek,timeGridDay,dayGridMonth"
            },
            "initialView": "timeGridWeek",  # Muestra la grilla semanal con horas (bloques grandes)
            "slotMinTime": "07:00:00",     # Arranca a las 7 AM
            "slotMaxTime": "19:00:00",     # Termina a las 7 PM
            "selectable": True,
            "editable": True,
            "allDaySlot": False,
            "height": 750,
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
                h_inicio = e["start"].split("T")[1][:5] if "T" in e["start"] else "08:00"
                h_fin = e["end"].split("T")[1][:5] if "end" in e and "T" in e["end"] else "12:00"
                col_badge = "🟢" if e["backgroundColor"] == COLOR_JARDINERIA else "🔵"
                tit_clean = e['title'].replace('\n', ' - ')
                st.write(f"{col_badge} **[{h_inicio} - {h_fin}]** {tit_clean}")
        else:
            st.caption("No hay actividades extras anotadas.")
            
        st.divider()
        st.markdown("### AGREGAR ACTIVIDAD EXTRA")
        with st.form("form_lateral_tarea"):
            tit_act = st.text_input("Título / Capilla")
            tipo_trabajo = st.radio("Rubro / Color", ["Jardinería (Verde)", "Limpieza (Celeste)"])
            
            c_h1, c_h2 = st.columns(2)
            with c_h1:
                hora_in = st.time_input("Inicio", value=datetime.strptime("08:00", "%H:%M").time())
            with c_h2:
                hora_fi = st.time_input("Fin", value=datetime.strptime("12:00", "%H:%M").time())
            
            btn_guardar_act = st.form_submit_button("+ Guardar en Fecha Seleccionada")
            if btn_guardar_act and tit_act.strip() != "":
                color_elegido = COLOR_JARDINERIA if "Jardinería" in tipo_trabajo else COLOR_LIMPIEZA
                border_left = "#1b5e20" if "Jardinería" in tipo_trabajo else "#0288d1"
                tag_tipo = "Jardinería" if "Jardinería" in tipo_trabajo else "Limpieza"
                
                inicio_iso = f"{f_sel_str}T{hora_in.strftime('%H:%M:%00')}"
                fin_iso = f"{f_sel_str}T{hora_fi.strftime('%H:%M:%00')}"
                
                st.session_state["eventos_calendar"].append({
                    "title": f"{tit_act}\n{tag_tipo}",
                    "start": inicio_iso,
                    "end": fin_iso,
                    "backgroundColor": color_elegido,
                    "borderColor": border_left,
                    "textColor": "#0f172a"
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
