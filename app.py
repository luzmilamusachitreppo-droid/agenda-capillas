import streamlit as st
import pandas as pd
from datetime import datetime, date

# Configuración de la página
st.set_page_config(
    page_title="Gestión de Jardines - Capillas",
    page_icon="🌿",
    layout="wide"
)

# Estilos visuales adaptados para tablet / mobile
st.markdown("""
    <style>
    .main { padding: 1rem; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; font-weight: bold; }
    .stSelectbox, .stTimeInput, .stDateInput { margin-bottom: 10px; }
    .capilla-card {
        background-color: #f0f4f1;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2e7d32;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌿 Agenda y Control de Trabajos - Capillas")

# Lista de capillas fijas
CAPILLAS = [
    "Güiraldes",
    "Puerto Vilelas",
    "Barrio Güiraldes",
    "Barrio Luz y Fuerza",
    "Capilla San José",
    "Capilla Santa Rosa",
    "Capilla San Cayetano"
]

# Inicialización del estado (Session State)
if "jornadas" not in st.session_state:
    st.session_state["jornadas"] = [
        {"fecha": str(date.today()), "capilla": "Güiraldes", "inicio": "08:00", "fin": "12:00", "estado": "Completado"},
        {"fecha": str(date.today()), "capilla": "Puerto Vilelas", "inicio": "13:00", "fin": "16:30", "estado": "En Proceso"}
    ]

if "tareas_extras" not in st.session_state:
    st.session_state["tareas_extras"] = [
        {"fecha": str(date.today()), "capilla": "Capilla San José", "tarea": "Poda de rosales y mantenimiento", "estado": "Pendiente"}
    ]

# Solapas principales del sistema
tab_cronograma, tab_registro, tab_extras = st.tabs([
    "📅 Calendario / Cronograma", 
    "✍️ Registrar Jornada", 
    "📌 Tareas Extras / Pendientes"
])

# ---------------------------------------------------------
# TAB 1: CALENDARIO Y CRONOGRAMA DE TAREAS
# ---------------------------------------------------------
with tab_cronograma:
    st.header("Cronograma General de Trabajos")
    
    col_filtro1, col_filtro2 = st.columns([1, 2])
    with col_filtro1:
        fecha_filtro = st.date_input("Filtrar por fecha:", date.today())
    
    st.subheader(f"Trabajos del día {fecha_filtro.strftime('%d/%m/%Y')}")
    
    # Filtrar jornadas para la fecha seleccionada
    jornadas_dia = [j for j in st.session_state["jornadas"] if j["fecha"] == str(fecha_filtro)]
    
    if jornadas_dia:
        df_jornadas = pd.DataFrame(jornadas_dia)
        df_jornadas.columns = ["Fecha", "Capilla", "Hora Inicio", "Hora Fin", "Estado"]
        st.dataframe(df_jornadas, use_container_width=True)
    else:
        st.info("No hay jornadas registradas para esta fecha.")

    st.divider()
    st.subheader("📋 Histórico Completo de Jornadas")
    if st.session_state["jornadas"]:
        df_todas = pd.DataFrame(st.session_state["jornadas"])
        df_todas.columns = ["Fecha", "Capilla", "Hora Inicio", "Hora Fin", "Estado"]
        st.dataframe(df_todas, use_container_width=True)
    else:
        st.write("Aún no hay datos cargados.")

# ---------------------------------------------------------
# TAB 2: REGISTRO DE JORNADA DIARIA
# ---------------------------------------------------------
with tab_registro:
    st.header("Cargar Horario y Estado de Capilla")
    
    with st.form("form_jornada"):
        col1, col2 = st.columns(2)
        with col1:
            fecha_reg = st.date_input("Fecha de Trabajo", date.today())
            capilla_reg = st.selectbox("Capilla / Lugar", CAPILLAS)
            estado_reg = st.selectbox("Estado del trabajo", ["Pendiente", "En Proceso", "Completado"])
        
        with col2:
            h_inicio = st.time_input("Hora de Inicio", datetime.strptime("08:00", "%H:%M").time())
            h_fin = st.time_input("Hora de Finalización (Manual)", datetime.strptime("12:00", "%H:%M").time())
        
        guardar = st.form_submit_button("💾 Guardar Jornada")
        if guardar:
            nueva_jornada = {
                "fecha": str(fecha_reg),
                "capilla": capilla_reg,
                "inicio": h_inicio.strftime("%H:%M"),
                "fin": h_fin.strftime("%H:%M"),
                "estado": estado_reg
            }
            st.session_state["jornadas"].append(nueva_jornada)
            st.success(f"¡Jornada en **{capilla_reg}** guardada correctamente!")

# ---------------------------------------------------------
# TAB 3: TAREAS EXTRAS Y PENDIENTES
# ---------------------------------------------------------
with tab_extras:
    st.header("Registro de Tareas Especiales / Extras")
    
    with st.form("form_extras"):
        f_extra = st.date_input("Fecha límite / programada", date.today())
        c_extra = st.selectbox("Capilla relacionada", CAPILLAS)
        desc_extra = st.text_area("Descripción de la tarea (ej. fertilización, poda alta, recambio de plantas)")
        
        guardar_extra = st.form_submit_button("➕ Agregar Tarea Extra")
        if guardar_extra:
            if desc_extra.strip() != "":
                nueva_tarea = {
                    "fecha": str(f_extra),
                    "capilla": c_extra,
                    "tarea": desc_extra,
                    "estado": "Pendiente"
                }
                st.session_state["tareas_extras"].append(nueva_tarea)
                st.success("Tarea extra agregada a la lista.")
            else:
                st.warning("Por favor escribí una descripción de la tarea.")

    st.subheader("📌 Tareas Pendientes")
    if st.session_state["tareas_extras"]:
        df_extras = pd.DataFrame(st.session_state["tareas_extras"])
        df_extras.columns = ["Fecha", "Capilla", "Tarea / Detalle", "Estado"]
        st.dataframe(df_extras, use_container_width=True)
    else:
        st.info("No hay tareas extras pendientes.")
        
