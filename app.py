import streamlit as st
import pandas as pd
from datetime import datetime, date

# Configuración de página
st.set_page_config(
    page_title="Agenda de Jardinería - Capillas",
    page_icon="🌿",
    layout="wide"
)

# Estilos CSS
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #2e7d32; color: white; }
    .card-capilla {
        background-color: #f1f8e9;
        border-left: 6px solid #33691e;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌿 PLANIFICACIÓN DE CAPILLAS (LUNES A SÁBADO)")
st.caption("Acceso compartido para el equipo de jardinería")

# --- ESTRUCTURA FIJA DE ROTACIÓN DE CAPILLAS ---
ROTACION_SEMANAL = {
    "Lunes": [
        {"nombre": "Barrio 1", "obs": "Prioridad 2 - Turno Completo", "horario": "Turno Completo"}
    ],
    "Martes": [
        {"nombre": "Barrio 3", "obs": "Prioridad 3 - Turno Completo", "horario": "Turno Completo"}
    ],
    "Miércoles": [
        {"nombre": "Alberdi", "obs": "Prioridad 4", "horario": "Mañana (08:00 - 12:00 hs)"},
        {"nombre": "Barrio 2", "obs": "Prioridad 7", "horario": "Tarde (12:00 - 16:00 hs)"}
    ],
    "Jueves": [
        {"nombre": "Güiraldes", "obs": "Prioridad 5", "horario": "Mañana (08:00 - 12:00 hs)"},
        {"nombre": "Puerto Tirol", "obs": "Prioridad 6", "horario": "Tarde (12:00 - 16:00 hs)"}
    ],
    "Viernes": [
        {"nombre": "Barrio 4", "obs": "Prioridad 1 (2 patios)", "horario": "Turno Completo"}
    ],
    "Sábado": [
        {"nombre": "Barrio 4 (Remates)", "obs": "Prioridad 1 - Remates", "horario": "Mañana"}
    ],
    "Domingo": [
        {"nombre": "Sin programación fija", "obs": "Día de descanso / Mantenimiento opcional", "horario": "-"}
    ]
}

DIAS_ESPANOL = {
    "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
    "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
}

# --- INICIALIZACIÓN DEL ESTADO ---
if "registro_jornadas" not in st.session_state:
    st.session_state["registro_jornadas"] = []

if "tareas_calendario" not in st.session_state:
    st.session_state["tareas_calendario"] = []

# --- PESTAÑAS PRINCIPALES ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📅 Cronograma Semanal Fijo", 
    "📆 Calendario Interactivo / Agendar Tarea", 
    "✍️ Registrar Jornada Realizada",
    "📌 Tareas Extras y Pendientes"
])

# ---------------------------------------------------------
# TAB 1: ROTACIÓN SEMANAL FIJA
# ---------------------------------------------------------
with tab1:
    st.header("Rotación Semanal de Capillas")
    st.write("Horario y orden de prioridad establecido para el mantenimiento habitual:")
    
    cols = st.columns(3)
    dias_orden = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
    
    for idx, dia in enumerate(dias_orden):
        col_target = cols[idx % 3]
        with col_target:
            st.subheader(f"🗓️ {dia}")
            for cap in ROTACION_SEMANAL[dia]:
                st.markdown(f"""
                <div class="card-capilla">
                    <h4>{cap['nombre']}</h4>
                    <p><b>Horario:</b> {cap['horario']}<br>
                    <b>Detalle:</b> {cap['obs']}</p>
                </div>
                """, unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 2: CALENDARIO INTERACTIVO (CUALQUIER FECHA DEL AÑO)
# ---------------------------------------------------------
with tab2:
    st.header("Calendario General y Agendado de Tareas")
    
    col_cal1, col_cal2 = st.columns([1, 2])
    
    with col_cal1:
        fecha_sel = st.date_input("Seleccionar Fecha del Año:", date.today())
        nombre_dia_ing = fecha_sel.strftime("%A")
        nombre_dia_esp = DIAS_ESPANOL.get(nombre_dia_ing, "Lunes")
        
        st.info(f"**Día de la semana:** {nombre_dia_esp}")
        st.markdown("**Capillas programadas por rutina para este día:**")
        for c in ROTACION_SEMANAL.get(nombre_dia_esp, []):
            st.write(f"• **{c['nombre']}** ({c['horario']})")

    with col_cal2:
        st.subheader(f"📌 Tareas agendadas para el {fecha_sel.strftime('%d/%m/%Y')}")
        
        # Filtrar tareas del calendario para la fecha elegida
        tareas_fecha = [t for t in st.session_state["tareas_calendario"] if t["fecha"] == str(fecha_sel)]
        
        if tareas_fecha:
            for t in tareas_fecha:
                st.success(f"**[{t['capilla']}]** {t['descripcion']} (Estado: {t['estado']})")
        else:
            st.write("No hay tareas especiales agendadas para esta fecha.")
            
        st.divider()
        st.subheader("➕ Agregar Tarea / Evento a esta fecha")
        with st.form("form_nueva_tarea_fecha"):
            capilla_tarea = st.selectbox("Seleccionar Capilla:", [
                "Barrio 1", "Barrio 2", "Barrio 3", "Barrio 4", "Alberdi", "Güiraldes", "Puerto Tirol", "General / Otra"
            ])
            desc_tarea = st.text_input("Descripción de la tarea:")
            btn_agendar = st.form_submit_button("Agendar Tarea")
            
            if btn_agendar:
                if desc_tarea.strip() != "":
                    st.session_state["tareas_calendario"].append({
                        "fecha": str(fecha_sel),
                        "capilla": capilla_tarea,
                        "descripcion": desc_tarea,
                        "estado": "Pendiente"
                    })
                    st.success("¡Tarea agendada en la fecha seleccionada!")
                    st.rerun()

# ---------------------------------------------------------
# TAB 3: REGISTRO DE JORNADA REALIZADA
# ---------------------------------------------------------
with tab3:
    st.header("Registrar Horario de Trabajo Realizado")
    
    with st.form("form_registro_jornada"):
        col_reg1, col_reg2 = st.columns(2)
        with col_reg1:
            f_jornada = st.date_input("Fecha de Trabajo", date.today())
            c_jornada = st.selectbox("Capilla Trabajada", [
                "Barrio 1", "Barrio 2", "Barrio 3", "Barrio 4", "Alberdi", "Güiraldes", "Puerto Tirol"
            ])
            estado_jornada = st.selectbox("Estado", ["Completado", "Parcial / En Proceso", "Suspendido por Lluvia"])
        
        with col_reg2:
            h_in = st.time_input("Hora Entrada", datetime.strptime("08:00", "%H:%M").time())
            h_out = st.time_input("Hora Salida", datetime.strptime("12:00", "%H:%M").time())
            obs_jornada = st.text_area("Observaciones del trabajo realizado:")
            
        guardar_jornada = st.form_submit_button("Guardar Registro")
        if guardar_jornada:
            st.session_state["registro_jornadas"].append({
                "fecha": str(f_jornada),
                "capilla": c_jornada,
                "inicio": h_in.strftime("%H:%M"),
                "fin": h_out.strftime("%H:%M"),
                "estado": estado_jornada,
                "obs": obs_jornada
            })
            st.success("¡Jornada registrada con éxito!")

    st.divider()
    st.subheader("📋 Historial de Jornadas Registradas")
    if st.session_state["registro_jornadas"]:
        df_jornadas = pd.DataFrame(st.session_state["registro_jornadas"])
        st.dataframe(df_jornadas, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# TAB 4: TAREAS EXTRAS Y PENDIENTES GENERALES
# ---------------------------------------------------------
with tab4:
    st.header("Lista de Tareas Especiales / Extras Agendadas")
    if st.session_state["tareas_calendario"]:
        df_tareas = pd.DataFrame(st.session_state["tareas_calendario"])
        st.dataframe(df_tareas, use_container_width=True, hide_index=True)
    else:
        st.info("No hay tareas especiales agendadas en el calendario.")
