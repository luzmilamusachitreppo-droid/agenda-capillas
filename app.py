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

# Estilos en tema claro (blanco/verde)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1e293b; }
    
    /* Botones y formularios */
    .stButton>button { width: 100%; border-radius: 6px; background-color: #2e7d32; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #1b5e20; color: white; }
    
    /* Cuadrícula del Calendario */
    .cal-header { text-align: center; font-weight: bold; padding: 8px; background-color: #e2e8f0; color: #334155; border-radius: 4px; }
    .cal-day-box {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        min-height: 85px;
        padding: 6px;
        font-size: 13px;
        color: #0f172a;
    }
    .cal-day-box-selected {
        background-color: #e8f5e9 !important;
        border: 2px solid #2e7d32 !important;
    }
    .task-tag {
        background-color: #c8e6c9;
        color: #1b5e20;
        padding: 2px 4px;
        border-radius: 3px;
        font-size: 11px;
        margin-top: 3px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .card-rotacion {
        background-color: #f1f8e9;
        border-left: 5px solid #2e7d32;
        padding: 12px;
        margin-bottom: 10px;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌿 SISTEMA DE GESTIÓN Y AGENDA INTEGRAL")

# --- ROTACIÓN FIJA (SIN PRIORIDADES) ---
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
    st.session_state["estados_capillas"] = {
        "Barrio 1": "Pendiente / Todavía no",
        "Barrio 2": "Pendiente / Todavía no",
        "Barrio 3": "Pendiente / Todavía no",
        "Barrio 4": "Pendiente / Todavía no",
        "Alberdi": "Pendiente / Todavía no",
        "Güiraldes": "Pendiente / Todavía no",
        "Puerto Tirol": "Pendiente / Todavía no"
    }

# Pestañas superiores
tab_cal, tab_capillas = st.tabs(["📅 Calendario", "⛪ Capillas y Estados"])

# ---------------------------------------------------------
# TAB 1: CALENDARIO EN CUADRÍCULA Y ANOTADOR LATERAL
# ---------------------------------------------------------
with tab_cal:
    col_main_cal, col_side_note = st.columns([3, 1])
    
    # Navegación del mes
    with col_main_cal:
        fecha_hoy = date.today()
        mes_sel = st.selectbox("Seleccionar Mes / Año:", [date(2026, m, 1) for m in range(1, 13)], 
                              format_func=lambda d: d.strftime("%B %Y").upper(),
                              index=fecha_hoy.month - 1)
        
        # Encabezado de Días
        cols_dias = st.columns(7)
        dias_head = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        for idx, d in enumerate(dias_head):
            cols_dias[idx].markdown(f'<div class="cal-header">{d}</div>', unsafe_allow_html=True)
            
        # Matriz del mes
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
                        
                        is_sel = (dia_num == st.session_state["dia_click"])
                        css_box = "cal-day-box cal-day-box-selected" if is_sel else "cal-day-box"
                        
                        resumen_texto = ""
                        for t in tareas_dia[:2]:
                            resumen_texto += f'<div class="task-tag">• {t["titulo"]}</div>'
                        
                        st.markdown(f"""
                        <div class="{css_box}">
                            <b>{dia_num}</b>
                            {resumen_texto}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"Ver {dia_num}", key=f"btn_{fecha_str}"):
                            st.session_state["dia_click"] = dia_num
                            st.rerun()

    # Anotador lateral derecho
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
# TAB 2: CAPILLAS Y ESTADO (HECHO / NO HECHO)
# ---------------------------------------------------------
with tab_capillas:
    st.header("Control de Estado de Capillas")
    st.write("Actualizá el estado del trabajo según corresponda:")
    
    cols_cap = st.columns(2)
    for idx, (capilla, estado) in enumerate(st.session_state["estados_capillas"].items()):
        with cols_cap[idx % 2]:
            st.markdown(f'<div class="card-rotacion"><h4>{capilla}</h4></div>', unsafe_allow_html=True)
            nuevo_est = st.selectbox(
                f"Estado actual de {capilla}:",
                ["Pendiente / Todavía no", "En Proceso", "Completado / Ya se hizo"],
                index=0 if "Pendiente" in estado else (1 if "Proceso" in estado else 2),
                key=f"est_{capilla}"
            )
            st.session_state["estados_capillas"][capilla] = nuevo_est
            st.divider()
