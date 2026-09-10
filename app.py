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

COLOR_JARDINERIA_BASE = "#2e7d32"

# Paleta fija de botones con círculos (Incluye Celeste al inicio)
PALETA_COLORES_CIRCULOS = {
    "Celeste": "#29b6f6",
    "Verde": "#4caf50",
    "Violeta": "#ab47bc",
    "Rosa": "#ec407a",
    "Amarillo": "#fbc02d",
    "Naranja": "#ffa726",
    "Rojo": "#ef5350"
}

# Estilos CSS
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1e293b; }
    
    /* Botones de navegación del calendario */
    .fc-button-primary {
        background-color: #0288d1 !important;
        border-color: #0288d1 !important;
        color: white !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
    }
    .fc-button-primary:hover, .fc-button-active {
        background-color: #01579b !important;
        border-color: #01579b !important;
    }

    /* Tarjetas de eventos */
    .fc-timegrid-event, .fc-daygrid-event {
        border-radius: 6px !important;
        border: none !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15) !important;
        padding: 3px 6px !important;
        cursor: pointer !important;
    }
    
    .fc-daygrid-day {
        cursor: pointer !important;
    }

    /* RESALTADO INTENSO AL PRESIONAR/SELECCIONAR UN DÍA */
    .fc-highlight {
        background-color: #29b6f6 !important;
        opacity: 0.85 !important;
        outline: 3px solid #0288d1 !important;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.3) !important;
    }
    
    /* Hover en los días del calendario */
    .fc-daygrid-day:hover {
        background-color: #e0f7fa !important;
    }
    
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

    /* Botón de guardar RECTANGULAR */
    div.stButton > button.btn-guardar-rect {
        border-radius: 8px !important;
        width: 100% !important;
        height: 42px !important;
        background-color: #0288d1 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        font-size: 15px !important;
    }
    div.stButton > button.btn-guardar-rect:hover {
        background-color: #01579b !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌿 Calendario Jardinería y Limpieza")

CAPILLAS_BASE = [
    "Barrio 1", "Barrio 2", "Barrio 3", "Barrio 4", 
    "Alberdi", "Güiraldes", "Puerto Tirol"
]

# Rutina semanal fija de Jardinería
ROTACION_JARDINERIA = {
    0: [{"nombre": "Barrio 1", "inicio": "08:00", "fin": "16:00"}],
    1: [{"nombre": "Barrio 3", "inicio": "08:00", "fin": "16:00"}],
    2: [{"nombre": "Barrio 2", "inicio": "12:00", "fin": "16:00"}],
    3: [{"nombre": "Puerto Tirol", "inicio": "12:00", "fin": "16:00"}],
    4: [{"nombre": "Barrio 4", "inicio": "08:00", "fin": "16:00"}]
}

DIAS_ESP = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

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
                    "title": f"🌱 Jardinería: {tarea['nombre']}",
                    "start": f"{curr.strftime('%Y-%m-%d')}T{tarea['inicio']}:00",
                    "end": f"{curr.strftime('%Y-%m-%d')}T{tarea['fin']}:00",
                    "backgroundColor": COLOR_JARDINERIA_BASE,
                    "borderColor": "#1b5e20",
                    "textColor": "#ffffff"
                })
        curr += delta
    return eventos

if "eventos_calendar" not in st.session_state:
    st.session_state["eventos_calendar"] = generar_eventos_jardineria(2026)

if "fecha_seleccionada" not in st.session_state:
    st.session_state["fecha_seleccionada"] = date.today().strftime("%Y-%m-%d")

if "color_seleccionado" not in st.session_state:
    st.session_state["color_seleccionado"] = "#29b6f6" # Celeste por defecto

if "estados_capillas" not in st.session_state:
    st.session_state["estados_capillas"] = {c: "Pendiente" for c in CAPILLAS_BASE}

tab_cal, tab_capillas = st.tabs(["📅 Calendario", "⛪ Capillas y Estados"])

with tab_cal:
    col_main_cal, col_side_note = st.columns([3, 1])
    
    with col_main_cal:
        calendar_options = {
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek,timeGridDay"
            },
            "initialView": "dayGridMonth",
            "selectable": True,
            "selectMirror": True,
            "unselectAuto": False,
            "editable": True,
            "droppable": True,
            "displayEventTime": False, # Oculta el numero de hora (8 o 12) antes del titulo
            "height": 720,
            "locale": "es"
        }
        
        cal_data = calendar(
            events=st.session_state["eventos_calendar"],
            options=calendar_options,
            key="custom_fullcalendar"
        )
        
        nueva_fecha = None
        if cal_data.get("dateClick"):
            nueva_fecha = cal_data["dateClick"]["date"].split("T")[0]
        elif cal_data.get("select"):
            nueva_fecha = cal_data["select"]["start"].split("T")[0]
        elif cal_data.get("eventClick"):
            nueva_fecha = cal_data["eventClick"]["event"]["start"].split("T")[0]
            
        if nueva_fecha and nueva_fecha != st.session_state["fecha_seleccionada"]:
            st.session_state["fecha_seleccionada"] = nueva_fecha
            st.rerun()

    with col_side_note:
        f_sel_str = st.session_state["fecha_seleccionada"]
        f_obj = datetime.strptime(f_sel_str, "%Y-%m-%d").date()
        nombre_dia_esp = DIAS_ESP[f_obj.weekday()]
        
        st.subheader(f"📋 Día: {f_obj.strftime('%d/%m/%Y')}")
        st.caption(f"Día de la semana: **{nombre_dia_esp}**")

        st.write("<b>Tareas en esta fecha:</b>", unsafe_allow_html=True)
        evs_dia = [e for e in st.session_state["eventos_calendar"] if e["start"].startswith(f_sel_str)]
        if evs_dia:
            for e in evs_dia:
                h_in = e["start"].split("T")[1][:5] if "T" in e["start"] else "08:00"
                h_fi = e["end"].split("T")[1][:5] if "end" in e and "T" in e["end"] else "12:00"
                tit_clean = e['title'].replace('\n', ' - ')
                st.write(f"📌 **[{h_in} - {h_fi}]** {tit_clean}")
        else:
            st.caption("Sin tareas adicionales agendadas.")
            
        st.divider()
        st.markdown("### ➕ AGREGAR ACTIVIDAD")
        
        nombre_actividad = st.text_input("Título / Nombre de la actividad", placeholder="Ej: Limpieza Alberdi, Reunión...")
        
        st.write("**Seleccionar Color:**")
        cols_colores = st.columns(7)
        for idx, (nombre_c, hex_c) in enumerate(PALETA_COLORES_CIRCULOS.items()):
            with cols_colores[idx]:
                es_seleccionado = (st.session_state["color_seleccionado"] == hex_c)
                borde_estilo = "3px solid #000000" if es_seleccionado else "2px solid #ffffff"
                
                st.markdown(f"""
                <style>
                div[data-testid="stColumn"]:nth-child({idx+1}) button {{
                    border-radius: 50% !important;
                    width: 36px !important;
                    height: 36px !important;
                    padding: 0 !important;
                    background-color: {hex_c} !important;
                    border: {borde_estilo} !important;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
                }}
                </style>
                """, unsafe_allow_html=True)
                
                if st.button(" ", key=f"btn_col_{nombre_c}"):
                    st.session_state["color_seleccionado"] = hex_c
                    st.rerun()

        c_h1, c_h2 = st.columns(2)
        with c_h1:
            h_in = st.time_input("Inicio", value=datetime.strptime("08:00", "%H:%M").time())
        with c_h2:
            h_fi = st.time_input("Fin", value=datetime.strptime("12:00", "%H:%M").time())
        
        # Botón de guardar con clase específica
        if st.button("Guardar Actividad", key="btn_guardar_actividad", type="primary"):
            if nombre_actividad.strip() != "":
                st.session_state["eventos_calendar"].append({
                    "title": nombre_actividad,
                    "start": f"{f_sel_str}T{h_in.strftime('%H:%M:%00')}",
                    "end": f"{f_sel_str}T{h_fi.strftime('%H:%M:%00')}",
                    "backgroundColor": st.session_state["color_seleccionado"],
                    "borderColor": st.session_state["color_seleccionado"],
                    "textColor": "#ffffff"
                })
                st.success("Actividad agregada al calendario.")
                st.rerun()

with tab_capillas:
    st.header("Control de Estado de Capillas")
    st.write("Estado general de las distintas zonas / capillas:")
    
    cols_cap = st.columns(2)
    for idx, c in enumerate(CAPILLAS_BASE):
        estado_act = st.session_state["estados_capillas"][c]
        
        with cols_cap[idx % 2]:
            st.markdown(f"""
            <div class="card-rotacion">
                <h4>{c}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            nuevo_est = st.selectbox(
                f"Estado de {c}:",
                ["Pendiente", "En Proceso", "Completado"],
                index=0 if estado_act == "Pendiente" else (1 if estado_act == "En Proceso" else 2),
                key=f"est_{c}"
            )
            st.session_state["estados_capillas"][c] = nuevo_est
            st.divider()
