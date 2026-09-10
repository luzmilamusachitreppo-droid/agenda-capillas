import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date, timedelta
import uuid

st.set_page_config(
    page_title="Calendario Jardinería y Limpieza",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Paleta de colores vibrantes
PALETA_COLORES = {
    "💚 Verde": {"bg": "#2e7d32", "text": "#ffffff"},
    "💜 Violeta": {"bg": "#7b1fa2", "text": "#ffffff"},
    "🩷 Rosa": {"bg": "#d81b60", "text": "#ffffff"},
    "🩵 Azul": {"bg": "#1976d2", "text": "#ffffff"},
    "💛 Amarillo": {"bg": "#fbc02d", "text": "#000000"},
    "🧡 Naranja": {"bg": "#f57c00", "text": "#ffffff"},
    "❤️ Rojo": {"bg": "#c62828", "text": "#ffffff"}
}

COLOR_JARDINERIA_BASE = {"bg": "#2e7d32", "text": "#ffffff"}

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

MESES_ESP = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

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

if "eventos_calendar" not in st.session_state:
    st.session_state["eventos_calendar"] = generar_eventos_jardineria(2026)

if "fecha_seleccionada" not in st.session_state or not isinstance(st.session_state["fecha_seleccionada"], date):
    st.session_state["fecha_seleccionada"] = date(2026, 9, 10)

if "mes_visita" not in st.session_state:
    st.session_state["mes_visita"] = 9

if "anio_visita" not in st.session_state:
    st.session_state["anio_visita"] = 2026

if "estados_capillas" not in st.session_state:
    st.session_state["estados_capillas"] = {c: "Pendiente" for c in CAPILLAS_BASE}

# CSS Estilo Agenda por Horas
st.markdown("""
    <style>
    .stApp { background-color: #f1f5f9; }
    
    .time-slot {
        font-size: 0.75rem;
        font-weight: bold;
        color: #64748b;
        padding-top: 6px;
        text-align: right;
        padding-right: 8px;
    }
    
    .time-row {
        border-top: 1px solid #e2e8f0;
        min-height: 48px;
    }
    
    .event-block {
        border-radius: 6px;
        padding: 6px 10px;
        font-weight: 600;
        font-size: 0.8rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        margin-bottom: 4px;
    }
    </style>
""", unsafe_allow_html=True)

tab_cal, tab_capillas = st.tabs(["📅 Agenda", "⛪ Capillas y Estados"])

with tab_cal:
    modo_vista = st.radio(
        "Modo de vista:",
        ["📱 Teléfono (Agenda Diaria por Horas)", "🖥️ Computadora (Mes Completo)"],
        horizontal=True
    )
    
    st.divider()

    # ------------------ VISTA TELÉFONO (AGENDA POR HORAS) ------------------
    if "📱" in modo_vista:
        # Navegador de día a día
        c1, c2, c3 = st.columns([1, 2, 1])
        if c1.button("◄ Día ant.", use_container_width=True):
            st.session_state["fecha_seleccionada"] -= timedelta(days=1)
            st.session_state["mes_visita"] = st.session_state["fecha_seleccionada"].month
            st.session_state["anio_visita"] = st.session_state["fecha_seleccionada"].year
            st.rerun()
            
        f_actual = st.session_state["fecha_seleccionada"]
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        c2.markdown(f"<h4 style='text-align:center; margin:0;'>{dias_semana[f_actual.weekday()]} {f_actual.strftime('%d/%m/%Y')}</h4>", unsafe_allow_html=True)
        
        if c3.button("Día sig. ►", use_container_width=True):
            st.session_state["fecha_seleccionada"] += timedelta(days=1)
            st.session_state["mes_visita"] = st.session_state["fecha_seleccionada"].month
            st.session_state["anio_visita"] = st.session_state["fecha_seleccionada"].year
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Eventos para la fecha seleccionada
        f_str = f_actual.strftime("%Y-%m-%d")
        eventos_dia = [e for e in st.session_state["eventos_calendar"] if e.get("fecha") == f_str]

        # Grilla de Horarios (07:00 a 18:00)
        st.markdown("### ⏱️ Horarios del Día")
        
        for hora in range(7, 19):
            col_hora, col_evento = st.columns([1, 4])
            
            with col_hora:
                st.markdown(f"<div class='time-slot'>{hora:02d}:00</div>", unsafe_allow_html=True)
            
            with col_evento:
                # Filtrar eventos que cubran esta hora
                evs_hora = [e for e in eventos_dia if e.get("inicio", 8) <= hora < e.get("fin", 12)]
                
                if evs_hora:
                    for e in evs_hora:
                        # Dibujar el bloque de color sólo en la hora de inicio de la actividad
                        if e.get("inicio") == hora:
                            est = e.get("estilo", COLOR_JARDINERIA_BASE)
                            duracion = e.get("fin", 12) - e.get("inicio", 8)
                            st.markdown(
                                f"""<div class='event-block' style='background-color:{est["bg"]}; color:{est["text"]};'>
                                📌 <b>{e.get("title")}</b><br>
                                <small>⏱️ {e.get("inicio"):02d}:00 - {e.get("fin"):02d}:00 ({duracion} hs)</small>
                                </div>""",
                                unsafe_allow_html=True
                            )
                else:
                    st.markdown("<div class='time-row'></div>", unsafe_allow_html=True)

        st.divider()

        # Botón desplegable para agregar nueva actividad
        with st.expander("➕ Agregar nueva actividad a este día", expanded=False):
            with st.form("form_nuevo_movil", clear_on_submit=True):
                titulo = st.text_input("Título / Capilla", placeholder="Ej: Limpieza Barrio 1")
                color = st.selectbox("Color del bloque", options=list(PALETA_COLORES.keys()))
                
                ch1, ch2 = st.columns(2)
                h_inicio = ch1.number_input("Hora inicio (0-23)", min_value=0, max_value=23, value=8)
                h_fin = ch2.number_input("Hora fin (0-23)", min_value=1, max_value=24, value=12)
                
                if st.form_submit_button("Guardar en Agenda", use_container_width=True, type="primary"):
                    if titulo.strip():
                        st.session_state["eventos_calendar"].append({
                            "id": str(uuid.uuid4()),
                            "title": titulo,
                            "fecha": f_str,
                            "inicio": int(h_inicio),
                            "fin": int(h_fin),
                            "estilo": PALETA_COLORES[color]
                        })
                        st.success("¡Actividad agendada!")
                        st.rerun()

    # ------------------ VISTA COMPUTADORA (MES COMPLETO) ------------------
    else:
        # NAVEGADOR DE MES
        c_nav1, c_nav2, c_nav3 = st.columns([1, 2, 1])
        if c_nav1.button("◄ Mes anterior", key="m_prev", use_container_width=True):
            if st.session_state["mes_visita"] == 1:
                st.session_state["mes_visita"] = 12
                st.session_state["anio_visita"] -= 1
            else:
                st.session_state["mes_visita"] -= 1
            st.rerun()
            
        c_nav2.markdown(f"<h3 style='text-align:center;'>{MESES_ESP[st.session_state['mes_visita']-1]} {st.session_state['anio_visita']}</h3>", unsafe_allow_html=True)
        
        if c_nav3.button("Siguiente ►", key="m_next", use_container_width=True):
            if st.session_state["mes_visita"] == 12:
                st.session_state["mes_visita"] = 1
                st.session_state["anio_visita"] += 1
            else:
                st.session_state["mes_visita"] += 1
            st.rerun()

        headers = st.columns(7)
        dias_hdr = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
        for idx, h in enumerate(dias_hdr):
            headers[idx].markdown(f"**{h}**")

        cal_semanas = calendar.monthcalendar(st.session_state["anio_visita"], st.session_state["mes_visita"])
        
        for semana in cal_semanas:
            cols_dia = st.columns(7)
            semana_rot = [semana[-1]] + semana[:-1]
            for idx, dia_num in enumerate(semana_rot):
                with cols_dia[idx]:
                    if dia_num != 0:
                        f_str = f"{st.session_state['anio_visita']}-{st.session_state['mes_visita']:02d}-{dia_num:02d}"
                        f_curr = date(st.session_state["anio_visita"], st.session_state["mes_visita"], dia_num)
                        
                        es_hoy = (f_curr == st.session_state["fecha_seleccionada"])
                        
                        lbl_dia = f"★ {dia_num}" if es_hoy else f"{dia_num}"
                        btn_type = "primary" if es_hoy else "secondary"
                        
                        if st.button(lbl_dia, key=f"btn_pc_{st.session_state['mes_visita']}_{dia_num}", type=btn_type, use_container_width=True):
                            st.session_state["fecha_seleccionada"] = f_curr
                            st.rerun()

                        evs = [e for e in st.session_state["eventos_calendar"] if e.get("fecha") == f_str]
                        for ev in evs:
                            est = ev.get("estilo", COLOR_JARDINERIA_BASE)
                            st.markdown(
                                f"""<div style='background-color:{est["bg"]}; color:{est["text"]}; padding:3px 6px; border-radius:4px; font-size:0.75rem; margin-top:2px;'>
                                {ev.get("inicio", 8)}:00 {ev.get("title", "")}
                                </div>""",
                                unsafe_allow_html=True
                            )
                    else:
                        st.write("")

with tab_capillas:
    st.header("Control de Estado de Capillas")
    for c in CAPILLAS_BASE:
        estado_act = st.session_state["estados_capillas"][c]
        st.subheader(c)
        nuevo_est = st.selectbox(
            f"Estado para {c}:",
            ["Pendiente", "En Proceso", "Completado"],
            index=0 if estado_act == "Pendiente" else (1 if estado_act == "En Proceso" else 2),
            key=f"est_{c}"
        )
        st.session_state["estados_capillas"][c] = nuevo_est
        st.divider()
