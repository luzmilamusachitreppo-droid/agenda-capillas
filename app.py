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

CAPILLAS_DEFAULT = [
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

# ITEMS EXTRAÍDOS DEL PDF DE LIMPIEZA
PDF_CHECKLIST_ITEMS = {
    "🚶 Pasillos": [
        "1. Limpieza de pisos: Barridos, desinfectados y sin manchas o líquidos derramados.",
        "2. Techos y paredes: Sin telarañas en zonas altas, grietas o humedad visible.",
        "3. Mobiliario / Cuadros / Avisos: Limpios, firmes y sin riesgo de caída."
    ],
    "🚻 Baños (Mujeres / Hombres)": [
        "4. Piletas y canillas limpias sin sarro ni manchas.",
        "5. Insumos cargados: Jabón de manos, papel higiénico y toallas disponibles.",
        "6. Cestos de basura: Vacíos y con bolsa limpia.",
        "7. Espejos y mesadas: Secos, sin manchas y en perfecto estado.",
        "8. Ventilación y olores: Ambiente fresco y sin malos olores.",
        "9. Insumos al alcance: Papel y jabón colocados a altura accesible."
    ],
    "🍳 Cocina": [
        "11. Mesadas y superficies: Limpias, desinfectadas, secas y libres de grasa.",
        "12. Bachas y piletas: Sin sarro, desinfectadas y sin manchas.",
        "13. Grifería: Limpia, seca, sin manchas de sarro ni pérdidas/goteos."
    ],
    "🏫 Aulas y Salones": [
        "15. Mobiliario (sillas, mesas, pizarras): Limpios, acomodados y sin estructuras flojas.",
        "16. Puertas y cerraduras: Picaportes y cerraduras abren/cierran suavemente.",
        "17. Ventanas y cortinas: Vidrios limpios, marcos mecánicos operativos.",
        "18. Enchufes e interruptores: En buen estado, con tapas y sin cables expuestos.",
        "20. Piletas y canillas: Sin goteos, buen flujo y desagües limpios."
    ],
    "💼 Oficinas y Sacramental": [
        "21. Escritorios y mesas: Despolvados y ordenados.",
        "22. Ventanas y persianas: Limpias y en buen estado.",
        "23. Cerraduras de seguridad: Puertas de acceso cierran y traban correctamente.",
        "24. Acondicionador de aire / Estufas: Filtros limpios y funcionamiento correcto.",
        "25. Mesas de vidrio sin manchas ni 'manos marcadas'."
    ]
}

CHECKLIST_JARDINERIA_DEFAULT = [
    "Corte de césped general",
    "Bordeado y desmalezado",
    "Riego de plantas y jardines",
    "Poda de hojas secas y ramas",
    "Limpieza y recolección de restos de jardín"
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
                    "estilo": COLOR_JARDINERIA_BASE
                })
        curr += delta
    return eventos

# Session State
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
        padding: 12px 6px;
        font-weight: 700;
        font-size: 0.95rem;
        color: #2d3748;
        border-bottom: 2px solid #e2e8f0;
        border-right: 1px solid #edf2f7;
        text-align: center;
    }
    
    .week-table td {
        border-bottom: 1px solid #edf2f7;
        border-right: 1px solid #edf2f7;
        height: 120px !important;
        vertical-align: top;
        padding: 6px;
    }
    
    .time-col {
        width: 80px !important;
        background: #f8fafc;
        font-size: 0.9rem;
        font-weight: 700;
        color: #4a5568;
        text-align: center;
        vertical-align: middle !important;
    }
    
    .event-card {
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 0.92rem;
        font-weight: 600;
        margin-bottom: 4px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.06);
        border-left: 5px solid;
        line-height: 1.4;
        height: 95%;
        box-sizing: border-box;
    }
    </style>
""", unsafe_allow_html=True)

# PESTAÑAS PRINCIPALES
tab_cal, tab_check, tab_capillas = st.tabs([
    "📅 1. Calendario y Agenda", 
    "📝 2. Checklist Digital", 
    "⛪ 3. Resumen de Capillas"
])

# ==========================================
# 1. PESTAÑA CALENDARIO Y AGENDA
# ==========================================
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
    es_movil = "📱" in modo_vista

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
            evs_hora = [e for e in st.session_state["eventos_calendar"] if e.get("fecha") == f_str and e.get("inicio", 8) == hora]
            for ev in evs_hora:
                est = ev.get("estilo", COLOR_JARDINERIA_BASE)
                html_dia += f"""
                    <div class='event-card' style='background-color:{est["bg"]}; border-color:{est["border"]}; color:{est["text"]};'>
                        📌 {ev.get("title")}<br>
                        <small style='font-size: 0.85rem;'>⏱️ {ev.get("inicio"):02d}:00 - {ev.get("fin"):02d}:00 hs</small>
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
        cant_dias = 3 if es_movil else 7
        fechas_semana = [f_inicio + timedelta(days=i) for i in range(cant_dias)]
        
        html_semana = "<table class='week-table'><thead><tr><th class='time-col'>Hora</th>"
        for idx, f in enumerate(fechas_semana):
            html_semana += f"<th>{dias_nombres[idx]}<br><span style='font-weight:400; font-size:0.85rem;'>{f.strftime('%d/%m')}</span></th>"
        html_semana += "</tr></thead><tbody>"
        
        for hora in range(7, 19):
            html_semana += f"<tr><td class='time-col'>{hora:02d}:00</td>"
            for f in fechas_semana:
                f_str = f.strftime("%Y-%m-%d")
                evs_dia = [e for e in st.session_state["eventos_calendar"] if e.get("fecha") == f_str and e.get("inicio", 8) == hora]
                html_semana += "<td>"
                if evs_dia:
                    for ev in evs_dia:
                        est = ev.get("estilo", COLOR_JARDINERIA_BASE)
                        html_semana += f"""
                            <div class='event-card' style='background-color:{est["bg"]}; border-color:{est["border"]}; color:{est["text"]};'>
                                📌 {ev.get("title")}<br>
                                <small style='font-size: 0.85rem;'>⏱️ {ev.get("inicio"):02d}:00 - {ev.get("fin"):02d}:00</small>
                            </div>
                        """
                html_semana += "</td>"
            html_semana += "</tr>"
        html_semana += "</tbody></table>"
        st.markdown(html_semana, unsafe_allow_html=True)

    # 3. VISTA POR MES (CON EDICIÓN DIRECTA EN CADA EVENTO ENTRANDO A UN POPOVER)
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

        if es_movil:
            st.info("📱 Modo Teléfono activo: Seleccioná un día del mes para ver la agenda completa abajo:")
            dia_sel_num = st.slider("Día del mes:", min_value=1, max_value=31, value=st.session_state["fecha_seleccionada"].day)
            st.session_state["fecha_seleccionada"] = date(st.session_state["anio_visita"], st.session_state["mes_visita"], dia_sel_num)
        else:
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

                            # POPUP / NOTA FLOTANTE PARA EDITAR/BORRAR AL TAPEAR EL EVENTO
                            evs = [e for e in st.session_state["eventos_calendar"] if e.get("fecha") == f_str]
                            for ev in evs:
                                lbl_btn = f"{ev.get('inicio', 8)}:00 {ev.get('title', '')}"
                                with st.popover(lbl_btn, use_container_width=True):
                                    st.markdown(f"#### 📌 Nota de Tarea")
                                    with st.form(f"pop_edit_{ev['id']}"):
                                        n_tit = st.text_input("Título", value=ev.get("title"))
                                        
                                        # Buscar color actual
                                        c_def = list(PALETA_COLORES.keys())[0]
                                        for k, v in PALETA_COLORES.items():
                                            if v["bg"] == ev.get("estilo", {}).get("bg"):
                                                c_def = k
                                                break
                                        n_col = st.selectbox("Color", options=list(PALETA_COLORES.keys()), index=list(PALETA_COLORES.keys()).index(c_def))
                                        
                                        col_i, col_f = st.columns(2)
                                        n_i = col_i.number_input("Inicio", min_value=0, max_value=23, value=int(ev.get("inicio", 8)))
                                        n_f = col_f.number_input("Fin", min_value=1, max_value=24, value=int(ev.get("fin", 12)))
                                        
                                        guardar_ev = st.form_submit_button("💾 Guardar Cambios", use_container_width=True, type="primary")
                                        borrar_ev = st.form_submit_button("🗑️ Borrar Tarea", use_container_width=True)
                                        
                                        if guardar_ev:
                                            ev["title"] = n_tit
                                            ev["inicio"] = int(n_i)
                                            ev["fin"] = int(n_f)
                                            ev["estilo"] = PALETA_COLORES[n_col]
                                            st.success("¡Tarea actualizada!")
                                            st.rerun()
                                            
                                        if borrar_ev:
                                            st.session_state["eventos_calendar"] = [e for e in st.session_state["eventos_calendar"] if e["id"] != ev["id"]]
                                            st.success("¡Tarea borrada!")
                                            st.rerun()
                        else:
                            st.write("")

        # AGENDA POR HORAS DEL DÍA SELECCIONADO
        st.markdown("<br>", unsafe_allow_html=True)
        dias_nom = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        f_sel = st.session_state["fecha_seleccionada"]
        f_sel_str = f_sel.strftime("%Y-%m-%d")
        
        st.markdown(f"### 📅 Agenda por horas: {dias_nom[f_sel.weekday()]} {f_sel.strftime('%d/%m/%Y')}")
        
        html_dia_sel = "<table class='week-table'><thead><tr><th class='time-col'>Hora</th><th>Actividades y Compromisos</th></tr></thead><tbody>"
        for hora in range(7, 19):
            html_dia_sel += f"<tr><td class='time-col'>{hora:02d}:00 hs</td><td>"
            evs_hora = [e for e in st.session_state["eventos_calendar"] if e.get("fecha") == f_sel_str and e.get("inicio", 8) == hora]
            for ev in evs_hora:
                est = ev.get("estilo", COLOR_JARDINERIA_BASE)
                html_dia_sel += f"""
                    <div class='event-card' style='background-color:{est["bg"]}; border-color:{est["border"]}; color:{est["text"]};'>
                        📌 <b>{ev.get("title")}</b><br>
                        <small style='font-size: 0.85rem;'>⏱️ Horario: {ev.get("inicio"):02d}:00 a {ev.get("fin"):02d}:00 hs</small>
                    </div>
                """
            html_dia_sel += "</td></tr>"
        html_dia_sel += "</tbody></table>"
        
        st.markdown(html_dia_sel, unsafe_allow_html=True)

    st.divider()

    # FORMULARIO PARA AGREGAR NUEVAS TAREAS
    st.header("➕ Agendar nueva tarea al calendario")
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
                st.success("¡Tarea agendada exitosamente!")
                st.rerun()

# ==========================================
# 2. PESTAÑA CHECKLIST DIGITAL
# ==========================================
with tab_check:
    st.header("📝 Checklist Digital de Control")
    st.caption("Completá la planilla de control y agregá observaciones opcionales por tarea.")

    f_sel = st.session_state["fecha_seleccionada"]
    f_sel_str = f_sel.strftime("%Y-%m-%d")

    col_cap_sel, col_tipo_sel = st.columns(2)
    
    with col_cap_sel:
        capilla_trabajo = st.selectbox(
            "⛪ Elegir Capilla a revisar:", 
            st.session_state["lista_capillas"], 
            index=0, 
            key="chk_cap_sel",
            help="Hacé clic para cambiar la capilla que estás controlando"
        )
        
    with col_tipo_sel:
        tipo_checklist = st.radio(
            "Tipo de Trabajo:", 
            ["🧹 Limpieza (Según PDF)", "🌿 Jardinería"], 
            horizontal=True, 
            key="chk_tipo_sel"
        )

    clave_base = f"{f_sel_str}_{capilla_trabajo}_{tipo_checklist}"
    if clave_base not in st.session_state["respuestas_checklist"]:
        st.session_state["respuestas_checklist"][clave_base] = {}

    if clave_base not in st.session_state["comentarios_checklist"]:
        st.session_state["comentarios_checklist"][clave_base] = {}

    if clave_base not in st.session_state["tareas_extra_checklist"]:
        st.session_state["tareas_extra_checklist"][clave_base] = {}

    st.markdown(f"### Lista de revisión para **{capilla_trabajo}** — {f_sel.strftime('%d/%m/%Y')}")

    total_puntos = 0
    puntos_completados = 0

    def render_item_con_observacion_opcional(item_texto, key_suffix, placeholder_ejemplo="Agregar detalle u observación..."):
        global total_puntos, puntos_completados
        total_puntos += 1
        
        k_item = f"{clave_base}_{key_suffix}"
        v_actual = st.session_state["respuestas_checklist"][clave_base].get(key_suffix, False)
        c_actual = st.session_state["comentarios_checklist"][clave_base].get(key_suffix, "")
        
        col_chk, col_exp = st.columns([3, 1])
        
        with col_chk:
            chk = st.checkbox(item_texto, value=v_actual, key=k_item)
            st.session_state["respuestas_checklist"][clave_base][key_suffix] = chk
            if chk:
                puntos_completados += 1

        with col_exp:
            lbl_expander = f"💬 Nota ({c_actual[:10]}...)" if c_actual else "💬 Observación"
            with st.expander(lbl_expander, expanded=False):
                comm = st.text_input(
                    "Nota extra:", 
                    value=c_actual, 
                    key=f"comm_{k_item}", 
                    placeholder=placeholder_ejemplo,
                    label_visibility="collapsed"
                )
                st.session_state["comentarios_checklist"][clave_base][key_suffix] = comm

    if "Limpieza" in tipo_checklist:
        for categoria, items in PDF_CHECKLIST_ITEMS.items():
            with st.expander(f"{categoria}", expanded=True):
                for item in items:
                    if "Baños" in categoria:
                        ej = "Ej: En el baño 2 de mujeres hay sarro"
                    elif "Cocina" in categoria:
                        ej = "Ej: La canilla de la bacha pierde una gota"
                    elif "Pasillos" in categoria:
                        ej = "Ej: Falta cambiar foco de entrada"
                    else:
                        ej = "Ej: Silla rota en el fondo del salón"

                    render_item_con_observacion_opcional(item, item, placeholder_ejemplo=ej)

                extras_cat = st.session_state["tareas_extra_checklist"][clave_base].get(categoria, [])
                for ex_item in extras_cat:
                    render_item_con_observacion_opcional(f"➕ {ex_item}", f"{categoria}_{ex_item}", placeholder_ejemplo="Detalle adicional...")

                st.markdown("---")
                with st.form(f"form_extra_{categoria}", clear_on_submit=True):
                    nueva_t = st.text_input(f"Agregar tarea extra en {categoria}:", placeholder="Ej: Cambiar foco roto")
                    if st.form_submit_button("➕ Añadir a esta habitación"):
                        if nueva_t.strip():
                            if categoria not in st.session_state["tareas_extra_checklist"][clave_base]:
                                st.session_state["tareas_extra_checklist"][clave_base][categoria] = []
                            st.session_state["tareas_extra_checklist"][clave_base][categoria].append(nueva_t.strip())
                            st.rerun()

    else:
        with st.expander("🌿 Control de Jardinería", expanded=True):
            for item in CHECKLIST_JARDINERIA_DEFAULT:
                render_item_con_observacion_opcional(item, item, placeholder_ejemplo="Ej: Falta regar las plantas traseras")

            extras_j = st.session_state["tareas_extra_checklist"][clave_base].get("Jardineria", [])
            for ex_item in extras_j:
                render_item_con_observacion_opcional(f"➕ {ex_item}", f"Jardineria_{ex_item}", placeholder_ejemplo="Detalle extra...")

            st.markdown("---")
            with st.form("form_extra_jardineria", clear_on_submit=True):
                nueva_tj = st.text_input("Agregar tarea extra de Jardinería:", placeholder="Ej: Riego de maceteros traseros")
                if st.form_submit_button("➕ Añadir a Jardinería"):
                    if nueva_tj.strip():
                        if "Jardineria" not in st.session_state["tareas_extra_checklist"][clave_base]:
                            st.session_state["tareas_extra_checklist"][clave_base]["Jardineria"] = []
                        st.session_state["tareas_extra_checklist"][clave_base]["Jardineria"].append(nueva_tj.strip())
                        st.rerun()

    pct = (puntos_completados / total_puntos) if total_puntos > 0 else 0
    st.progress(pct, text=f"Progreso en {capilla_trabajo}: {puntos_completados} de {total_puntos} completados ({int(pct*100)}%)")

    if pct == 1.0:
        st.balloons()
        st.success(f"🎉 ¡Revisión completada al 100% en {capilla_trabajo}!")

# ==========================================
# 3. PESTAÑA RESUMEN DE CAPILLAS
# ==========================================
with tab_capillas:
    st.header("⛪ Resumen y Control de Estado de Capillas")
    st.caption("Seguimiento del estado general de cada ubicación.")
    
    with st.expander("➕ ¿Querés agregar una nueva capilla?", expanded=False):
        with st.form("form_nueva_capilla", clear_on_submit=True):
            nueva_cap_nombre = st.text_input("Nombre de la capilla:", placeholder="Ej: Barrio San José")
            if st.form_submit_button("Agregar Capilla"):
                if nueva_cap_nombre.strip() and nueva_cap_nombre.strip() not in st.session_state["lista_capillas"]:
                    st.session_state["lista_capillas"].append(nueva_cap_nombre.strip())
                    st.session_state["estados_capillas"][nueva_cap_nombre.strip()] = "Pendiente"
                    st.success(f"¡Capilla {nueva_cap_nombre.strip()} agregada!")
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    for c in st.session_state["lista_capillas"]:
        estado_act = st.session_state["estados_capillas"].get(c, "Pendiente")
        st.subheader(c)
        nuevo_est = st.selectbox(
            f"Estado actual para {c}:",
            ["Pendiente", "En Proceso", "Completado"],
            index=0 if estado_act == "Pendiente" else (1 if estado_act == "En Proceso" else 2),
            key=f"est_{c}"
        )
        st.session_state["estados_capillas"][c] = nuevo_est
        st.divider()
