import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date, timedelta
import uuid

# Configuración de página
st.set_page_config(
    page_title="Calendario Jardinería y Limpieza",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Paleta de colores
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

# Estilos CSS
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    
    .agenda-container {
        display: flex;
        flex-direction: column;
        gap: 0px;
        background: #ffffff;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        overflow: hidden;
    }
    
    .agenda-row {
        display: flex;
        flex-direction: row;
        align-items: stretch;
        min-height: 52px;
        border-bottom: 1px solid #f1f5f9;
    }
    
    .agenda-time {
        width: 60px;
        min-width: 60px;
        font-size: 0.75rem;
        font-weight: 700;
        color: #64748b;
        padding: 8px 4px;
        text-align: right;
        border-right: 1px solid #e2e8f0;
        background-color: #f8fafc;
    }
    
    .agenda-events {
        flex-grow: 1;
        padding: 4px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .event-card-mobile {
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 0.8rem;
        font-weight: 600;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        margin: 2px 0;
    }
    </style>
""", unsafe_allow_html=True)

tab_cal, tab_capillas = st.tabs(["📅 Agenda", "⛪ Capillas y Estados"])

with tab_cal:
    modo_vista = st.radio(
        "Modo de vista:",
        ["📱 Teléfono", "🖥️ Computadora"],
        horizontal=True
    )
    
    st.divider()

    # ------------------ VISTA TELÉFONO ------------------
    if "📱" in modo_vista:
        c1, c2, c3 = st.columns([1, 2, 1])
        if c1.button("◄ Ant.", use_container_width=True):
            st.session_state["fecha_seleccionada"] -= timedelta(days=1)
            st.session_state["mes_visita"] = st.session_state["fecha_seleccionada"].month
            st.session_state["anio_visita"] = st.session_state["fecha_seleccionada"].year
            st.rerun()
            
        f_actual = st.session_state["fecha_seleccionada"]
        dias_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        c2.markdown(f"<h4 style='text-align:center; margin:0;'>{dias_semana[f_actual.weekday()]} {f_actual.strftime('%d/%m/%Y')}</h4>", unsafe_allow_html=True)
        
        if c3.button("Sig. ►", use_container_width=True):
            st.session_state["fecha_seleccionada"] += timedelta(days=1)
            st.session_state["mes_visita"] = st.session_state["fecha_seleccionada"].month
            st.session_state["anio_visita"] = st.session_state["fecha_seleccionada"].year
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        f_str = f_actual.strftime("%Y-%m-%d")
        eventos_dia = [e for e in st.session_state["eventos_calendar"] if e.get("fecha") == f_str]

        # Agenda HTML horizontal por hora
        html_agenda = "<div class='agenda-container'>"
        for hora in range(7, 19):
            evs_hora = [e for e in eventos_dia if e.get("inicio", 8) <= hora < e.get("fin", 12)]
            
            html_agenda += f"<div class='agenda-row'><div class='agenda-time'>{hora:02d}:00</div><div class='agenda-events'>"
            
            if evs_hora:
                for e in evs_hora:
                    if e.get("inicio") == hora:
                        est = e.get("estilo", COLOR_JARDINERIA_BASE)
                        duracion = e.get("fin", 12) - e.get("inicio", 8)
                        html_agenda += f"""
                            <div class='event-card-mobile' style='background-color:{est["bg"]}; color:{est["text"]};'>
                                📌 {e.get("title")}<br>
                                <small>⏱️ {e.get("inicio"):02d}:00 - {e.get("fin"):02d}:00 ({duracion} hs)</small>
                            </div>
                        """
            html_agenda += "</div></div>"
            
        html_agenda += "</div>"
        st.markdown(html_agenda, unsafe_allow_html=True)

        st.divider()

        # ------------------ SECCIÓN DE GESTIÓN (EDITAR / ELIMINAR / AGREGAR) ------------------
        
        # 1. EDITAR / ELIMINAR TAREAS DEL DÍA
        if eventos_dia:
            with st.expander("✏️ Editar o Eliminar actividad del día", expanded=False):
                opciones_eventos = {f"{e['title']} ({e['inicio']}:00 - {e['fin']}:00 hs)": e for e in eventos_dia}
                seleccion_label = st.selectbox("Seleccioná la tarea a modificar:", list(opciones_eventos.keys()))
                
                evento_sel = opciones_eventos[seleccion_label]
                
                with st.form("form_editar_movil"):
                    nuevo_titulo = st.text_input("Título / Capilla", value=evento_sel["title"])
                    
                    # Buscar color actual en la paleta
                    color_def = "💚 Verde"
                    for k, v in PALETA_COLORES.items():
                        if v["bg"] == evento_sel.get("estilo", {}).get("bg"):
                            color_def = k
                            break
                    
                    nuevo_color = st.selectbox("Color", options=list(PALETA_COLORES.keys()), index=list(PALETA_COLORES.keys()).index(color_def))
                    
                    ce1, ce2 = st.columns(2)
                    n_inicio = ce1.number_input("Hora inicio (0-23)", min_value=0, max_value=23, value=int(evento_sel["inicio"]))
                    n_fin = ce2.number_input("Hora fin (0-23)", min_value=1, max_value=24, value=int(evento_sel["fin"]))
                    
                    c_btn1, c_btn2 = st.columns(2)
                    
                    btn_guardar = c_btn1.form_submit_button("💾 Guardar Cambios", use_container_width=True, type="primary")
                    btn_eliminar = c_btn2.form_submit_button("🗑️ Eliminar Tarea", use_container_width=True)
                    
                    if btn_guardar:
                        evento_sel["title"] = nuevo_titulo
                        evento_sel["inicio"] = int(n_inicio)
                        evento_sel["fin"] = int(n_fin)
                        evento_sel["estilo"] = PALETA_COLORES[nuevo_color]
                        st.success("¡Tarea actualizada!")
                        st.rerun()
                        
                    if btn_eliminar:
                        st.session_state["eventos_calendar"] = [e for e in st.session_state["eventos_calendar"] if e["id"] != evento_sel["id"]]
                        st.success("¡Tarea eliminada!")
                        st.rerun()

        # 2. AGREGAR NUEVA ACTIVIDAD
        with st.expander("➕ Agregar nueva actividad", expanded=False):
            with st.form("form_nuevo_movil", clear_on_submit=True):
                titulo = st.text_input("Título / Capilla", placeholder="Ej: Limpieza Barrio 1")
                color = st.selectbox("Color", options=list(PALETA_COLORES.keys()))
                
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

    # ------------------ VISTA COMPUTADORA ------------------
    else:
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
