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

# CHECKLIST COMPLETA Y DETALLADA CON TODAS LAS ACTIVIDADES FIJAS
PDF_CHECKLIST_ITEMS = {
    "🚶 Pasillos, Naves y Salón": [
        "1. Limpieza y barrido de pisos generales.",
        "2. Lavado y desinfección de pisos con producto adecuado.",
        "3. Limpieza de techos, tirantes y paredes (eliminación de telarañas).",
        "4. Sacudido y limpieza de bancos, sillas y mobiliario principal.",
        "5. Limpieza de vidrios, ventanas y marcos.",
        "6. Limpieza y sacudido de imágenes, altares y elementos litúrgicos.",
        "7. Vaciado y desinfección de papeleros y cestos de basura."
    ],
    "🚻 Baños y Sanitarios": [
        "1. Limpieza y desinfección profunda de inodoros y bidet.",
        "2. Limpieza de piletas, lavamanos y griferías.",
        "3. Limpieza y secado de espejos y azulejos.",
        "4. Reposición de insumos (papel higiénico, jabón, toallas de mano).",
        "5. Barrido, trapeado y desinfección de pisos de baño.",
        "6. Vaciado y desinfección de cestos de residuos."
    ],
    "🚪 Accesos y Fachada": [
        "1. Barrido de veredas, veredones y atrio de acceso.",
        "2. Limpieza de puertas principales, picaportes y rejas.",
        "3. Reorganización de afiches, carteleras e informativos.",
        "4. Control visual de luminarias exteriores e internas."
    ]
}

CHECKLIST_JARDINERIA_DEFAULT = [
    "1. Corte de césped en sectores generales y patios.",
    "2. Bordeado, orillado y desmalezado de muros/caminos.",
    "3. Riego de plantas, arbustos y jardines.",
    "4. Podado de mantenimiento de cercos vivos y ramas bajas.",
    "5. Juntado, embolsado y retiro de restos de poda y césped.",
    "6. Control e inspección general del estado del patio/jardín."
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

# ESTILOS BASE CSS
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    
    .block-evento {
        background-color: #d1e7dd;
        border-left: 4px solid #0f5132;
        color: #0f5132;
        border-radius: 6px;
        padding: 8px 10px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
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
    
    .hora-row-separator {
        border-bottom: 1px solid #e2e8f0;
        margin-top: 4px;
        margin-bottom: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# SELECTOR DE MODO DE VISTA
st.radio(
    "🖥️ Vista optimizada para:",
    ["💻 Computadora", "📱 Celular"],
    horizontal=True,
    key="selector_modo_dispositivo"
)

# PESTAÑAS PRINCIPALES
tab_cal, tab_check, tab_capillas = st.tabs([
    "📅 1. Agenda Principal", 
    "📝 2. Checklist Digital", 
    "⛪ 3. Resumen de Capillas"
])

# ==========================================
# VISTA COMPUTADORA (GRILLA COMPLETA)
# ==========================================
def render_agenda_desktop():
    f_sel = st.session_state["fecha_seleccionada"]
    f_sel_str = f_sel.strftime("%Y-%m-%d")

    col_grilla, col_panel_derecho = st.columns([3.5, 1.1], gap="medium")

    with col_grilla:
        c_act, c_nav_l, c_titulo_m, c_nav_r, _ = st.columns([1, 0.4, 2.5, 0.4, 1])
        
        if c_act.button("Hoy", use_container_width=True, key="btn_hoy_desk"):
            st.session_state["fecha_seleccionada"] = date.today()
            st.rerun()

        if c_nav_l.button("◄", use_container_width=True, key="btn_prev_desk"):
            st.session_state["fecha_seleccionada"] -= timedelta(days=7)
            st.rerun()

        inicio_semana = f_sel - timedelta(days=f_sel.weekday())
        dias_semana = [inicio_semana + timedelta(days=i) for i in range(7)]
        
        mes_principal = dias_semana[3]
        titulo_semana = f"{MESES_ESP[mes_principal.month - 1]} {mes_principal.year}"

        c_titulo_m.markdown(f"<h3 style='margin:0; text-align:center;'>{titulo_semana}</h3>", unsafe_allow_html=True)

        if c_nav_r.button("►", use_container_width=True, key="btn_next_desk"):
            st.session_state["fecha_seleccionada"] += timedelta(days=7)
            st.rerun()

        st.divider()

        # Encabezados de días
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

        # Horarios
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
                                <div class="block-evento" style="background-color: {bg_c}; color: {tx_c}; border-left-color: {border_c}; font-size:0.75rem;">
                                    {ev['title']}<br>
                                    <span style="font-size:0.68rem; opacity:0.85;">⏱️ {ev['inicio']:02d}:00 - {ev['fin']:02d}:00 hs</span>
                                </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.write("")
            
            st.markdown("<div class='hora-row-separator'></div>", unsafe_allow_html=True)

    with col_panel_derecho:
        with st.popover("➕ Nueva tarea", use_container_width=True):
            st.markdown("#### Agendar Tarea")
            with st.form("form_nuevo_turno_desk", clear_on_submit=True):
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

        # Mini Calendario Mensual
        mes_panel = mes_principal
        st.markdown(f"**{MESES_ESP_CORTO[mes_panel.month-1].upper()} DE {mes_panel.year}**")
        
        cal_obj = calendar.Calendar(firstweekday=0)
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
                    if cols_m[i].button(str(d_num), key=f"m_btn_{mes_panel.month}_{d_num}_desk", type=btn_t, use_container_width=True):
                        st.session_state["fecha_seleccionada"] = f_m_curr
                        st.rerun()
                else:
                    cols_m[i].write("")

        st.divider()

        # Tareas del Día
        evs_dia_sel = [e for e in st.session_state["eventos_calendar"] if e.get("fecha") == f_sel_str]
        st.markdown(f"### 📋 Tareas pendientes ({len(evs_dia_sel)})")
        st.caption(f"Día: {f_sel.strftime('%d/%m/%Y')}")

        if not evs_dia_sel:
            st.info("Sin tareas para este día.")
        else:
            for ev in evs_dia_sel:
                c_det, c_del = st.columns([4, 1])
                with c_det:
                    st.markdown(f"**{ev['title']}**")
                    st.caption(f"⏱️ {ev['inicio']:02d}:00 - {ev['fin']:02d}:00 hs")
                with c_del:
                    if st.button("🗑️", key=f"del_desk_{ev['id']}", help="Eliminar"):
                        st.session_state["eventos_calendar"] = [e for e in st.session_state["eventos_calendar"] if e["id"] != ev["id"]]
                        st.rerun()

# ==========================================
# VISTA CELULAR (ADAPTADA Y LIMPIA)
# ==========================================
def render_agenda_mobile():
    f_sel = st.session_state["fecha_seleccionada"]
    f_sel_str = f_sel.strftime("%Y-%m-%d")

    st.markdown("### 📱 Agenda Diaria")
    
    c_prev, c_fecha, c_next = st.columns([1, 3, 1])
    if c_prev.button("◄", use_container_width=True, key="m_prev"):
        st.session_state["fecha_seleccionada"] -= timedelta(days=1)
        st.rerun()
    
    with c_fecha:
        nueva_f = st.date_input("Seleccionar Fecha", value=f_sel, label_visibility="collapsed", key="m_date_pick")
        if nueva_f != f_sel:
            st.session_state["fecha_seleccionada"] = nueva_f
            st.rerun()

    if c_next.button("►", use_container_width=True, key="m_next"):
        st.session_state["fecha_seleccionada"] += timedelta(days=1)
        st.rerun()

    if st.button("📍 Ir a Hoy", use_container_width=True, key="m_hoy"):
        st.session_state["fecha_seleccionada"] = date.today()
        st.rerun()

    st.markdown(f"#### 📅 {f_sel.strftime('%d/%m/%Y')}")

    with st.popover("➕ Agregar Tarea en este Día", use_container_width=True):
        with st.form("form_mob_add", clear_on_submit=True):
            tit_t = st.text_input("Título / Capilla", placeholder="Ej: Jardinería Barrio 1")
            nota_t = st.text_input("Detalle", placeholder="Notas de la tarea")
            cat_t = st.selectbox("Categoría", options=list(PALETA_COLORES.keys()))
            
            c1, c2 = st.columns(2)
            h_i = c1.number_input("Hora Inicio", min_value=7, max_value=20, value=8)
            h_f = c2.number_input("Hora Fin", min_value=8, max_value=21, value=12)
            
            if st.form_submit_button("Guardar Tarea", type="primary", use_container_width=True):
                if tit_t.strip():
                    st.session_state["eventos_calendar"].append({
                        "id": str(uuid.uuid4()),
                        "title": tit_t.strip(),
                        "fecha": f_sel_str,
                        "inicio": int(h_i),
                        "fin": int(h_f),
                        "estilo": PALETA_COLORES[cat_t],
                        "nota": nota_t.strip()
                    })
                    st.success("¡Agregado!")
                    st.rerun()

    st.divider()

    evs_dia = [e for e in st.session_state["eventos_calendar"] if e.get("fecha") == f_sel_str]
    evs_dia = sorted(evs_dia, key=lambda x: x["inicio"])

    if not evs_dia:
        st.info("No hay actividades registradas para esta fecha.")
    else:
        for ev in evs_dia:
            bg_c = ev.get("estilo", {}).get("bg", "#d1e7dd")
            tx_c = ev.get("estilo", {}).get("text", "#0f5132")
            border_c = ev.get("estilo", {}).get("border", "#0f5132")
            
            with st.container():
                st.markdown(f"""
                    <div class="block-evento" style="background-color: {bg_c}; color: {tx_c}; border-left-color: {border_c}; font-size:0.95rem; padding: 10px;">
                        <strong>{ev['title']}</strong><br>
                        ⏱️ {ev['inicio']:02d}:00 - {ev['fin']:02d}:00 hs
                        {f'<br>💬 {ev["nota"]}' if ev.get("nota") else ''}
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("Eliminar", key=f"del_m_{ev['id']}", use_container_width=True):
                    st.session_state["eventos_calendar"] = [e for e in st.session_state["eventos_calendar"] if e["id"] != ev["id"]]
                    st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 1. PESTAÑA CALENDARIO
# ==========================================
with tab_cal:
    if st.session_state.get("selector_modo_dispositivo") == "📱 Celular":
        render_agenda_mobile()
    else:
        render_agenda_desktop()

# ==========================================
# 2. PESTAÑA CHECKLIST DIGITAL
# ==========================================
with tab_check:
    st.header("📝 Checklist Digital de Control")
    f_sel = st.session_state["fecha_seleccionada"]
    f_sel_str = f_sel.strftime("%Y-%m-%d")

    # OPCIÓN PARA SELECCIONAR O INGRESAR CUALQUIER CAPILLA DE FORMA LIBRE
    col_cap_input, col_tipo_sel = st.columns(2)
    with col_cap_input:
        capilla_manual = st.text_input("✍️ Nombre de la Capilla:", placeholder="Escribir nombre de la capilla...")
        capilla_lista = st.selectbox("O seleccionar de la lista:", st.session_state["lista_capillas"], key="chk_cap_sel")
        
        # Prioriza la capilla ingresada manualmente si existe
        capilla_trabajo = capilla_manual.strip() if capilla_manual.strip() else capilla_lista

    with col_tipo_sel:
        tipo_checklist = st.radio("Tipo de Inspección:", ["🧹 Limpieza", "🌿 Jardinería"], horizontal=True, key="chk_tipo_sel")

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
        with st.expander("🌿 Jardinería y Exteriores", expanded=True):
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
