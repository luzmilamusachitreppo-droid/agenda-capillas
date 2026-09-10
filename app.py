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

# Paleta de colores
PALETA_COLORES = {
    "🩵 Celeste": "#29b6f6",
    "💚 Verde": "#4caf50",
    "💜 Violeta": "#ab47bc",
    "🩷 Rosa": "#ec407a",
    "💛 Amarillo": "#fbc02d",
    "🧡 Naranja": "#ffa726",
    "❤️ Rojo": "#ef5350"
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

    /* Resaltado de día seleccionado */
    .fc-highlight {
        background-color: #29b6f6 !important;
        opacity: 0.85 !important;
        outline: 3px solid #0288d1 !important;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.3) !important;
    }
    
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
                    "color": COLOR_JARDINERIA_BASE,
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
            "displayEventTime": False,
            "height": 720,
            "locale": "es"
        }
        
        # Key basado únicamente en la cantidad de eventos para re-renderizar solo al guardar
        cal_key = f"calendario_principal_{len(st.session_state['eventos_calendar'])}"
        
        cal_data = calendar(
            events=st.session_state["eventos_calendar"],
            options=calendar_options,
            key=cal_key
        )
        
        # Guardar la fecha del clic sin reconstruir el calendario
        if cal_data.get("dateClick"):
            st.session_state["fecha_seleccionada"] = cal_data["dateClick"]["date"].split("T")[0]
        elif cal_data.get("select"):
            st.session_state["fecha_seleccionada"] = cal_data["select"]["start"].split("T")[0]
        elif cal_data.get("eventClick"):
            st.session_state["fecha_seleccionada"] = cal_data["eventClick"]["event"]["start"].split("T")[0]

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
        
        with st.form("form_nueva_actividad", clear_on_submit=True):
            nombre_actividad = st.text_input("Título / Nombre de la actividad", placeholder="Ej: Limpieza Alberdi, Reunión...")
            
            color_nom = st.radio(
                "Seleccionar Color:",
                options=list(PALETA_COLORES.keys()),
                horizontal=True
            )
            hex_color_elegido = PALETA_COLORES[color_nom]

            c_h1, c_h2 = st.columns(2)
            with c_h1:
                h_in = st.time_input("Inicio", value=datetime.strptime("08:00", "%H:%M").time())
            with c_h2:
                h_fi = st.time_input("Fin", value=datetime.strptime("12:00", "%H:%M").time())
            
            btn_guardar = st.form_submit_button("Guardar Actividad", use_container_width=True)
            
            if btn_guardar:
                if nombre_actividad.strip() != "":
                    nuevo_evento = {
                        "title": nombre_actividad,
                        "start": f"{f_sel_str}T{h_in.strftime('%H:%M:00')}",
                        "end": f"{f_sel_str}T{h_fi.strftime('%H:%M:00')}",
                        "color": hex_color_elegido,
                        "backgroundColor": hex_color_elegido,
                        "borderColor": hex_color_elegido,
                        "textColor": "#ffffff"
                    }
                    st.session_state["eventos_calendar"].append(nuevo_evento)
                    st.success("Actividad agregada al calendario.")
                    st.rerun()
                else:
                    st.warning("Por favor ingresá un nombre para la actividad.")

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
