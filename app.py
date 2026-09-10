import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date

# Configuración visual de la página
st.set_page_config(
    page_title="Sistema de Gestión y Agenda Integral",
    page_icon="🌿",
    layout="wide"
)

# Estilos CSS para hacer que el botón sea la tarjeta completa tipo Google Calendar
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1e293b; }
    
    /* Encabezado de los días de la semana */
    .cal-header { 
        text-align: center; 
        font-weight: bold; 
        padding: 8px; 
        background-color: #e2e8f0; 
        color: #334155; 
        border-radius: 4px;
        margin-bottom: 5px;
    }
    
    /* Convertir el botón en la tarjeta rectangular blanca */
    div[data-testid="column"] .stButton > button {
        width: 100% !important;
        height: 110px !important;
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 6px !important;
        color: #0f172a !important;
        text-align: left !important;
        vertical-align: top !important;
        padding: 8px 10px !important;
        font-size: 14px !important;
        font-weight: normal !important;
        box-shadow: none !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
        align-items: flex-start !important;
        white-space: pre-wrap !important;
    }

    /* Hover cuando pasás el mouse por arriba */
    div[data-testid="column"] .stButton > button:hover {
        border-color: #2e7d32 !important;
        background-color: #f1f8e9 !important;
    }

    /* TARJETA SELECCIONADA: Cuadro en Verde */
    .day-selected > button {
        background-color: #e8f5e9 !important;
        border: 2px solid #2e7d32 !important;
        font-weight: bold !important;
    }

    /* Botón verde del formulario lateral */
    .stForm .stButton > button {
        background-color: #2e7d32 !important;
        color: white !important;
        font-weight: bold !important;
        height: 42px !important;
        text-align: center !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Tarjeta verde de la pestaña Capillas */
    .card-rotacion {
        background-color: #f1f8e9;
        border-left: 5px solid #2e7d32;
        padding: 10px 15px;
        margin-bottom: 8px;
        border-radius: 6px;
    }
    .card-rotacion h4 {
        margin: 0;
        color: #1b5e20;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌿 SISTEMA DE GESTIÓN Y AGENDA INTEGRAL")

# --- ROTACIÓN CON DÍAS Y HORARIOS ---
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

# --- ESTADO EN SESIÓN ---
if "tareas_calendario" not in st.session_state:
    st.session_state["tareas_calendario"] = []

if "estados_capillas" not in st.session_state:
    st.session_state["estados_capillas"] = {c["nombre"]: "Pendiente / Todavía no" for c in CAPILLAS_INFO}

# Pestañas principales
tab_cal, tab_capillas = st.tabs(["📅 Calendario", "⛪ Capillas y Estados"])

# ---------------------------------------------------------
# TAB 1: CALENDARIO EN CUADRÍCULA Y ANOTADOR LATERAL
# ---------------------------------------------------------
with tab_cal:
    col_main_cal, col_side_note = st.columns([3, 1])
    
    with col_main_cal:
        fecha_hoy = date.today()
        mes_sel = st.selectbox("Seleccionar Mes / Año:", [date(2026, m, 1) for m in range(1, 13)], 
                              format_func=lambda d: d.strftime("%B %Y").upper(),
                              index=fecha_hoy.month - 1)
        
        # Encabezado días
        cols_dias = st.columns(7)
        dias_head = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        for idx, d in enumerate(dias_head):
            cols_dias[idx].markdown(f'<div class="cal-header">{d}</div>', unsafe_allow_html=True)
            
        cal_matriz = calendar.monthcalendar(mes_sel.year, mes_sel.month)
        
        if "dia_click" not in st.session_state:
            st.session_state["dia_click"] = fecha_hoy.day
            
        for semana in cal_matriz:
            cols_sem = st.columns(7)
            for i, dia_num in enumerate(semana):
                with cols_sem[i]:
                    if dia_num != 0:
                        fecha_str = f"{mes_sel.year}-{mes_sel.month:02d}-{dia_num:02d}"
                        tareas_dia = [t for t in st.session_state["tareas_calendario"] if t["fecha"] == fecha_str]
                        
                        # Texto dentro de la casilla blanca
                        label_btn = f"{dia_num}"
                        if tareas_dia:
                            for t in tareas_dia[:2]:
                                label_btn += f"\n• {t['titulo']}"
                            
                        is_sel = (dia_num == st.session_state["dia_click"])
                        
                        # Si está seleccionado, envolvemos el botón en una clase para pintarlo de verde
                        if is_sel:
                            st.markdown('<div class="day-selected">', unsafe_allow_html=True)
                            
                        if st.button(label_btn, key=f"btn_{fecha_str}"):
                            st.session_state["dia_click"] = dia_num
                            st.rerun()
                            
                        if is_sel:
                            st.markdown('</div>', unsafe_allow_html=True)

    # Anotador lateral
    with col_side_note:
        dia_actual = st.session_state["dia_click"]
        fecha_sel_str = f"{mes_sel.year}-{mes_sel.month:02d}-{dia_actual:02d}"
        fecha_obj = date(mes_sel.year, mes_sel.month, dia_actual)
        nombre_dia_esp = DIAS_ESP[fecha_obj.weekday()]
        
        st.subheader(f"📋 Trabajos: {fecha_obj.strftime('%d/%m/%Y')}")
        st.caption(f"Día: **{nombre_dia_esp}**")
        
        rot_dia = ROTACION_SEMANAL.get(nombre_dia_esp, [])
        if rot_dia:
            st.write("<b>Rutina Fija:</b>", unsafe_allow_html=True)
            for r in rot_dia:
                st.info(f"• **{r['nombre']}** ({r['horario']})")

        st.write("<b>Tareas Agendadas:</b>", unsafe_allow_html=True)
        tareas_actuales = [t for t in st.session_state["tareas_calendario"] if t["fecha"] == fecha_sel_str]
        if tareas_actuales:
            for t in tareas_actuales:
                st.success(f"📌 **[{t['hora']}]** {t['titulo']} ({t['tipo']})")
        else:
            st.caption("No hay actividades extras anotadas.")
            
        st.divider()
        st.markdown("### AGREGAR ACTIVIDAD")
        with st.form("form_lateral_tarea"):
            tit_act = st.text_input("Título de la actividad")
            hora_act = st.text_input("Hora (ej: 10:30)", "08:00")
            tipo_act = st.selectbox("Tipo", ["Mantenimiento", "Poda", "Limpieza Profunda", "Otro"])
            
            btn_guardar_act = st.form_submit_button("+ Guardar en Fecha Seleccionada")
            if btn_guardar_act and tit_act.strip() != "":
                st.session_state["tareas_calendario"].append({
                    "fecha": fecha_sel_str,
                    "titulo": tit_act,
                    "hora": hora_act,
                    "tipo": tipo_act
                })
                st.success("Actividad guardada.")
                st.rerun()

# ---------------------------------------------------------
# TAB 2: CAPILLAS Y ESTADO (CON DÍAS ORGANIZADOS)
# ---------------------------------------------------------
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
                <h4>{cap_nombre} — <span style="font-size: 15px; color: #2e7d32;">{cap_dia}</span></h4>
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
