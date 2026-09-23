import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date, timedelta
import uuid

# Configuración de página
st.set_page_config(
    page_title="Agenda de Capillas",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Paleta de colores Pastel
PALETA_COLORES = {
    "💚 Verde - Confirmado": {"bg": "#d1e7dd", "border": "#0f5132", "text": "#0f5132"},
    "💙 Azul - En proceso": {"bg": "#cff4fc", "border": "#055160", "text": "#055160"},
    "💜 Violeta - Especial": {"bg": "#e2d9f3", "border": "#593196", "text": "#593196"},
    "💛 Amarillo - Pendiente": {"bg": "#fff3cd", "border": "#664d03", "text": "#664d03"},
    "🩷 Rosa - Alerta": {"bg": "#f8d7da", "border": "#842029", "text": "#842029"}
}

COLOR_DEFAULT = PALETA_COLORES["💚 Verde - Confirmado"]

CAPILLAS_DEFAULT = [
    "Barrio 1", "Barrio 2", "Barrio 3", "Barrio 4", 
    "Alberdi", "Güiraldes", "Puerto Tirol"
]

ROTACION_JARDINERIA = {
    0: [{"nombre": "Barrio 1", "inicio": 8, "fin": 12}],
    1: [{"nombre": "Barrio 3", "inicio": 8, "fin": 12}],
    2: [{"nombre": "Barrio 2", "inicio": 12, "fin": 16}],
    3: [{"nombre": "Puerto Tirol", "inicio": 12, "fin": 16}],
    4: [{"nombre": "Barrio 4", "inicio": 8, "fin": 12}]
}

MESES_ESP = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
MESES_ESP_CORTO = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

PDF_CHECKLIST_ITEMS = {
    "🚶 Pasillos": [
        "1. Limpieza de pisos: Barridos y desinfectados.",
        "2. Techos y paredes: Sin telarañas.",
        "3. Mobiliario: Limpios y firmes."
    ],
    "🚻 Baños": [
        "4. Piletas limpias.",
        "5. Insumos cargados.",
        "6. Cestos vacíos."
    ]
}

CHECKLIST_JARDINERIA_DEFAULT = [
    "Corte de césped general",
    "Bordeado y desmalezado",
    "Riego de plantas",
    "Limpieza de restos"
]

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
                    "estilo": COLOR_DEFAULT,
                    "nota": "Trabajo de jardinería programado"
                })
        curr += delta
    return eventos

# Estado de la app
if "lista_capillas" not in st.session_state:
    st.session_state["lista_capillas"] = CAPILLAS_DEFAULT.copy()

if "eventos_calendar" not in st.session_state:
    st.session_state["eventos_calendar"] = generar_eventos_jardineria(2026)

if "fecha_seleccionada" not in st.session_state:
    st.session_state["fecha_seleccionada"] = date(2026, 11, 1)

if "estados_capillas" not in st.session_state:
    st.session_state["estados_capillas"] = {c: "Pendiente" for c in st.session_state["lista_capillas"]}

if "respuestas_checklist" not in st.session_state:
    st.session_state["respuestas_checklist"] = {}

# Estilos CSS (Incluye adaptación exclusiva para celulares)
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    
    .block-evento {
        background-color: #d1e7dd;
        border-left: 3px solid #0f5132;
        color: #0f5132;
        border-radius: 5px;
        padding: 4px 6px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-bottom: 4px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        word-wrap: break-word;
    }
    
    .day-header {
        text-align: center;
        font-weight: bold;
        font-size: 0.88rem;
        color: #334155;
    }
    .day-num {
        font-size: 1.05rem;
        font-weight: bold;
        color: #0284c7;
    }
    .day-num-inactive {
        font-size: 1.05rem;
        font-weight: normal;
        color: #64748b;
    }
    .month-badge {
        font-size: 0.68rem;
        font-weight: bold;
        color: #0284c7;
        background-color: #e0f2fe;
        border-radius: 4px;
        padding: 1px 4px;
        margin-top: 2px;
        display: inline-block;
    }
    
    /* Línea divisoria fina de horarios */
    .hora-row-separator {
        border-bottom: 1px solid #e2e8f0;
        margin-top: 4px;
        margin-bottom: 8px;
    }

    /* ---------------------------------------------------
       ADAPTACIÓN EXCLUSIVA PARA VISTA EN CELULARES
    --------------------------------------------------- */
    @media (max-width: 768px) {
        /* Permite desplazamiento horizontal suave en la grilla sin romper el diseño */
        [data-testid="stHorizontalBlock"] {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }
        
        /* Ajuste de tamaño de fuente para pantallas reducidas */
        .block-evento {
            font-size: 0.70rem;
            padding: 3px 4px;
        }
        
        .day-header {
            font-size: 0.75rem;
        }
        
        .day-num, .day-num-inactive {
            font-size: 0.90rem;
        }

        /* Ajuste táctil conveniente para botones en dispositivos móviles */
        .stButton>button {
            padding: 4px 8px;
            font-size: 0.85rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# PESTAÑAS PRINCIPALES
tab_cal, tab_check, tab_capillas = st.tabs([
    "📅 1. Agenda Principal", 
    "📝 2. Checklist Digital", 
    "⛪ 3. Resumen de Capillas"
])

# ==========================================
# 1. PESTAÑA CALENDARIO
# ==========================================
with tab_cal:
    col_grilla, col_panel_derecho = st.columns([3.5, 1.1], gap="medium")

    f_sel = st.session_state["fecha_seleccionada"]
    f_sel_str = f_sel.strftime("%Y-%m-%d")

    # ----------------------------------------------------
    # COLUMNA IZQUIERDA: GRILLA SEMANAL DE AGENDA (7 DÍAS)
    # ----------------------------------------------------
    with col_grilla:
        # Encabezado con flechas a los lados del nombre del mes
        c_act, c_nav_l, c_titulo_m, c_nav_r, _ = st.columns([1, 0.4, 2.5, 0.4, 1])
        
        if c_act.button("Hoy", use_container_width=True):
            st.session_state["fecha_seleccionada"] = date.today()
            st.rerun()

        if c_nav_l.button("◄", use_container_width=True):
            st.session_state["fecha_seleccionada"] -= timedelta(days=7)
            st.rerun()

        # Días de la semana seleccionada (Lunes a Domingo)
        inicio_semana = f_sel - timedelta(days=f_sel.weekday())
        dias_semana = [inicio_semana + timedelta(days=i) for i in range(7)]
        
        # El mes principal de la semana se determina por el día Jueves (índice 3, mayoritario)
        mes_principal = dias_semana[3]
        titulo_semana = f"{MESES_ESP[mes_principal.month - 1]} {mes_principal.year}"

        c_titulo_m.markdown(f"<h3 style='margin:0; text-align:center;'>{titulo_semana}</h3>", unsafe_allow_html=True)

        if c_nav_r.button("►", use_container_width=True):
            st.session_state["fecha_seleccionada"] += timedelta(days=7)
            st.rerun()

        st.divider()

        # Encabezados de días (7 días)
        cols_hdr = st.columns([0.6] + [1.8]*7)
        cols_hdr[0].write("")
        
        dias_nombres = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        for idx, d_f in enumerate(dias_semana):
            es_hoy = (d_f == f_sel)
            clase_num = "day-num" if es_hoy else "day-num-inactive"
            
            badge_mes = ""
            if d_f.day == 1 or idx == 0:
                badge_mes = f"<br><span class='month-badge'>{MESES_ESP_CORTO[d_f.month-1]}</span>"

            cols_hdr[idx+1].markdown(
                f"<div class='day-header'>{dias_nombres[idx]}<br><span class='{clase_num}'>{d_f.day}</span>{badge_mes}</div>", 
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Filas por Horas (8:00 a 16:00 hs) con línea divisoria fina
        for hora in range(8, 17):
            cols_h = st.columns([0.6] + [1.8]*7)
            cols_h[0].markdown(f"<span style='color:#64748b; font-size:0.75rem; font-weight:600;'>{hora:02d}:00</span>", unsafe_allow_html=True)
            
            for idx, d_f in enumerate(dias_semana):
                d_str = d_f.strftime("%Y-%m-%d")
                evs_h = [e for e in st.session_state["eventos_calendar"] if e.get("fecha") == d_str and e.get("inicio") == hora]
                
                with cols_h[idx+1]:
                    if evs_h:
                        for ev in evs_h:
                            bg_c = ev.get("estilo", {}).get("bg", "#d1e7dd")
                            tx_c = ev.get("estilo", {}).get("text", "#0f5132")
                            border_c = ev.get("estilo", {}).get("border", "#0f5132")
                            
                            st.markdown(f"""
                                <div class="block-evento" style="background-color: {bg_c}; color: {tx_c}; border-left-color: {border_c};">
                                    {ev['title']}<br>
                                    <span style="font-size:0.7rem; opacity:0.85;">⏱️ {ev['inicio']:02d}:00 - {ev['fin']:02d}:00 hs</span>
                                </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.write("")
            
            # Línea fina divisoria entre renglones de hora
            st.markdown("<div class='hora-row-separator'></div>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # COLUMNA DERECHA: PANEL LATERAL
    # ----------------------------------------------------
    with col_panel_derecho:
        with st.popover("➕ Nueva tarea", use_container_width=True):
            st.markdown("#### Agendar Tarea")
            with st.form("form_nuevo_turno_top", clear_on_submit=True):
                f_t = st.date_input("Fecha", value=f_sel)
                tit_t = st.text_input("Título / Capilla", placeholder="Ej: Evento Parroquial")
                nota_t = st.text_input("Detalle", placeholder="Ej: Reunión especial")
                cat_t = st.selectbox("Categoría / Color", options=list(PALETA_COLORES.keys()))
                
                c_i, c_f = st.columns(2)
                h_i = c_i.number_input("Inicio", min_value=7, max_value=20, value=8)
                h_f = c_f.number_input("Fin", min_value=8, max_value=21, value=12)
                
                if st.form_submit_button("Guardar Turno", type="primary", use_container_width=True):
                    if tit_t.strip():
                        st.session_state["eventos_calendar"].append({
                            "id": str(uuid.uuid4()),
                            "title": tit_t.strip(),
                            "fecha": f_t.strftime("%Y-%m-%d"),
                            "inicio": int(h_i),
                            "fin": int(h_f),
                            "estilo": PALETA_COLORES[cat_t],
                            "nota": nota_t.strip()
                        })
                        st.session_state["fecha_seleccionada"] = f_t
                        st.success("¡Agendado!")
                        st.rerun()

        st.text_input("🔍 Buscar", placeholder="Buscar tarea...", label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)

        # Mini Calendario Mensual Sincronizado (basado en el mes principal de la semana)
        mes_panel = mes_principal
        st.markdown(f"**{MESES_ESP_CORTO[mes_panel.month-1].upper()} DE {mes_panel.year}**")
        
        cal_obj = calendar.Calendar(firstweekday=0) # 0 = Lunes
        cal_m = cal_obj.monthdayscalendar(mes_panel.year, mes_panel.month)
        
        hdr_m = st.columns(7)
        d_min = ["L", "M", "M", "J", "V", "S", "D"]
        for i, d_m in enumerate(d_min):
            hdr_m[i].markdown(f"<div style='text-align:center; font-size:0.75rem; font-weight:bold; color:#64748b;'>{d_m}</div>", unsafe_allow_html=True)

        for sem in cal_m:
            cols_m = st.columns(7)
            for i, d_num in enumerate(sem):
                if d_num != 0:
                    f_m_curr = date(mes_panel.year, mes_panel.month, d_num)
                    es_sel = (f_m_curr == st.session_state["fecha_seleccionada"])
                    
                    btn_t = "primary" if es_sel else "secondary"
                    if cols_m[i].button(str(d_num), key=f"m_btn_{mes_panel.month}_{d_num}", type=btn_t, use_container_width=True):
                        st.session_state["fecha_seleccionada"] = f_m_curr
                        st.rerun()
                else:
                    cols_m[i].write("")

        st.divider()

        # Bloc de Tareas Pendientes
        evs_dia_sel = [e for e in st.session_state["eventos_calendar"] if e.get("fecha") == f_sel_str]
        
        st.markdown(f"### 📋 Tareas pendientes ({len(evs_dia_sel)})")
        st.caption(f"Día: {f_sel.strftime('%d/%m/%Y')}")

        if not evs_dia_sel:
            st.info("Sin tareas para este día.")
        else:
            for ev in evs_dia_sel:
                with st.container():
                    c_det, c_del = st.columns([4, 1])
                    with c_det:
                        st.markdown(f"**{ev['title']}**")
                        st.caption(f"⏱️ {ev['inicio']:02d}:00 - {ev['fin']:02d}:00 hs")
                        if ev.get("nota"):
                            st.caption(f"💬 {ev['nota']}")
                    with c_del:
                        if st.button("🗑️", key=f"del_p_{ev['id']}", help="Eliminar"):
                            st.session_state["eventos_calendar"] = [e for e in st.session_state["eventos_calendar"] if e["id"] != ev["id"]]
                            st.rerun()
                    st.markdown("---")

# ==========================================
# 2. PESTAÑA CHECKLIST DIGITAL
# ==========================================
with tab_check:
    st.header("📝 Checklist Digital de Control")
    f_sel = st.session_state["fecha_seleccionada"]
    f_sel_str = f_sel.strftime("%Y-%m-%d")

    col_cap_sel, col_tipo_sel = st.columns(2)
    with col_cap_sel:
        capilla_trabajo = st.selectbox("Elegir Capilla:", st.session_state["lista_capillas"], key="chk_cap_sel")
    with col_tipo_sel:
        tipo_checklist = st.radio("Tipo:", ["🧹 Limpieza", "🌿 Jardinería"], horizontal=True, key="chk_tipo_sel")

    clave_base = f"{f_sel_str}_{capilla_trabajo}_{tipo_checklist}"
    if clave_base not in st.session_state["respuestas_checklist"]:
        st.session_state["respuestas_checklist"][clave_base] = {}

    st.markdown(f"### Revisión: **{capilla_trabajo}** ({f_sel.strftime('%d/%m/%Y')})")
    
    if "Limpieza" in tipo_checklist:
        for cat, items in PDF_CHECKLIST_ITEMS.items():
            with st.expander(cat, expanded=True):
                for item in items:
                    v_act = st.session_state["respuestas_checklist"][clave_base].get(item, False)
                    chk = st.checkbox(item, value=v_act, key=f"{clave_base}_{item}")
                    st.session_state["respuestas_checklist"][clave_base][item] = chk
    else:
        with st.expander("🌿 Jardinería", expanded=True):
            for item in CHECKLIST_JARDINERIA_DEFAULT:
                v_act = st.session_state["respuestas_checklist"][clave_base].get(item, False)
                chk = st.checkbox(item, value=v_act, key=f"{clave_base}_{item}")
                st.session_state["respuestas_checklist"][clave_base][item] = chk

# ==========================================
# 3. PESTAÑA RESUMEN DE CAPILLAS
# ==========================================
with tab_capillas:
    st.header("⛪ Resumen de Capillas")
    for c in st.session_state["lista_capillas"]:
        st.subheader(c)
        st.selectbox(f"Estado de {c}:", ["Pendiente", "En Proceso", "Completado"], key=f"est_{c}")
        st.divider()
