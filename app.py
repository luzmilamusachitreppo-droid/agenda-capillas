import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date, timedelta
import uuid

# Configuración de página con layout amplio
st.set_page_config(
    page_title="Agenda de Capillas",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Paleta de colores Pastel
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
                    "estilo": COLOR_JARDINERIA_BASE,
                    "nota": "Trabajo de jardinería programado"
                })
        curr += delta
    return eventos

# Variables de Sesión
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

# Estilos CSS Limpios
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    
    /* Estilo del Bloc de Notas Lateral */
    .bloc-notas {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Indicador visual de tareas en la casilla */
    .dot-indicator {
        font-size: 11px;
        color: #2563eb;
        font-weight: bold;
        display: block;
        margin-top: 2px;
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
# 1. PESTAÑA CALENDARIO Y AGENDA (DISPOSICIÓN LIMPIA Y BLOC LATERAL)
# ==========================================
with tab_cal:
    # Encabezado del mes y navegación
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

    # LAYOUT DE 2 COLUMNAS: CALENDARIO (70%) Y BLOC DE NOTAS (30%)
    col_calendario, col_bloc = st.columns([2.3, 1], gap="medium")

    # COLUMNA IZQUIERDA: CALENDARIO LIMPIO
    with col_calendario:
        headers = st.columns(7)
        dias_hdr = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
        for idx, h in enumerate(dias_hdr):
            headers[idx].markdown(f"<h4 style='text-align:center;'>{h}</h4>", unsafe_allow_html=True)

        cal_semanas = calendar.monthcalendar(st.session_state["anio_visita"], st.session_state["mes_visita"])
        
        for semana in cal_semanas:
            cols_dia = st.columns(7)
            semana_rot = [semana[-1]] + semana[:-1] # Ajustar domingo primero
            
            for idx, dia_num in enumerate(semana_rot):
                with cols_dia[idx]:
                    if dia_num != 0:
                        f_str = f"{st.session_state['anio_visita']}-{st.session_state['mes_visita']:02d}-{dia_num:02d}"
                        f_curr = date(st.session_state["anio_visita"], st.session_state["mes_visita"], dia_num)
                        
                        # Conteo de tareas para mostrar etiqueta
                        evs_dia = [e for e in st.session_state["eventos_calendar"] if e.get("fecha") == f_str]
                        cant_tareas = len(evs_dia)
                        
                        es_seleccionado = (f_curr == st.session_state["fecha_seleccionada"])
                        
                        # Texto del botón
                        txt_btn = f"★ {dia_num}" if es_seleccionado else f"{dia_num}"
                        if cant_tareas > 0 and not es_seleccionado:
                            txt_btn += f" ({cant_tareas})"
                            
                        btn_type = "primary" if es_seleccionado else "secondary"
                        
                        if st.button(txt_btn, key=f"btn_cal_{st.session_state['mes_visita']}_{dia_num}", type=btn_type, use_container_width=True):
                            st.session_state["fecha_seleccionada"] = f_curr
                            st.rerun()
                    else:
                        st.write("")

    # COLUMNA DERECHA: BLOC DE NOTAS LATERAL DEL DÍA SELECCIONADO
    with col_bloc:
        f_sel = st.session_state["fecha_seleccionada"]
        f_sel_str = f_sel.strftime("%Y-%m-%d")
        dias_semana_esp = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        st.markdown(f"### 📝 Bloc del día")
        st.markdown(f"**{dias_semana_esp[f_sel.weekday()]} {f_sel.strftime('%d/%m/%Y')}**")
        st.divider()

        # Botón para desplegar el formulario de agendar
        with st.popover("➕ Agendar nueva tarea", use_container_width=True):
            st.markdown("#### Agendar en este día")
            with st.form("form_nueva_tarea_bloc", clear_on_submit=True):
                titulo_n = st.text_input("Título / Capilla", placeholder="Ej: Jardinería Barrio 1")
                nota_n = st.text_input("Detalle u observación", placeholder="Ej: Traer cortadora de césped")
                color_n = st.selectbox("Color", options=list(PALETA_COLORES.keys()))
                
                c1, c2 = st.columns(2)
                h_i = c1.number_input("Desde (hs)", min_value=0, max_value=23, value=8)
                h_f = c2.number_input("Hasta (hs)", min_value=1, max_value=24, value=12)
                
                if st.form_submit_button("Guardar Tarea", type="primary", use_container_width=True):
                    if titulo_n.strip():
                        st.session_state["eventos_calendar"].append({
                            "id": str(uuid.uuid4()),
                            "title": titulo_n.strip(),
                            "fecha": f_sel_str,
                            "inicio": int(h_i),
                            "fin": int(h_f),
                            "estilo": PALETA_COLORES[color_n],
                            "nota": nota_n.strip()
                        })
                        st.success("¡Tarea guardada!")
                        st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Listado de tareas del día seleccionado
        evs_del_dia = [e for e in st.session_state["eventos_calendar"] if e.get("fecha") == f_sel_str]
        
        if not evs_del_dia:
            st.info("No hay tareas agendadas para este día.")
        else:
            for ev in evs_del_dia:
                with st.container():
                    col_t, col_del = st.columns([4, 1])
                    
                    with col_t:
                        st.markdown(f"**📌 {ev['title']}**")
                        st.caption(f"⏱️ {ev['inicio']:02d}:00 a {ev['fin']:02d}:00 hs")
                        if ev.get("nota"):
                            st.caption(f"💬 {ev['nota']}")
                            
                    with col_del:
                        # Botón de basura para borrar tarea
                        if st.button("🗑️", key=f"del_{ev['id']}", help="Eliminar tarea"):
                            st.session_state["eventos_calendar"] = [e for e in st.session_state["eventos_calendar"] if e["id"] != ev["id"]]
                            st.rerun()
                            
                    st.markdown("---")

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
            key="chk_cap_sel"
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
                    ej = "Ej: Detalle adicional..."
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

# ==========================================
# 3. PESTAÑA RESUMEN DE CAPILLAS
# ==========================================
with tab_capillas:
    st.header("⛪ Resumen y Control de Estado de Capillas")
    
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
