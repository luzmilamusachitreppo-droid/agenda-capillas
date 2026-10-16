import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import uuid
import gspread
from google.oauth2.service_account import Credentials
import json
import time

# Configuración de página
st.set_page_config(
    page_title="Agenda de Capillas - Sistema Privado",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Conexión optimizada a Google Sheets con reintento automático
@st.cache_resource
def get_spreadsheet():
    import re
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    raw = st.secrets["gcp_json"].strip()
    raw = re.sub(r",\s*}", "}", raw)
    creds_dict = json.loads(raw, strict=False)
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    for intento in range(3):
        try:
            return client.open_by_key("12zw7JZ3cHMg7wKZWMTsfJmmWrpP4DDjLN9K2K_w715w")
        except Exception as e:
            if intento == 2:
                raise e
            time.sleep(2)

try:
    sheet = get_spreadsheet()
    ws_recordatorios = sheet.worksheet("recordatorios")
    ws_eventos = sheet.worksheet("eventos")
    
    try:
        ws_resumen = sheet.worksheet("resumen_capillas")
    except Exception:
        ws_resumen = None

    try:
        ws_gmail = sheet.worksheet("gmail_tracking")
    except Exception:
        ws_gmail = None
except Exception as e:
    st.error("⚠️ Error de conexión con Google Sheets. Por favor, aguardá un minuto y recargá la página.")
    st.stop()

# Autenticación de usuarios
USUARIOS_AUTORIZADOS = {
    "admin": "capillas2026",
    "Luzmila": "Caceresythomas456",
    "Guillermo": "Caceresythomas789",
    "encargado": "parroquia2026",
    "Silvia": "Caceresythomas123"
}

if "usuario_autenticado" not in st.session_state:
    st.session_state["usuario_autenticado"] = False
if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = ""

if not st.session_state["usuario_autenticado"]:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("## 🔒 Acceso Restringido")
        st.write("Sistema Interno de Gestión de Capillas")
        with st.form("form_login_privado"):
            usr_input = st.text_input("👤 Usuario")
            pass_input = st.text_input("🔑 Contraseña", type="password")
            if st.form_submit_button("Ingresar al Sistema", type="primary", use_container_width=True):
                if usr_input.strip() in USUARIOS_AUTORIZADOS and USUARIOS_AUTORIZADOS[usr_input.strip()] == pass_input.strip():
                    st.session_state["usuario_autenticado"] = True
                    st.session_state["usuario_actual"] = usr_input.strip()
                    st.success("¡Acceso concedido!")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")
    st.stop()

# Encabezado con usuario
c_usr, c_out = st.columns([3, 1])
with c_usr:
    st.caption(f"👤 Sesión activa: **{st.session_state['usuario_actual']}**")
with c_out:
    if st.button("🚪 Cerrar", use_container_width=True):
        st.session_state["usuario_autenticado"] = False
        st.rerun()

st.divider()

# Listado ordenado por zonas de capillas
ZONAS_CAPILLAS = {
    "CAPILLAS CORRIENTES": [
        "Capilla Laguna seca",
        "Armenia",
        "Costanera",
        "Bella Vista",
        "Mendoza al sur",
        "Goya"
    ],
    "CAPILLA RESISTENCIA NORTE": [
        "Barrio 1",
        "Barrio 2",
        "Barrio 3",
        "El Colorado",
        "La Leonesa",
        "San Martin"
    ],
    "CAPILLA RESISTENCIA SUR": [
        "Alberdi",
        "Barrio 4",
        "Guiraldes",
        "Barranqueras",
        "Puerto Tirol"
    ]
}

todas_las_capillas = []
for z, caps in ZONAS_CAPILLAS.items():
    todas_las_capillas.extend(caps)

OPCIONES_CAPILLA_FORM = ["(Ninguna / Tarea General)"] + todas_las_capillas

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
    "Resto Baños y Sanitarios": [
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

PALETA_COLORES = {
    "💚 Verde - Confirmado": {"bg": "#d1e7dd", "border": "#0f5132", "text": "#0f5132"},
    "💙 Azul - En proceso": {"bg": "#cff4fc", "border": "#055160", "text": "#055160"},
    "💜 Violeta - Especial": {"bg": "#e2d9f3", "border": "#593196", "text": "#593196"},
    "💛 Amarillo - Pendiente": {"bg": "#fff3cd", "border": "#664d03", "text": "#664d03"},
    "🩷 Rosa - Alerta": {"bg": "#f8d7da", "border": "#842029", "text": "#842029"}
}

if "fecha_seleccionada" not in st.session_state:
    st.session_state["fecha_seleccionada"] = date.today()

st.markdown("""
    <style>
    .card-note {
        background-color: #ffffff;
        border-left: 5px solid #0284c7;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
    }
    .badge-visita {
        background-color: #e0f2fe;
        color: #0369a1;
        border-radius: 6px;
        padding: 4px 8px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .badge-alerta-roja {
        background-color: #fee2e2;
        color: #991b1b;
        border: 1px solid #fecaca;
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        margin: 4px;
    }
    .badge-alerta-amarilla {
        background-color: #fef9c3;
        color: #854d0e;
        border: 1px solid #fef08a;
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        margin: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# 5 Pestañas principales
tab_cal, tab_check, tab_capillas, tab_notes, tab_gmail = st.tabs([
    "📅 1. Agenda Principal", 
    "📝 2. Checklist Digital", 
    "⛪ 3. Resumen de Capillas",
    "📌 4. Recordatorios Rápidos",
    "✉️ 5. Gmail"
])

# ==========================================
# 1. AGENDA PRINCIPAL Y AVISOS PRÓXIMOS
# ==========================================
with tab_cal:
    f_sel = st.session_state["fecha_seleccionada"]
    f_sel_str = f_sel.strftime("%Y-%m-%d")

    try:
        eventos_gsheets = ws_eventos.get_all_records()
    except Exception:
        eventos_gsheets = []

    # BLOQUE DE ALERTAS Y AVISOS SEMANALES CON COLOR DINÁMICO
    inicio_sem_actual = f_sel - timedelta(days=f_sel.weekday())
    fin_sem_actual = inicio_sem_actual + timedelta(days=6)
    
    eventos_semana = []
    for ev in eventos_gsheets:
        f_ev_str = str(ev.get("fecha", ""))
        try:
            f_ev_dt = datetime.strptime(f_ev_str, "%Y-%m-%d").date()
            if inicio_sem_actual <= f_ev_dt <= fin_sem_actual:
                eventos_semana.append((f_ev_dt, ev))
        except Exception:
            pass
            
    eventos_semana.sort(key=lambda x: x[0])

    if eventos_semana:
        with st.expander(f"🔔 **Avisos de Tareas Programadas para esta Semana ({inicio_sem_actual.strftime('%d/%m')} al {fin_sem_actual.strftime('%d/%m')})**", expanded=True):
            cols_ev = st.columns(min(len(eventos_semana), 3))
            for idx_ev, (f_dt, ev_data) in enumerate(eventos_semana):
                col_idx = idx_ev % 3
                cat_aviso = ev_data.get("categoria", "") or ev_data.get("color", "💚 Verde - Confirmado")
                estilo_aviso = PALETA_COLORES.get(cat_aviso, PALETA_COLORES["💚 Verde - Confirmado"])
                
                with cols_ev[col_idx]:
                    st.markdown(f"""
                        <div style="background-color: {estilo_aviso['bg']}; border-left: 4px solid {estilo_aviso['border']}; color: {estilo_aviso['text']}; padding: 10px; border-radius: 6px; margin-bottom: 8px;">
                            <strong>📅 {f_dt.strftime('%d/%m (%a)')}: {ev_data.get('title')}</strong><br>
                            ⏱️ {int(ev_data.get('inicio', 0)):02d}:00 - {int(ev_data.get('fin', 0)):02d}:00 hs<br>
                            <span style="font-size:0.8rem;">{ev_data.get('nota', 'Sin detalle')}</span>
                        </div>
                    """, unsafe_allow_html=True)

    fechas_con_tareas = {str(e.get("fecha")) for e in eventos_gsheets if e.get("fecha")}

    st.markdown(f"<h3 style='text-align: center; color: #0284c7; margin-bottom: 5px;'>📅 Semana del {f_sel.strftime('%d/%m/%Y')}</h3>", unsafe_allow_html=True)

    col_nav1, col_hoy, col_nav2 = st.columns([1, 1, 1])
    if col_nav1.button("◄ Semana", use_container_width=True):
        st.session_state["fecha_seleccionada"] -= timedelta(days=7)
        st.rerun()
    if col_hoy.button("📍 Hoy", use_container_width=True):
        st.session_state["fecha_seleccionada"] = date.today()
        st.rerun()
    if col_nav2.button("Semana ►", use_container_width=True):
        st.session_state["fecha_seleccionada"] += timedelta(days=7)
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    inicio_semana = f_sel - timedelta(days=f_sel.weekday())
    dias_semana = [inicio_semana + timedelta(days=i) for i in range(7)]
    nombres_cortos = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

    cols_semana = st.columns(7)
    for idx, d_f in enumerate(dias_semana):
        d_str = d_f.strftime("%Y-%m-%d")
        tiene_tarea = d_str in fechas_con_tareas
        etiqueta = f"{nombres_cortos[idx]}\n{d_f.day}" + (" •" if tiene_tarea else "")
        
        es_seleccionado = (d_f == f_sel)
        tipo_btn = "primary" if es_seleccionado else "secondary"
        
        if cols_semana[idx].button(etiqueta, key=f"btn_semana_{d_str}", type=tipo_btn, use_container_width=True):
            st.session_state["fecha_seleccionada"] = d_f
            st.rerun()

    st.divider()

    col_izq, col_der = st.columns([1.2, 1], gap="medium")

    with col_izq:
        st.markdown(f"#### 📋 Tareas del {f_sel.strftime('%d/%m/%Y')}")
        evs_dia = [e for e in eventos_gsheets if str(e.get("fecha")) == f_sel_str]
        
        if not evs_dia:
            st.info("No hay tareas programadas para esta fecha.")
        else:
            for ev in evs_dia:
                cat_ev = ev.get("categoria", "") or ev.get("color", "💚 Verde - Confirmado")
                estilo = PALETA_COLORES.get(cat_ev, PALETA_COLORES["💚 Verde - Confirmado"])
                id_ev = str(ev.get("id", ""))
                
                st.markdown(f"""
                    <div style="background-color: {estilo['bg']}; border-left: 5px solid {estilo['border']}; padding: 12px; border-radius: 8px; margin-bottom: 8px; color: {estilo['text']};">
                        <strong>{ev.get('title', 'Sin Título')}</strong><br>
                        ⏱️ {int(ev.get('inicio', 0)):02d}:00 - {int(ev.get('fin', 0)):02d}:00 hs
                        {f'<br>💬 {ev.get("nota")}' if ev.get("nota") else ''}
                    </div>
                """, unsafe_allow_html=True)
                
                col_ev_edit, col_ev_del = st.columns([1, 1])
                
                with col_ev_edit:
                    with st.popover("✏️ Editar", use_container_width=True):
                        st.markdown("**Editar Tarea de Agenda**")
                        with st.form(key=f"form_edit_ev_{id_ev}"):
                            # Extraer datos actuales
                            tit_actual = str(ev.get("title", ""))
                            cap_def = "(Ninguna / Tarea General)"
                            t_puro = tit_actual
                            if " - " in tit_actual:
                                partes = tit_actual.split(" - ", 1)
                                if partes[0] in todas_las_capillas:
                                    cap_def = partes[0]
                                    t_puro = partes[1]

                            new_f_tarea = st.date_input("Fecha:", value=f_sel, key=f"f_ed_{id_ev}")
                            
                            idx_cap_def = OPCIONES_CAPILLA_FORM.index(cap_def) if cap_def in OPCIONES_CAPILLA_FORM else 0
                            new_cap_opc = st.selectbox("Capilla (Opcional):", options=OPCIONES_CAPILLA_FORM, index=idx_cap_def, key=f"cap_ed_{id_ev}")
                            new_tit_input = st.text_input("Título / Tarea:", value=t_puro, key=f"tit_ed_{id_ev}")
                            
                            idx_cat_def = list(PALETA_COLORES.keys()).index(cat_ev) if cat_ev in PALETA_COLORES else 0
                            new_cat_t = st.selectbox("Situación / Color:", options=list(PALETA_COLORES.keys()), index=idx_cat_def, key=f"cat_ed_{id_ev}")
                            new_nota_t = st.text_area("Detalle adicional", value=str(ev.get("nota", "")), height=68, key=f"nota_ed_{id_ev}")
                            
                            ce1, ce2 = st.columns(2)
                            new_h_i = ce1.number_input("Inicio", min_value=7, max_value=20, value=int(ev.get("inicio", 8)), key=f"hi_ed_{id_ev}")
                            new_h_f = ce2.number_input("Fin", min_value=8, max_value=21, value=int(ev.get("fin", 12)), key=f"hf_ed_{id_ev}")

                            if st.form_submit_button("💾 Guardar Cambios", type="primary", use_container_width=True):
                                if new_tit_input.strip():
                                    if new_cap_opc != "(Ninguna / Tarea General)":
                                        titulo_final = f"{new_cap_opc} - {new_tit_input.strip()}"
                                    else:
                                        titulo_final = new_tit_input.strip()
                                else:
                                    titulo_final = new_cap_opc if new_cap_opc != "(Ninguna / Tarea General)" else "Tarea General"

                                cell = ws_eventos.find(id_ev)
                                if cell:
                                    row_n = cell.row
                                    ws_eventos.update_cell(row_n, 2, titulo_final)
                                    ws_eventos.update_cell(row_n, 3, new_f_tarea.strftime("%Y-%m-%d"))
                                    ws_eventos.update_cell(row_n, 4, int(new_h_i))
                                    ws_eventos.update_cell(row_num=row_n, col=5, value=int(new_h_f))
                                    ws_eventos.update_cell(row_n, 6, new_nota_t.strip())
                                    ws_eventos.update_cell(row_n, 7, new_cat_t)
                                    st.session_state["fecha_seleccionada"] = new_f_tarea
                                    st.success("¡Tarea actualizada!")
                                    st.rerun()

                with col_ev_del:
                    if st.button("🗑️ Borrar", key=f"del_ev_{id_ev}", use_container_width=True):
                        cell = ws_eventos.find(id_ev)
                        if cell:
                            ws_eventos.delete_rows(cell.row)
                        st.rerun()
                
                st.markdown("<br>", unsafe_allow_html=True)

    with col_der:
        st.markdown("#### ➕ Agregar Tarea")
        with st.form("form_add_evento_col", clear_on_submit=True):
            f_tarea = st.date_input("Fecha:", value=f_sel)
            
            cap_opcional = st.selectbox("Capilla (Opcional):", options=OPCIONES_CAPILLA_FORM)
            tit_tarea_input = st.text_input("Título / Tarea:", placeholder="Ej: Limpieza profunda, Control de luminarias, etc.")
            
            cat_t = st.selectbox("Situación / Color:", options=list(PALETA_COLORES.keys()))
            nota_t = st.text_area("Detalle adicional", placeholder="Notas u observaciones...", height=68)
            
            c1, c2 = st.columns(2)
            h_i = c1.number_input("Inicio", min_value=7, max_value=20, value=8)
            h_f = c2.number_input("Fin", min_value=8, max_value=21, value=12)
            
            if st.form_submit_button("Guardar en Agenda", type="primary", use_container_width=True):
                if tit_tarea_input.strip():
                    if cap_opcional != "(Ninguna / Tarea General)":
                        titulo_completo = f"{cap_opcional} - {tit_tarea_input.strip()}"
                    else:
                        titulo_completo = tit_tarea_input.strip()
                else:
                    if cap_opcional != "(Ninguna / Tarea General)":
                        titulo_completo = cap_opcional
                    else:
                        titulo_completo = "Tarea General"

                ws_eventos.append_row([
                    str(uuid.uuid4()),
                    titulo_completo,
                    f_tarea.strftime("%Y-%m-%d"),
                    int(h_i),
                    int(h_f),
                    nota_t.strip(),
                    cat_t
                ])
                st.session_state["fecha_seleccionada"] = f_tarea
                st.success("¡Tarea guardada con éxito!")
                st.rerun()
                # ==========================================
# 2. CHECKLIST DIGITAL
# ==========================================
with tab_check:
    st.header("📝 Checklist Digital de Control")
    
    col_c1, col_c2 = st.columns([1, 1])
    with col_c1:
        capilla_trabajo = st.selectbox("Seleccionar Capilla:", todas_las_capillas, key="chk_cap_sel")
    with col_c2:
        tipo_checklist = st.radio("Tipo de Inspección:", ["🧹 Limpieza", "🌿 Jardinería"], horizontal=True, key="chk_tipo_sel")

    st.markdown(f"### Revisión: **{capilla_trabajo}** ({f_sel.strftime('%d/%m/%Y')})")
    
    if "Limpieza" in tipo_checklist:
        for cat, items in PDF_CHECKLIST_ITEMS.items():
            with st.expander(cat, expanded=True):
                for item in items:
                    st.checkbox(item, key=f"chk_item_{capilla_trabajo}_{item}")
                    st.text_input(f"Observación ({item})", key=f"obs_item_{capilla_trabajo}_{item}", placeholder="Detalles u observaciones...")
                    st.markdown("<hr style='margin: 8px 0; border-top: 1px dashed #cbd5e1;'>", unsafe_allow_html=True)
    else:
        with st.expander("🌿 Jardinería y Exteriores", expanded=True):
            for item in CHECKLIST_JARDINERIA_DEFAULT:
                st.checkbox(item, key=f"chk_jard_{capilla_trabajo}_{item}")
                st.text_input(f"Observación ({item})", key=f"obs_jard_{capilla_trabajo}_{item}", placeholder="Detalles u observaciones...")
                st.markdown("<hr style='margin: 8px 0; border-top: 1px dashed #cbd5e1;'>", unsafe_allow_html=True)

# ==========================================
# 3. RESUMEN DE CAPILLAS Y ESTADÍSTICAS VISUALES
# ==========================================
with tab_capillas:
    st.header("⛪ Resumen de Capillas y Control de Visitas")
    
    registros_capillas = []
    if ws_resumen:
        try:
            registros_capillas = ws_resumen.get_all_records()
        except Exception:
            registros_capillas = []

    mapa_resumen = {}
    total_visitas_global = 0

    for idx_r, r in enumerate(registros_capillas):
        cap = str(r.get("capilla", "")).strip()
        if cap:
            if cap not in mapa_resumen:
                mapa_resumen[cap] = {"estado": r.get("estado_planilla", "Pendiente"), "visitas": []}
            
            dias_str = str(r.get("dias_visitados", "")).strip()
            if dias_str:
                mapa_resumen[cap]["visitas"].append({
                    "row_index": idx_r + 2,
                    "texto": dias_str
                })
                total_visitas_global += 1
            
            if r.get("estado_planilla"):
                mapa_resumen[cap]["estado"] = r.get("estado_planilla")

    st.markdown("### 📊 Estadísticas Generales del Mes")
    c_met1, c_met2, c_met3 = st.columns(3)
    c_met1.metric("📌 Total de Visitas Registradas", total_visitas_global)
    
    capillas_visitadas_count = sum(1 for c in todas_las_capillas if len(mapa_resumen.get(c, {}).get("visitas", [])) > 0)
    c_met2.metric("⛪ Capillas con al menos 1 Visita", f"{capillas_visitadas_count} / {len(todas_las_capillas)}")
    
    completadas_count = sum(1 for c in todas_las_capillas if mapa_resumen.get(c, {}).get("estado") == "Completado")
    c_met3.metric("📋 Planillas Completadas", f"{completadas_count} / {len(todas_las_capillas)}")

    st.markdown("<br>", unsafe_allow_html=True)

    sin_visitas = []
    pocas_visitas = []

    for c in todas_las_capillas:
        cant_v = len(mapa_resumen.get(c, {}).get("visitas", []))
        if cant_v == 0:
            sin_visitas.append(c)
        elif cant_v <= 2:
            pocas_visitas.append((c, cant_v))

    col_rep1, col_rep2 = st.columns(2)
    with col_rep1:
        st.markdown("""
            <div style="background-color: #fef2f2; border-left: 5px solid #ef4444; padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                <h4 style="margin:0 0 4px 0; color: #991b1b; font-size:1rem;">🔴 Capillas SIN visitas este mes (0)</h4>
            </div>
        """, unsafe_allow_html=True)
        if not sin_visitas:
            st.success("¡Excelente! Todas las capillas recibieron al menos una visita este mes.")
        else:
            html_sin = ""
            for c in sin_visitas:
                html_sin += f'<span class="badge-alerta-roja">⛪ {c}</span>'
            st.markdown(html_sin, unsafe_allow_html=True)

    with col_rep2:
        st.markdown("""
            <div style="background-color: #fefce8; border-left: 5px solid #eab308; padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                <h4 style="margin:0 0 4px 0; color: #854d0e; font-size:1rem;">💛 Capillas visitadas de 1 a 2 veces</h4>
            </div>
        """, unsafe_allow_html=True)
        if not pocas_visitas:
            st.info("No hay capillas en el rango de 1 a 2 visitas.")
        else:
            html_pocas = ""
            for c, cant in pocas_visitas:
                html_pocas += f'<span class="badge-alerta-amarilla">⛪ {c} ({cant} visita{"s" if cant > 1 else ""})</span>'
            st.markdown(html_pocas, unsafe_allow_html=True)

    st.divider()

    for zona, capillas in ZONAS_CAPILLAS.items():
        st.markdown(f"### 📍 {zona}")
        for c in capillas:
            data_capilla = mapa_resumen.get(c, {"estado": "Pendiente", "visitas": []})
            cant_v = len(data_capilla["visitas"])
            
            st.markdown(f"#### ⛪ {c} &nbsp;&nbsp;|&nbsp;&nbsp; <span style='font-size:0.9rem; color:#0284c7;'>📊 Visitas este mes: <strong>{cant_v}</strong></span>", unsafe_allow_html=True)
            
            col_est, col_add_v = st.columns([1, 1.5])
            
            with col_est:
                idx_default = ["Pendiente", "En Proceso", "Completado"].index(data_capilla["estado"]) if data_capilla["estado"] in ["Pendiente", "En Proceso", "Completado"] else 0
                nuevo_estado = st.selectbox(
                    "Estado de planilla", 
                    ["Pendiente", "En Proceso", "Completado"], 
                    index=idx_default,
                    key=f"est_sel_{c}"
                )
                
                if nuevo_estado != data_capilla["estado"]:
                    if ws_resumen:
                        ws_resumen.append_row([zona, c, nuevo_estado, ""])
                        st.success(f"Estado de {c} actualizado a {nuevo_estado}")
                        st.rerun()

            with col_add_v:
                nueva_fecha_v = st.text_input(
                    "➕ Registrar nueva visita este mes:", 
                    placeholder="Ej: 02/10", 
                    key=f"in_fecha_{c}"
                )
                if st.button(f"📌 Registrar visita en {c}", key=f"btn_add_v_{c}", use_container_width=True):
                    if nueva_fecha_v.strip() and ws_resumen:
                        ws_resumen.append_row([
                            zona, 
                            c, 
                            nuevo_estado, 
                            f"{nueva_fecha_v.strip()} (por {st.session_state['usuario_actual']})"
                        ])
                        st.success(f"¡Visita {nueva_fecha_v} guardada para {c}!")
                        st.rerun()

            st.markdown("📅 **Días visitados este mes:**")
            if not data_capilla["visitas"]:
                st.caption("Aún no hay visitas registradas este mes.")
            else:
                for v_info in data_capilla["visitas"]:
                    c_badge, c_del = st.columns([4, 1])
                    with c_badge:
                        st.markdown(f'<span class="badge-visita">✔ {v_info["texto"]}</span>', unsafe_allow_html=True)
                    with c_del:
                        if st.button("🗑️ Borrar", key=f"del_v_{c}_{v_info['row_index']}", help="Borrar esta visita"):
                            if ws_resumen:
                                ws_resumen.delete_rows(v_info["row_index"])
                                st.success("Visita eliminada con éxito.")
                                st.rerun()

            st.markdown("<hr style='margin: 15px 0; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
        st.divider()

# ==========================================
# 4. RECORDATORIOS RÁPIDOS
# ==========================================
with tab_notes:
    st.markdown("## 📌 Recordatorios")

    OPCIONES_PRIORIDAD = ["🩷 Urgente / Importante", "💛 Normal", "💚 Idea / Nota"]

    with st.form("form_nueva_nota_libre", clear_on_submit=True):
        titulo_nota = st.text_input("Nota:", placeholder="Ej: Comprar bolsas de residuos para la capilla Alberdi")
        detalle_nota = st.text_area("Detalle:", placeholder="Ej: Pedir en la ferretería de la esquina", height=80)
        prioridad_nota = st.selectbox("Prioridad:", OPCIONES_PRIORIDAD)
        btn_guardar_nota = st.form_submit_button("➕ Añadir Recordatorio", type="primary", use_container_width=True)

        if btn_guardar_nota and titulo_nota.strip():
            ws_recordatorios.append_row([
                str(uuid.uuid4()),
                titulo_nota.strip(),
                detalle_nota.strip(),
                prioridad_nota,
                st.session_state["usuario_actual"],
                datetime.now().strftime("%d/%m/%Y %H:%M")
            ])
            st.success("¡Recordatorio guardado!")
            st.rerun()

    st.divider()
    
    recs = ws_recordatorios.get_all_records()
    
    if not recs:
        st.info("No hay recordatorios pendientes.")
    else:
        mapa_colores_notas = {
            "🩷 Urgente / Importante": {"border": "#ef4444", "bg": "#fef2f2", "orden": 1},
            "💛 Normal": {"border": "#eab308", "bg": "#fefce8", "orden": 2},
            "💚 Idea / Nota": {"border": "#22c55e", "bg": "#f0fdf4", "orden": 3}
        }

        def parse_fecha(f_str):
            try:
                return datetime.strptime(str(f_str), "%d/%m/%Y %H:%M")
            except Exception:
                return datetime.min

        recs_ordenados = sorted(
            recs,
            key=lambda x: (
                mapa_colores_notas.get(x.get("prioridad", ""), {"orden": 99})["orden"],
                parse_fecha(x.get("fecha_creacion", ""))
            ),
            reverse=False
        )

        for idx, nota in enumerate(recs_ordenados):
            tit = nota.get("titulo", "Sin título")
            det = nota.get("detalle", "")
            prio = nota.get("prioridad", "💛 Normal")
            autor = nota.get("creado_por", "Sistema")
            fec = nota.get("fecha_creacion", "")
            id_n = str(nota.get("id", ""))

            c_info = mapa_colores_notas.get(prio, {"border": "#0284c7", "bg": "#ffffff", "orden": 2})
            
            with st.container():
                st.markdown(f"""
                    <div class="card-note" style="border-left-color: {c_info['border']}; background-color: {c_info['bg']};">
                        <h4 style="margin:0 0 6px 0; color:#1e293b;">{tit}</h4>
                        <p style="margin:0 0 8px 0; color:#475569; font-size:0.9rem;">{det if det else '<em>Sin detalle adicional</em>'}</p>
                        <span style="font-size:0.75rem; color:#64748b;">
                            📌 Prioridad: <strong>{prio}</strong> | 👤 Por <strong>{autor}</strong> ({fec})
                        </span>
                    </div>
                """, unsafe_allow_html=True)
                
                col_edit, col_del = st.columns([1, 1])
                
                with col_edit:
                    with st.popover("✏️ Editar Recordatorio", use_container_width=True):
                        st.markdown(f"**Editar Recordatorio**")
                        with st.form(key=f"form_edit_note_{idx}_{id_n}"):
                            new_tit = st.text_input("Nota / Título:", value=tit)
                            new_det = st.text_area("Detalle:", value=det, height=70)
                            
                            prio_idx = OPCIONES_PRIORIDAD.index(prio) if prio in OPCIONES_PRIORIDAD else 1
                            new_prio = st.selectbox("Prioridad / Urgencia:", OPCIONES_PRIORIDAD, index=prio_idx)
                            
                            if st.form_submit_button("💾 Guardar Cambios", type="primary", use_container_width=True):
                                if new_tit.strip():
                                    cell = ws_recordatorios.find(id_n)
                                    if cell:
                                        row_num = cell.row
                                        ws_recordatorios.update_cell(row_num, 2, new_tit.strip())
                                        ws_recordatorios.update_cell(row_num, 3, new_det.strip())
                                        ws_recordatorios.update_cell(row_num, 4, new_prio)
                                        st.success("¡Recordatorio actualizado!")
                                        st.rerun()

                with col_del:
                    if st.button("🗑️ Borrar", key=f"btn_del_nota_{idx}_{id_n}", use_container_width=True):
                        if id_n:
                            cell = ws_recordatorios.find(id_n)
                            if cell:
                                ws_recordatorios.delete_rows(cell.row)
                        st.rerun()
                        
                st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 5. GMAIL - CONTROL Y SEGUIMIENTO DE GMAIL / OT
# ==========================================
with tab_gmail:
    st.markdown("## ✉️ Control y Seguimiento de Gmail / OT")
    st.write("Registra y controla los correos enviados, su estado, proceso y situación financiera.")

    OPCIONES_ESTADO_MAIL = ["Enviado", "No enviado"]
    OPCIONES_PROCESO = ["Aprobado", "Rechazado", "Pendiente respuesta"]
    OPCIONES_FINANCIERO = ["Por facturar", "Enviado a contador", "Facturado", "Cobrado"]

    with st.form("form_nuevo_gmail", clear_on_submit=True):
        asunto_mail = st.text_input("Asunto del correo:", placeholder="Ej: Presupuesto de mantenimiento Capilla Alberdi")
        
        c_g1, c_g2 = st.columns(2)
        with c_g1:
            fecha_envio = st.date_input("Fecha de envío:", value=date.today())
            estado_mail = st.selectbox("Estado del Gmail:", OPCIONES_ESTADO_MAIL)
            etapa_proc = st.selectbox("Etapa del proceso:", OPCIONES_PROCESO)
        with c_g2:
            nro_ot = st.text_input("N° OT:", placeholder="Ej: OT-2026-048")
            estado_fin = st.selectbox("Estado financiero:", OPCIONES_FINANCIERO)

        btn_guardar_mail = st.form_submit_button("➕ Registrar Correo / OT", type="primary", use_container_width=True)

        if btn_guardar_mail and asunto_mail.strip():
            if ws_gmail:
                ws_gmail.append_row([
                    str(uuid.uuid4()),
                    asunto_mail.strip(),
                    fecha_envio.strftime("%d/%m/%Y"),
                    estado_mail,
                    etapa_proc,
                    nro_ot.strip() if nro_ot else "S/N",
                    estado_fin,
                    st.session_state["usuario_actual"],
                    datetime.now().strftime("%d/%m/%Y %H:%M")
                ])
                st.success("¡Seguimiento de correo guardado con éxito!")
                st.rerun()
            else:
                st.error("⚠️ La solapa 'gmail_tracking' no fue encontrada en Google Sheets.")

    st.divider()

    registros_gmail = []
    if ws_gmail:
        try:
            registros_gmail = ws_gmail.get_all_records()
        except Exception:
            registros_gmail = []

    # DETECCIÓN DE CORREOS EN ESPERA HACE VARIOS DÍAS
    mails_demorados = []
    hoy_date = date.today()

    for mail in registros_gmail:
        if mail.get("etapa_proceso") == "Pendiente respuesta":
            fec_env_str = str(mail.get("fecha_envio", ""))
            try:
                fec_env_dt = datetime.strptime(fec_env_str, "%d/%m/%Y").date()
                dias_transcurridos = (hoy_date - fec_env_dt).days
                if dias_transcurridos >= 3:
                    mails_demorados.append((mail, dias_transcurridos))
            except Exception:
                pass

    if mails_demorados:
        with st.expander(f"⚠️ **Atención: {len(mails_demorados)} correo(s) en 'Pendiente respuesta' desde hace más de 3 días**", expanded=True):
            for m_dem, d_trans in mails_demorados:
                st.markdown(f"""
                    <div style="background-color: #fef2f2; border-left: 5px solid #ef4444; padding: 10px; border-radius: 6px; margin-bottom: 6px;">
                        🚨 <strong>{m_dem.get('asunto')}</strong> (OT: {m_dem.get('nro_ot')}) — <em>Sin respuesta hace {d_trans} días</em> (Enviado: {m_dem.get('fecha_envio')})
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not registros_gmail:
        st.info("No hay correos ni órdenes de trabajo registradas todavía.")
    else:
        mapa_colores_mail = {
            "Aprobado": {"border": "#22c55e", "bg": "#f0fdf4"},
            "Rechazado": {"border": "#ef4444", "bg": "#fef2f2"},
            "Pendiente respuesta": {"border": "#eab308", "bg": "#fefce8"}
        }

        for idx, mail in enumerate(registros_gmail):
            id_m = str(mail.get("id", ""))
            asunto = mail.get("asunto", "Sin asunto")
            fec_env = mail.get("fecha_envio", "")
            est_m = mail.get("estado_gmail", "Enviado")
            etapa = mail.get("etapa_proceso", "Pendiente respuesta")
            ot = mail.get("nro_ot", "S/N")
            finan = mail.get("estado_financiero", "Por facturar")
            autor = mail.get("creado_por", "Sistema")
            f_crea = mail.get("fecha_creacion", "")

            c_mail_info = mapa_colores_mail.get(etapa, {"border": "#0284c7", "bg": "#ffffff"})

            with st.container():
                st.markdown(f"""
                    <div class="card-note" style="border-left-color: {c_mail_info['border']}; background-color: {c_mail_info['bg']};">
                        <h4 style="margin:0 0 6px 0; color:#1e293b;">✉️ {asunto}</h4>
                        <p style="margin:0 0 4px 0; color:#475569; font-size:0.9rem;">
                            🏷️ <strong>N° OT:</strong> {ot} &nbsp;|&nbsp; 
                            📤 <strong>Envío:</strong> {fec_env} ({est_m})
                        </p>
                        <p style="margin:0 0 8px 0; color:#334155; font-size:0.9rem;">
                            🔄 <strong>Proceso:</strong> {etapa} &nbsp;|&nbsp; 
                            💰 <strong>Financiero:</strong> {finan}
                        </p>
                        <span style="font-size:0.75rem; color:#64748b;">
                            👤 Registrado por <strong>{autor}</strong> ({f_crea})
                        </span>
                    </div>
                """, unsafe_allow_html=True)

                col_em_edit, col_em_del = st.columns([1, 1])

                with col_em_edit:
                    with st.popover("✏️ Editar Registro", use_container_width=True):
                        st.markdown("**Editar Seguimiento de Correo**")
                        with st.form(key=f"form_edit_mail_{idx}_{id_m}"):
                            new_asunto = st.text_input("Asunto:", value=asunto)
                            new_ot = st.text_input("N° OT:", value=ot)
                            
                            idx_est = OPCIONES_ESTADO_MAIL.index(est_m) if est_m in OPCIONES_ESTADO_MAIL else 0
                            new_est = st.selectbox("Estado Gmail:", OPCIONES_ESTADO_MAIL, index=idx_est)
                            
                            idx_eta = OPCIONES_PROCESO.index(etapa) if etapa in OPCIONES_PROCESO else 0
                            new_eta = st.selectbox("Etapa Proceso:", OPCIONES_PROCESO, index=idx_eta)
                            
                            idx_fin = OPCIONES_FINANCIERO.index(finan) if finan in OPCIONES_FINANCIERO else 0
                            new_fin = st.selectbox("Estado Financiero:", OPCIONES_FINANCIERO, index=idx_fin)

                            if st.form_submit_button("💾 Guardar Cambios", type="primary", use_container_width=True):
                                if new_asunto.strip():
                                    cell = ws_gmail.find(id_m)
                                    if cell:
                                        row_num = cell.row
                                        ws_gmail.update_cell(row_num, 2, new_asunto.strip())
                                        ws_gmail.update_cell(row_num, 4, new_est)
                                        ws_gmail.update_cell(row_num, 5, new_eta)
                                        ws_gmail.update_cell(row_num, 6, new_ot.strip())
                                        ws_gmail.update_cell(row_num, 7, new_fin)
                                        st.success("¡Registro de Gmail actualizado!")
                                        st.rerun()

                with col_em_del:
                    if st.button("🗑️ Borrar", key=f"btn_del_mail_{idx}_{id_m}", use_container_width=True):
                        if id_m:
                            cell = ws_gmail.find(id_m)
                            if cell:
                                ws_gmail.delete_rows(cell.row)
                        st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)
