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

# Paleta de colores Pastel / Estados
PALETA_COLORES = {
    "💚 Verde - Confirmado": {"bg": "#4CAF50", "text": "#FFFFFF"},
    "💙 Azul - En proceso": {"bg": "#2196F3", "text": "#FFFFFF"},
    "💜 Violeta - Clase/Especial": {"bg": "#9C27B0", "text": "#FFFFFF"},
    "💛 Amarillo - Pendiente": {"bg": "#FFC107", "text": "#000000"},
    "❤️ Rojo - Faltante": {"bg": "#E91E63", "text": "#FFFFFF"}
}

CAPILLAS_DEFAULT = [
    "Barrio 1", "Barrio 2", "Barrio 3", "Barrio 4", 
    "Alberdi", "Güiraldes", "Puerto Tirol"
]

ROTACION_JARDINERIA = {
    0: [{"nombre": "Barrio 1", "inicio": 8, "fin": 9}],
    1: [{"nombre": "Barrio 3", "inicio": 8, "fin": 9}],
    2: [{"nombre": "Barrio 2", "inicio": 12, "fin": 13}],
    3: [{"nombre": "Puerto Tirol", "inicio": 12, "fin": 13}],
    4: [{"nombre": "Barrio 4", "inicio": 8, "fin": 9}]
}

MESES_ESP = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

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
                    "estilo": PALETA_COLORES["💚 Verde - Confirmado"],
                    "nota": "Atención programada"
                })
        curr += delta
    return eventos

# Estado de la app
if "lista_capillas" not in st.session_state:
    st.session_state["lista_capillas"] = CAPILLAS_DEFAULT.copy()

if "eventos_calendar" not in st.session_state:
    st.session_state["eventos_calendar"] = generar_eventos_jardineria(2026)

if "fecha_seleccionada" not in st.session_state:
    st.session_state["fecha_seleccionada"] = date(2026, 9, 15)

if "mes_visita" not in st.session_state:
    st.session_state["mes_visita"] = 9

if "anio_visita" not in st.session_state:
    st.session_state["anio_visita"] = 2026

if "estados_capillas" not in st.session_state:
    st.session_state["estados_capillas"] = {c: "Pendiente" for c in st.session_state["lista_capillas"]}

if "respuestas_checklist" not in st.session_state:
    st.session_state["respuestas_checklist"] = {}

if "comentarios_checklist" not in st.session_state:
    st.session_state["comentarios_checklist"] = {}

if "tareas_extra_checklist" not in st.session_state:
    st.session_state["tareas_extra_checklist"] = {}

# Estilos CSS para imitar la interfaz exacta de la imagen
st.markdown("""
    <style>
    .stApp { background-color: #f1f5f9; }
    
    /* Tarjeta del evento en la grilla horaria */
    .block-evento {
        border-radius: 8px;
        padding: 8px 10px;
        color: white;
        font-weight: 600;
        font-size: 0.85rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 4px;
    }
    
    /* Estilo del panel lateral derecho */
    .panel-derecho {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #e2e8f0;
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
# 1. PESTAÑA CALENDARIO (ESTILO EXACTO A LA IMAGEN)
# ==========================================
with tab_cal:
    # Layout de 2 columnas principales
    col_grilla, col_panel_derecho = st.columns([3.2, 1], gap="medium")

    f_sel = st.session_state["fecha_seleccionada"]
    f_sel_str = f_sel.strftime("%Y-%m-%d")

    # ----------------------------------------------------
    # COLUMNA IZQUIERDA: GRILLA SEMANAL DE AGENDA
    # ----------------------------------------------------
    with col_grilla:
        # Encabezado superior de la agenda (Hoy, Flechas, Mes y Año)
        c_act, c_nav_l, c_nav_r, c_titulo_m, c_filtros = st.columns([1, 0.4, 0.4, 3, 2])
        
        if c_act.button("Hoy", use_container_width=True):
            st.session_state["fecha_seleccionada"] = date.today()
            st.session_state["mes_visita"] = date.today().month
            st.session_state["anio_visita"] = date.today().year
            st.rerun()

        if c_nav_l.button("◄"):
            st.session_state["fecha_seleccionada"] -= timedelta(days=7)
            st.rerun()

        if c_nav_r.button("►"):
            st.session_state["fecha_seleccionada"] += timedelta(days=7)
            st.rerun()

        # Calcular días de la semana actual
        inicio_semana = f_sel - timedelta(days=f_sel.weekday())
        dias_semana = [inicio_semana + timedelta(days=i) for i in range(5)] # Lun a Vie
        
        c_titulo_m.markdown(f"### {MESES_ESP[f_sel.month-1]}. {f_sel.year}")

        st.divider()

        # Encabezados de días de la grilla (Seg, Ter, Qua, Qui, Sex / Lun, Mar, Mié, Jue, Vie)
        cols_hdr = st.columns([1] + [2]*5)
        cols_hdr[0].write("") # Espacio para columna de hora
        
        dias_nombres = ["Lun", "Mar", "Mié", "Jue", "Vie"]
        for idx, d_f in enumerate(dias_semana):
            es_hoy = (d_f == f_sel)
            txt_hdr = f"**{dias_nombres[idx]}**<br><span style='font-size:1.1rem; color:{'#00bcd4' if es_hoy else '#333'};'>{d_f.day}</span>"
            cols_hdr[idx+1].markdown(f"<div style='text-align:center;'>{txt_hdr}</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Filas por Horas (de 8:00 a 14:00 hs como en tu imagen)
        for hora in range(8, 15):
            cols_h = st.columns([1] + [2]*5)
            cols_h[0].markdown(f"<span style='color:#888; font-size:0.8rem;'>{hora:02d}:00</span>", unsafe_allow_html=True)
            
            for idx, d_f in enumerate(dias_semana):
                d_str = d_f.strftime("%Y-%m-%d")
                evs_h = [e for e in st.session_state["eventos_calendar"] if e.get("fecha") == d_str and e.get("inicio") == hora]
                
                with cols_h[idx+1]:
                    if evs_h:
                        for ev in evs_h:
                            bg_c = ev["estilo"]["bg"]
                            tx_c = ev["estilo"]["text"]
                            st.markdown(f"""
                                <div class="block-evento" style="background-color: {bg_c}; color: {tx_c};">
                                    {ev['title']}<br>
                                    <span style="font-size:0.75rem; opacity:0.9;">{ev['inicio']:02d}:00 - {ev['fin']:02d}:00</span>
                                </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.write("")

    # ----------------------------------------------------
    # COLUMNA DERECHA: PANEL DE ACCIONES, CALENDARIO MINI Y BLOC
    # ----------------------------------------------------
    with col_panel_derecho:
        # 1. Botón Principal + Nuevo Agendamiento
        with st.popover("➕ Nuevo agendamiento", use_container_width=True):
            st.markdown("#### Agendar Nueva Tarea")
            with st.form("form_nuevo_turno_panel", clear_on_submit=True):
                f_t = st.date_input("Fecha", value=f_sel)
                tit_t = st.text_input("Título / Capilla", placeholder="Ej: Alberto Augusto")
                nota_t = st.text_input("Detalle de atención", placeholder="Ej: Primera cita / Mantenimiento")
                cat_t = st.selectbox("Estado / Color", options=list(PALETA_COLORES.keys()))
                
                c_i, c_f = st.columns(2)
                h_i = c_i.number_input("Inicio", min_value=7, max_value=20, value=8)
                h_f = c_f.number_input("Fin", min_value=8, max_value=21, value=9)
                
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
                        st.success("¡Agendado!")
                        st.rerun()

        # 2. Buscador Rápido
        st.text_input("🔍 Buscar...", placeholder="Buscar tarea o persona...", label_visibility="collapsed")

        st.markdown("<br>", unsafe_allow_html=True)

        # 3. Mini Calendario Mensual
        m_col1, m_col2 = st.columns([3, 1])
        m_col1.markdown(f"**{MESES_ESP[st.session_state['mes_visita']-1].upper()} DE {st.session_state['anio_visita']}**")
        
        # Mini grilla del mes
        cal_m = calendar.monthcalendar(st.session_state["anio_visita"], st.session_state["mes_visita"])
        hdr_mini = st.columns(7)
        d_min = ["S", "T", "Q", "Q", "S", "S", "D"]
        for i, d_m in enumerate(d_min):
            hdr_mini[i].caption(d_m)

        for sem in cal_m:
            cols_m = st.columns(7)
            sem_rot = [sem[-1]] + sem[:-1]
            for i, d_num in enumerate(sem_rot):
                if d_num != 0:
                    f_m_curr = date(st.session_state["anio_visita"], st.session_state["mes_visita"], d_num)
                    es_sel = (f_m_curr == st.session_state["fecha_seleccionada"])
                    lbl = f"**{d_num}**" if es_sel else f"{d_num}"
                    
                    if cols_m[i].button(lbl, key=f"mini_{d_num}", use_container_width=True):
                        st.session_state["fecha_seleccionada"] = f_m_curr
                        st.rerun()

        st.divider()

        # 4. Bloc de Tareas y Resumen del Día Seleccionado
        evs_dia_sel = [e for e in st.session_state["eventos_calendar"] if e.get("fecha") == f_sel_str]
        st.markdown(f"### 📋 {len(evs_dia_sel)} Agendamientos")
        st.caption(f"Día: {f_sel.strftime('%d/%m/%Y')}")

        if not evs_dia_sel:
            st.info("Sin agendamientos para hoy.")
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
        capilla_trabajo = st.selectbox("⛪ Elegir Capilla:", st.session_state["lista_capillas"], key="chk_cap_sel")
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
