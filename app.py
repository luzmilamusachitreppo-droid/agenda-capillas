import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date, timedelta
import uuid

# Configuración de página
st.set_page_config(
    page_title="Agenda - Jardinería y Limpieza",
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

# Inicializaciones en Session State
if "eventos_calendar" not in st.session_state:
    st.session_state["eventos_calendar"] = generar_eventos_jardineria(2026)

if "fecha_seleccionada" not in st.session_state:
    st.session_state["fecha_seleccionada"] = date(2026, 9, 15)

if "mes_visita" not in st.session_state:
    st.session_state["mes_visita"] = 9

if "anio_visita" not in st.session_state:
    st.session_state["anio_visita"] = 2026

if "estados_capillas" not in st.session_state:
    st.session_state["estados_capillas"] = {c: "Pendiente" for c in CAPILLAS_BASE}

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
        padding: 14px 8px;
        font-weight: 700;
        font-size: 1.05rem;
        color: #2d3748;
        border-bottom: 2px solid #e2e8f0;
        border-right: 1px solid #edf2f7;
        text-align: center;
    }
    
    .week-table td {
        border-bottom: 1px solid #edf2f7;
        border-right: 1px solid #edf2f7;
        height: 55px;
        vertical-align: top;
        padding: 4px;
    }
    
    .time-col {
        width: 80px !important;
        background: #f8fafc;
        font-size: 0.88rem;
        font-weight: 700;
        color: #4a5568;
        text-align: center;
        vertical-align: middle !important;
    }
    
    .event-card {
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 2px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.06);
        border-left: 4px solid;
        line-height: 1.3;
    }

    @media (max-width: 768px) {
        .week-table th { font-size: 0.8rem; padding: 8px 2px; }
        .event-card { font-size: 0.75rem; padding: 4px 6px; }
    }
    </style>
""", unsafe_allow_html=True)

# Pestañas Principales
tab_cal, tab_capillas = st.tabs(["📅 Agenda", "⛪ Capillas y Estados"])

with tab_cal:
    col_v1, col_v2 = st.columns([1, 1])
    
    with col_v1:
        modo_vista = st.radio(
            "Dispositivo:",
            ["📱 Teléfono", "🖥️ Computadora"],
            horizontal=True
        )
        
    with col_v2:
        periodo_vista = st.radio(
            "Vista por:",
            ["Por Día", "Por Semana", "Por Mes"],
            horizontal=True,
            index=2
        )

    st.divider()

    f_act = st.session_state["fecha_seleccionada"]

    # 1. VISTA POR DÍA
    if periodo_vista == "Por Día":
        c_nav1, c_nav2, c_nav3 = st.columns([1, 2, 1])
        if c_nav1.button("◄ Día Ant.", use_container_width=True):
            st.session_state["fecha_seleccionada"] -= timedelta(days=1)
            st.rerun()
            
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        c_nav2.markdown(f"<h2 style='text-align:center; margin:0;'>{dias_semana[f_act.weekday()]} {f_act.strftime('%d/%m/%Y')}</h2>", unsafe_allow_html=True)
        
        if c_nav3.button("Día Sig. ►", use_container_width=True):
            st.session_state["fecha_seleccionada"] += timedelta(days=1)
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        f_str = f_act.strftime("%Y-%m-%d")

        html_dia = "<table class='week-table'><thead><tr><th class='time-col'>Hora</th><th>Actividades programadas</th></tr></thead><tbody>"
        for hora in range(7, 19):
            html_dia += f"<tr><td class='time-col'>{hora:02d}:00 hs</td><td>"
            evs_hora = [e for e in st.session_state["eventos_calendar"] if e.get("fecha") == f_str and e.get("inicio", 8) <= hora < e.get("fin", 12)]
            for ev in evs_hora:
                if ev.get("inicio") == hora:
                    est = ev.get("estilo", COLOR_JARDINERIA_BASE)
                    html_dia += f"""
                        <div class='event-card' style='background-color:{est["bg"]}; border-color:{est["border"]}; color:{est["text"]};'>
                            📌 {ev.get("title")}<br>
                            <small style='font-size: 0.8rem;'>⏱️ {ev.get("inicio"):02d}:00 - {ev.get("fin"):02d}:00 hs</small>
                        </div>
                    """
            html_dia += "</td></tr>"
        html_dia += "</tbody></table>"
        st.markdown(html_dia, unsafe_allow_html=True)

    # 2. VISTA POR SEMANA
    elif periodo_vista == "Por Semana":
        f_inicio = f_act - timedelta(days=f_act.weekday())
        f_fin = f_inicio + timedelta(days=6)
        
        c_nav1, c_nav2, c_nav3 = st.columns([1, 3, 1])
        if c_nav1.button("◄ Sem. Anterior", use_container_width=True):
            st.session_state["fecha_seleccionada"] -= timedelta(days=7)
            st.rerun()
            
        c_nav2.markdown(f"<h2 style='text-align:center; margin:0;'>Semana del {f_inicio.strftime('%d/%m')} al {f_fin.strftime('%d/%m/%Y')}</h2>", unsafe_allow_html=True)
        
        if c_nav3.button("Sem. Siguiente ►", use_container_width=True):
            st.session_state["fecha_seleccionada"] += timedelta(days=7)
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        dias_nombres = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        cant_dias = 5 if "📱" in modo_vista else 7
        fechas_semana = [f_inicio + timedelta(days=i) for i in range(cant_dias)]
        
        html_semana = "<table class='week-table'><thead><tr><th class='time-col'>Hora</th>"
        for idx, f in enumerate(fechas_semana):
            html_semana += f"<th>{dias_nombres[idx]}<br><span style='font-weight:400; font-size:0.85rem;'>{f.strftime('%d/%m')}</span></th>"
        html_semana += "</tr></thead><tbody>"
        
        for hora in range(7, 19):
            html_semana += f"<tr><td class='time-col'>{hora:02d}:00</td>"
            for f in fechas_semana:
                f_str = f.strftime("%Y-%m-%d")
                evs_dia = [e for e in st.session_state["eventos_calendar"] if e.get("fecha") == f_str and e.get("inicio", 8) <= hora < e.get("fin", 12)]
                html_semana += "<td>"
                if evs_dia:
                    for ev in evs_dia:
                        if ev.get("inicio") == hora:
                            est = ev.get("estilo", COLOR_JARDINERIA_BASE)
                            html_semana += f"""
                                <div class='event-card' style='background-color:{est["bg"]}; border-color:{est["border"]}; color:{est["text"]};'>
                                    📌 {ev.get("title")}<br>
                                    <small style='font-size: 0.8rem;'>⏱️ {ev.get("inicio"):02d}:00 - {ev.get("fin"):02d}:00</small>
                                </div>
                            """
                html_semana += "</td>"
            html_semana += "</tr>"
        html_semana += "</tbody></table>"
        st.markdown(html_semana, unsafe_allow_html=True)

    # 3. VISTA POR MES (CON AGENDA DIARIA DESPLEGADA POR HORAS ABAJO)
    elif periodo_vista == "Por Mes":
        c_nav1, c_nav2, c_nav3 = st.columns([1, 2, 1])
        if c_nav1.button("◄ Mes Anterior", use_container_width=True):
            if st.session_state["mes_visita"] == 1:
                st.session_state["mes_visita"] = 12
                st.session_state["anio_visita"] -= 1
            else:
                st.session_state["mes_visita"] -= 1
            st.rerun()
            
        c_nav2.markdown(f"<h2 style='text-align:center; margin:0;'>{MESES_ESP[st.session_state['mes_visita']-1]} {st.session_state['anio_visita']}</h2>", unsafe_allow_html=True)
        
        if c_nav3.button("Mes Siguiente ►", use_container_width=True):
            if st.session_state["mes_visita"] == 12:
                st.session_state["mes_visita"] = 1
                st.session_state["anio_visita"] += 1
            else:
                st.session_state["mes_visita"] += 1
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        headers = st.columns(7)
        dias_hdr = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
        for idx, h in enumerate(dias_hdr):
            headers[idx].markdown(f"### {h}")

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
                        
                        if st.button(lbl_dia, key=f"btn_m_{st.session_state['mes_visita']}_{dia_num}", type=btn_type, use_container_width=True):
                            st.session_state["fecha_seleccionada"] = f_curr
                            st.rerun()

                        evs = [e for e in st.session_state["eventos_calendar"] if e.get("fecha") == f_str]
                        for ev in evs:
                            est = ev.get("estilo", COLOR_JARDINERIA_BASE)
                            st.markdown(
                                f"""<div style='background-color:{est["bg"]}; color:{est["text"]}; border-left: 4px solid {est["border"]}; padding:4px 6px; border-radius:6px; font-size:0.85rem; font-weight:600; margin-top:3px;'>
                                {ev.get("inicio", 8)}:00 {ev.get("title", "")}
                                </div>""",
                                unsafe_allow_html=True
                            )
                    else:
                        st.write("")

        # AGENDA POR HORAS (TIPO GOOGLE CALENDAR) DEL DÍA PRESIONADO
        st.markdown("<br>", unsafe_allow_html=True)
        dias_nom = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        f_sel = st.session_state["fecha_seleccionada"]
        f_sel_str = f_sel.strftime("%Y-%m-%d")
        
        st.markdown(f"### 📅 Agenda por horas: {dias_nom[f_sel.weekday()]} {f_sel.strftime('%d/%m/%Y')}")
        
        html_dia_sel = "<table class='week-table'><thead><tr><th class='time-col'>Hora</th><th>Actividades y Compromisos</th></tr></thead><tbody>"
        for hora in range(7, 19):
            html_dia_sel += f"<tr><td class='time-col'>{hora:02d}:00 hs</td><td>"
            evs_hora = [e for e in st.session_state["eventos_calendar"] if e.get("fecha") == f_sel_str and e.get("inicio", 8) <= hora < e.get("fin", 12)]
            for ev in evs_hora:
                if ev.get("inicio") == hora:
                    est = ev.get("estilo", COLOR_JARDINERIA_BASE)
                    html_dia_sel += f"""
                        <div class='event-card' style='background-color:{est["bg"]}; border-color:{est["border"]}; color:{est["text"]};'>
                            📌 <b>{ev.get("title")}</b><br>
                            <small style='font-size: 0.8rem;'>⏱️ Horario: {ev.get("inicio"):02d}:00 a {ev.get("fin"):02d}:00 hs</small>
                        </div>
                    """
            html_dia_sel += "</td></tr>"
        html_dia_sel += "</tbody></table>"
        
        st.markdown(html_dia_sel, unsafe_allow_html=True)

    st.divider()

    # PANEL INFERIOR DE GESTIÓN
    col_add, col_edit = st.columns(2)
    
    with col_add:
        with st.expander("➕ Agregar nueva tarea", expanded=False):
            with st.form("form_nueva_tarea", clear_on_submit=True):
                f_tarea = st.date_input("Fecha", value=f_act)
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
            evs_disponibles = st.session_state["eventos_calendar"]
            
            if evs_disponibles:
                opciones = {f"{e['fecha']} - {e['title']} ({e['inicio']}:00 hs)": e for e in evs_disponibles}
                sel_lbl = st.selectbox("Seleccioná la tarea a modificar:", list(opciones.keys()))
                ev_sel = opciones[sel_lbl]
                
                with st.form("form_editar_tarea"):
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
                st.info("No hay tareas registradas.")

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
