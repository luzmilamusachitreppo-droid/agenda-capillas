import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date, timedelta
import uuid

# Configuración de página con diseño ancho
st.set_page_config(
    page_title="Agenda Semanal - Jardinería y Limpieza",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Paleta de colores pastel estéticos
PALETA_COLORES = {
    "💚 Verde Pastel": {"bg": "#d1e7dd", "border": "#0f5132", "text": "#0f5132"},
    "💜 Violeta Pastel": {"bg": "#e2d9f3", "border": "#593196", "text": "#593196"},
    "🩷 Rosa Pastel": {"bg": "#f8d7da", "border": "#842029", "text": "#842029"},
    "🩵 Azul Pastel": {"bg": "#cff4fc", "border": "#055160", "text": "#055160"},
    "💛 Amarillo Pastel": {"bg": "#fff3cd", "border": "#664d03", "text": "#664d03"},
    "🧡 Naranja Pastel": {"bg": "#ffe5d0", "border": "#994d00", "text": "#994d00"}
}

COLOR_JARDINERIA_BASE = PALETA_COLORES["💚 Verde Pastel"]

CAPILLAS_BASE = [
    "Barrio 1", "Barrio 2", "Barrio 3", "Barrio 4", 
    "Alberdi", "Güiraldes", "Puerto Tirol"
]

ROTACION_JARDINERIA = {
    0: [{"nombre": "Barrio 1", "inicio": 8, "fin": 16}],
    1: [{"nombre": "Barrio 3", "inicio": 8, "fin": 16}],
    2: [{"nombre": "Barrio 2", "inicio": 12, "fin": 16}],
    3: [{"nombre": "Puerto Tirol", "inicio": 12, "fin": 16}],
    4: [{"nombre": "Barrio 4", "inicio": 8, "fin": 16}]
}

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
                    "title": f"Jardinería: {tarea['nombre']}",
                    "fecha": curr.strftime("%Y-%m-%d"),
                    "inicio": tarea['inicio'],
                    "fin": tarea['fin'],
                    "estilo": COLOR_JARDINERIA_BASE
                })
        curr += delta
    return eventos

# Inicializaciones en Session State
if "eventos_calendar" not in st.session_state:
    st.session_state["eventos_calendar"] = generar_eventos_jardineria(2026)

if "fecha_inicio_semana" not in st.session_state:
    hoy = date(2026, 9, 14)
    st.session_state["fecha_inicio_semana"] = hoy - timedelta(days=hoy.weekday())

if "estados_capillas" not in st.session_state:
    st.session_state["estados_capillas"] = {c: "Pendiente" for c in CAPILLAS_BASE}

# Garantizar que todas las capillas existan en la variable de estado
for c in CAPILLAS_BASE:
    if c not in st.session_state["estados_capillas"]:
        st.session_state["estados_capillas"][c] = "Pendiente"

# Estilos CSS
st.markdown("""
    <style>
    .stApp { background-color: #fafafa; }
    
    .week-table {
        width: 100%;
        border-collapse: collapse;
        background: #ffffff;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #e0e0e0;
    }
    
    .week-table th {
        background: #f4f5f7;
        padding: 12px 8px;
        font-weight: 700;
        font-size: 0.85rem;
        color: #4a5568;
        border-bottom: 2px solid #e2e8f0;
        border-right: 1px solid #edf2f7;
        text-align: center;
    }
    
    .week-table td {
        border-bottom: 1px solid #edf2f7;
        border-right: 1px solid #edf2f7;
        height: 48px;
        vertical-align: top;
        padding: 2px;
        width: 13.5%;
    }
    
    .time-col {
        width: 55px !important;
        background: #f8fafc;
        font-size: 0.75rem;
        font-weight: 600;
        color: #718096;
        text-align: center;
        vertical-align: middle !important;
    }
    
    .event-card {
        border-radius: 6px;
        padding: 4px 6px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 2px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border-left: 3px solid;
    }
    </style>
""", unsafe_allow_html=True)

tab_cal, tab_capillas = st.tabs(["📅 Agenda Semanal", "⛪ Capillas y Estados"])

with tab_cal:
    # Navegación semanal
    f_inicio = st.session_state["fecha_inicio_semana"]
    f_fin = f_inicio + timedelta(days=6)
    
    col_nav1, col_nav2, col_nav3 = st.columns([1, 3, 1])
    
    if col_nav1.button("◄ Semana Anterior", use_container_width=True):
        st.session_state["fecha_inicio_semana"] -= timedelta(days=7)
        st.rerun()
        
    col_nav2.markdown(
        f"<h3 style='text-align: center; margin:0;'>Semana del {f_inicio.strftime('%d/%m')} al {f_fin.strftime('%d/%m/%Y')}</h3>", 
        unsafe_allow_html=True
    )
    
    if col_nav3.button("Siguiente Semana ►", use_container_width=True):
        st.session_state["fecha_inicio_semana"] += timedelta(days=7)
        st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Días de la semana
    dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    fechas_semana = [f_inicio + timedelta(days=i) for i in range(7)]
    
    # Construcción de la tabla
    html_tabla = "<table class='week-table'><thead><tr><th class='time-col'>Hora</th>"
    
    for idx, f in enumerate(fechas_semana):
        html_tabla += f"<th>{dias_semana[idx]}<br><span style='font-weight:400; font-size:0.8rem; color:#718096;'>{f.strftime('%d/%m')}</span></th>"
    html_tabla += "</tr></thead><tbody>"
    
    # Horas de 07:00 a 18:00
    for hora in range(7, 19):
        html_tabla += f"<tr><td class='time-col'>{hora:02d}:00</td>"
        
        for f in fechas_semana:
            f_str = f.strftime("%Y-%m-%d")
            evs_dia = [e for e in st.session_state["eventos_calendar"] if e.get("fecha") == f_str and e.get("inicio", 8) <= hora < e.get("fin", 12)]
            
            html_tabla += "<td>"
            if evs_dia:
                for ev in evs_dia:
                    if ev.get("inicio") == hora:
                        est = ev.get("estilo", COLOR_JARDINERIA_BASE)
                        html_tabla += f"""
                            <div class='event-card' style='background-color:{est["bg"]}; border-color:{est["border"]}; color:{est["text"]};'>
                                📌 {ev.get("title")}<br>
                                <small>⏱️ {ev.get("inicio"):02d}:00 - {ev.get("fin"):02d}:00</small>
                            </div>
                        """
            html_tabla += "</td>" # Etiqueta corregida aquí
        html_tabla += "</tr>"
        
    html_tabla += "</tbody></table>"
    st.markdown(html_tabla, unsafe_allow_html=True)

    st.divider()

    # Panel inferior de Gestión
    col_add, col_edit = st.columns(2)
    
    with col_add:
        with st.expander("➕ Agregar nueva tarea", expanded=False):
            with st.form("form_nueva_tarea_semana", clear_on_submit=True):
                f_tarea = st.date_input("Fecha", value=f_inicio)
                titulo = st.text_input("Título / Capilla", placeholder="Ej: Jardinería Alberdi")
                color = st.selectbox("Color / Categoría", options=list(PALETA_COLORES.keys()))
                
                ch1, ch2 = st.columns(2)
                h_ini = ch1.number_input("Hora Inicio", min_value=0, max_value=23, value=8)
                h_fin = ch2.number_input("Hora Fin", min_value=1, max_value=24, value=12)
                
                if st.form_submit_button("Agendar Tarea", use_container_width=True, type="primary"):
                    if titulo.strip():
                        st.session_state["eventos_calendar"].append({
                            "id": str(uuid.uuid4()),
                            "title": titulo,
                            "fecha": f_tarea.strftime("%Y-%m-%d"),
                            "inicio": int(h_ini),
                            "fin": int(h_fin),
                            "estilo": PALETA_COLORES[color]
                        })
                        st.success("¡Tarea agendada!")
                        st.rerun()

    with col_edit:
        with st.expander("✏️ Editar o Eliminar tarea", expanded=False):
            fechas_str_semana = [f.strftime("%Y-%m-%d") for f in fechas_semana]
            evs_semana = [e for e in st.session_state["eventos_calendar"] if e.get("fecha") in fechas_str_semana]
            
            if evs_semana:
                opciones = {f"{e['fecha']} - {e['title']} ({e['inicio']}:00 hs)": e for e in evs_semana}
                sel_lbl = st.selectbox("Seleccioná la tarea a modificar:", list(opciones.keys()))
                ev_sel = opciones[sel_lbl]
                
                with st.form("form_editar_semana"):
                    n_titulo = st.text_input("Título", value=ev_sel["title"])
                    
                    c_def = list(PALETA_COLORES.keys())[0]
                    for k, v in PALETA_COLORES.items():
                        if v["bg"] == ev_sel.get("estilo", {}).get("bg"):
                            c_def = k
                            break
                            
                    n_color = st.selectbox("Color", options=list(PALETA_COLORES.keys()), index=list(PALETA_COLORES.keys()).index(c_def))
                    
                    ce1, ce2 = st.columns(2)
                    n_ini = ce1.number_input("Hora Inicio", min_value=0, max_value=23, value=int(ev_sel["inicio"]))
                    n_fn = ce2.number_input("Hora Fin", min_value=1, max_value=24, value=int(ev_sel["fin"]))
                    
                    b_guardar = st.form_submit_button("💾 Guardar Cambios", use_container_width=True, type="primary")
                    b_borrar = st.form_submit_button("🗑️ Eliminar Tarea", use_container_width=True)
                    
                    if b_guardar:
                        ev_sel["title"] = n_titulo
                        ev_sel["inicio"] = int(n_ini)
                        ev_sel["fin"] = int(n_fn)
                        ev_sel["estilo"] = PALETA_COLORES[n_color]
                        st.success("¡Tarea actualizada!")
                        st.rerun()
                        
                    if b_borrar:
                        st.session_state["eventos_calendar"] = [e for e in st.session_state["eventos_calendar"] if e["id"] != ev_sel["id"]]
                        st.success("¡Tarea eliminada!")
                        st.rerun()
            else:
                st.info("No hay tareas registradas para esta semana.")

with tab_capillas:
    st.header("Control de Estado de Capillas")
    for c in CAPILLAS_BASE:
        estado_act = st.session_state["estados_capillas"].get(c, "Pendiente")
        st.subheader(c)
        nuevo_est = st.selectbox(
            f"Estado para {c}:",
            ["Pendiente", "En Proceso", "Completado"],
            index=0 if estado_act == "Pendiente" else (1 if estado_act == "En Proceso" else 2),
            key=f"est_{c}"
        )
        st.session_state["estados_capillas"][c] = nuevo_est
        st.divider()
