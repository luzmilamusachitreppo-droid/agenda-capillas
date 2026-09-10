import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Agenda de Jardinería - Capillas",
    page_icon="🌿",
    layout="wide"
)

st.title("🌿 PLANIFICACIÓN DE CAPILLAS (LUNES A SÁBADO)")
st.caption("Acceso compartido para el equipo de jardinería")

# Inicialización de datos en sesión (para pruebas o conexión a nube)
if "capillas" not in st.session_state:
    st.session_state["capillas"] = [
        {"id": 1, "nombre": "Barrio 1", "dia": "Lunes", "obs": "Prioridad 2 - Turno Completo"},
        {"id": 2, "nombre": "Barrio 3", "dia": "Martes", "obs": "Prioridad 3 - Turno Completo"},
        {"id": 3, "nombre": "Alberdi", "dia": "Miércoles", "obs": "Prioridad 4 - Mañana (08-12hs)"},
        {"id": 4, "nombre": "Barrio 2", "dia": "Miércoles", "obs": "Prioridad 7 - Tarde (12-16hs)"},
        {"id": 5, "nombre": "Guiraldes", "dia": "Jueves", "obs": "Prioridad 5 - Mañana (08-12hs)"},
        {"id": 6, "nombre": "Puerto Tirol", "dia": "Jueves", "obs": "Prioridad 6 - Tarde (12-16hs)"},
        {"id": 7, "nombre": "Barrio 4", "dia": "Viernes", "obs": "Prioridad 1 - Turno Completo (2 patios)"},
        {"id": 8, "nombre": "Barrio 4 (Remates)", "dia": "Sábado", "obs": "Prioridad 1 - Remates Mañana"}
    ]

if "registro_jornadas" not in st.session_state:
    st.session_state["registro_jornadas"] = {}

# Pestañas principales
tab1, tab2 = st.tabs(["⛪ Cronograma de Capillas", "📅 Registro Diario y Tareas Extras"])

with tab1:
    st.info("📌 Recordatorio: La hora de finalización se ingresa manualmente al completar la jornada.")
    
    for cap in st.session_state["capillas"]:
        with st.expander(f"⛪ **{cap['nombre'].upper()}** — {cap['dia']} ({cap['obs']})", expanded=True):
            cols = st.columns(4)
            for sem in range(1, 5):
                clave = f"{cap['id']}_sem_{sem}"
                datos = st.session_state["registro_jornadas"].get(clave, {})
                
                with cols[sem - 1]:
                    st.markdown(f"### Semana {sem}")
                    
                    if datos:
                        st.write(f"📅 **Fecha:** {datos.get('fecha', '-')}")
                        st.write(f"⏰ **Inicio:** {datos.get('hora_inicio', '08:00')}")
                        st.write(f"🏁 **Fin real:** {datos.get('hora_fin', 'Pendiente')}")
                        st.write(f"📌 **Estado:** {datos.get('estado', 'Programada')}")
                    else:
                        st.write(" *Sin registrar*")
                    
                    # Formulario para actualizar la semana
                    with st.popover(f"✏️ Cargar/Editar Sem {sem}"):
                        fecha = st.date_input(f"Fecha (Capilla {cap['nombre']} - Sem {sem})", key=f"f_{clave}")
                        h_inicio = st.time_input("Hora de Inicio", value=datetime.strptime("08:00", "%H:%M").time(), key=f"hi_{clave}")
                        h_fin = st.text_input("Hora de Finalización Real", value=datos.get('hora_fin', ''), placeholder="ej: 11:30 hs o 15:45 hs", key=f"hf_{clave}")
                        estado = st.selectbox("Estado", ["Programada", "Realizada", "Pendiente", "Reprogramada"], key=f"est_{clave}")
                        
                        if st.button("💾 Guardar", key=f"btn_{clave}"):
                            st.session_state["registro_jornadas"][clave] = {
                                "fecha": fecha.strftime("%d/%m/%Y"),
                                "hora_inicio": h_inicio.strftime("%H:%M"),
                                "hora_fin": h_fin if h_fin else "En curso",
                                "estado": estado
                            }
                            st.success("¡Guardado!")
                            st.rerun()

with tab2:
    st.subheader("🚨 Registrar Tarea Extra / Salida del Día")
    
    col_a, col_b = st.columns(2)
    with col_a:
        f_extra = st.date_input("Fecha de la tarea extra")
        titulo_extra = st.text_input("Descripción de la tarea", placeholder="Ej: Comprar insumos / Salida especial")
    with col_b:
        h_extra = st.text_input("Horario aproximado", placeholder="Ej: 10:00 a 12:30 hs")
        obs_extra = st.text_area("Observaciones o notas")
        
    if st.button("➕ Agregar Tarea Extra"):
        if titulo_extra:
            if "extras" not in st.session_state:
                st.session_state["extras"] = []
            st.session_state["extras"].append({
                "fecha": f_extra.strftime("%d/%m/%Y"),
                "titulo": titulo_extra,
                "horario": h_extra,
                "obs": obs_extra
            })
            st.success("Tarea extra registrada correctamente.")
            st.rerun()

    st.divider()
    st.subheader("📋 Registro de Tareas Extras Cargadas")
    if "extras" in st.session_state and st.session_state["extras"]:
        df_extras = pd.DataFrame(st.session_state["extras"])
        st.dataframe(df_extras, use_container_width=True)
    else:
        st.write("No hay tareas extras registradas por el momento.")
        