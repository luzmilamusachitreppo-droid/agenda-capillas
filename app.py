import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import uuid
import gspread
from google.oauth2.service_account import Credentials
import json
import time
import io

# Configuración de página
st.set_page_config(
    page_title="Agenda de Capillas - Sistema Privado",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Conexión optimizada a Google Sheets
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

OPCIONES_PRIORIDAD_RECORDATORIO = [
    "💓 Urgente / Importante",
    "💛 Normal",
    "💚 Poco Urgente / Rutinario"
]

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
# 1. AGENDA PRINCIPAL
# ==========================================
with tab_cal:
    f_sel = st.session_state["fecha_seleccionada"]
    f_sel_str = f_sel.strftime("%Y-%m-%d")

    try:
        eventos_gsheets = ws_eventos.get_all_records()
    except Exception:
        eventos_gsheets = []

    meses_nombres = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
        7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }

    st.markdown(f"### 🗓️ Resumen Mensual: **{meses_nombres[f_sel.month]} {f_sel.year}**")
    
    eventos_mes = []
    for ev in eventos_gsheets:
        f_ev_str = str(ev.get("fecha", ""))
        try:
            f_ev_dt = datetime.strptime(f_ev_str, "%Y-%m-%d").date()
            if f_ev_dt.year == f_sel.year and f_ev_dt.month == f_sel.month:
                eventos_mes.append((f_ev_dt, ev))
        except Exception:
            pass
            
    eventos_mes.sort(key=lambda x: x[0])

    with st.expander(f"📱 **Ver todas las tareas del mes en lista ({len(eventos_mes)})**", expanded=False):
        if not eventos_mes:
            st.info("No hay tareas programadas para este mes.")
        else:
            for f_dt, ev_data in eventos_mes:
                cat_mes = ev_data.get("categoria", "") or ev_data.get("color", "💚 Verde - Confirmado")
                est_mes = PALETA_COLORES.get(cat_mes, PALETA_COLORES["💚 Verde - Confirmado"])
                
                st.markdown(f"""
                    <div style="background-color: {est_mes['bg']}; border-left: 5px solid {est_mes['border']}; color: {est_mes['text']}; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
                        <strong style="font-size: 1rem;">📅 {f_dt.strftime('%d/%m (%a)')} — {ev_data.get('title')}</strong><br>
                        ⏱️ {int(ev_data.get('inicio', 0)):02d}:00 - {int(ev_data.get('fin', 0)):02d}:00 hs
                        {f'<br>💬 {ev_data.get("nota")}' if ev_data.get("nota") else ''}
                    </div>
                """, unsafe_allow_html=True)

    st.divider()

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
        with st.expander(f"🔔 **Avisos de esta Semana ({inicio_sem_actual.strftime('%d/%m')} al {fin_sem_actual.strftime('%d/%m')})**", expanded=True):
            for f_dt, ev_data in eventos_semana:
                cat_aviso = ev_data.get("categoria", "") or ev_data.get("color", "💚 Verde - Confirmado")
                estilo_aviso = PALETA_COLORES.get(cat_aviso, PALETA_COLORES["💚 Verde - Confirmado"])
                st.markdown(f"""
                    <div style="background-color: {estilo_aviso['bg']}; border-left: 4px solid {estilo_aviso['border']}; color: {estilo_aviso['text']}; padding: 8px; border-radius: 6px; margin-bottom: 6px;">
                        <strong>📅 {f_dt.strftime('%d/%m (%a)')}: {ev_data.get('title')}</strong><br>
                        ⏱️ {int(ev_data.get('inicio', 0)):02d}:00 - {int(ev_data.get('fin', 0)):02d}:00 hs
                    </div>
                """, unsafe_allow_html=True)

    fechas_con_tareas = {str(e.get("fecha")) for e in eventos_gsheets if e.get("fecha")}

    st.markdown(f"<h3 style='text-align: center; color: #0284c7; margin-bottom: 5px;'>📅 Semana del {f_sel.strftime('%d/%m/%Y')}</h3>", unsafe_allow_html=True)

    col_nav1, col_hoy, col_nav2 = st.columns([1, 1, 1])
    if col_nav1.button("◄ Sem.", use_container_width=True):
        st.session_state["fecha_seleccionada"] -= timedelta(days=7)
        st.rerun()
    if col_hoy.button("📍 Hoy", use_container_width=True):
        st.session_state["fecha_seleccionada"] = date.today()
        st.rerun()
    if col_nav2.button("Sem. ►", use_container_width=True):
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
                    st.markdown("**Editar Tarea**")
                    with st.form(key=f"form_edit_ev_{id_ev}"):
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

                        if st.form_submit_button("💾 Guardar", type="primary", use_container_width=True):
                            if new_tit_input.strip():
                                titulo_final = f"{new_cap_opc} - {new_tit_input.strip()}" if new_cap_opc != "(Ninguna / Tarea General)" else new_tit_input.strip()
                            else:
                                titulo_final = new_cap_opc if new_cap_opc != "(Ninguna / Tarea General)" else "Tarea General"

                            cell = ws_eventos.find(id_ev)
                            if cell:
                                row_n = cell.row
                                ws_eventos.update_cell(row_n, 2, titulo_final)
                                ws_eventos.update_cell(row_n, 3, new_f_tarea.strftime("%Y-%m-%d"))
                                ws_eventos.update_cell(row_n, 4, int(new_h_i))
                                ws_eventos.update_cell(row_n, 5, int(new_h_f))
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

    st.divider()

    st.markdown("#### ➕ Agregar Nueva Tarea")
    with st.form("form_add_evento_col", clear_on_submit=True):
        f_tarea = st.date_input("Fecha:", value=f_sel)
        cap_opcional = st.selectbox("Capilla (Opcional):", options=OPCIONES_CAPILLA_FORM)
        tit_tarea_input = st.text_input("Título / Tarea:", placeholder="Ej: Limpieza profunda")
        cat_t = st.selectbox("Situación / Color:", options=list(PALETA_COLORES.keys()))
        nota_t = st.text_area("Detalle adicional", placeholder="Notas u observaciones...", height=68)
        
        c1, c2 = st.columns(2)
        h_i = c1.number_input("Inicio", min_value=7, max_value=20, value=8)
        h_f = c2.number_input("Fin", min_value=8, max_value=21, value=12)
        
        if st.form_submit_button("Guardar en Agenda", type="primary", use_container_width=True):
            if tit_tarea_input.strip():
                titulo_completo = f"{cap_opcional} - {tit_tarea_input.strip()}" if cap_opcional != "(Ninguna / Tarea General)" else tit_tarea_input.strip()
            else:
                titulo_completo = cap_opcional if cap_opcional != "(Ninguna / Tarea General)" else "Tarea General"

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
# 2. CHECKLIST DIGITAL Y DESCARGA DE PLANILLA WORD
# ==========================================
with tab_check:
    st.header("📝 Checklist Digital de Control")
    
    try:
        with open("planilla_base.docx", "rb") as archivo_word:
            st.download_button(
                label="📥 Descargar Planilla Base (Word)",
                data=archivo_word,
                file_name="Planilla_Base_Capillas.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
    except Exception:
        pass

    st.markdown("<br>", unsafe_allow_html=True)
    
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
# 3. RESUMEN DE CAPILLAS Y CONTROL DE INSPECCIÓN FOTOGRÁFICA
# ==========================================
with tab_capillas:
    st.header("⛪ Resumen de Capillas y Control de Inspección Fotográfica")
    
    registros_capillas = []
    if ws_resumen:
        try:
            registros_capillas = ws_resumen.get_all_records()
        except Exception:
            registros_capillas = []

    MESES_NOMBRES = {
        "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril", 
        "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto", 
        "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
    }
    
    col_mes_sel, col_mes_info = st.columns([1.5, 2])
    with col_mes_sel:
        mes_actual_num = datetime.now().strftime("%m")
        meses_opciones = ["10", "11", "12", "09", "08", "01", "02", "03", "04", "05", "06", "07"]
        
        mes_seleccionado = st.selectbox(
            "📅 Seleccionar mes a consultar/registrar:",
            options=meses_opciones,
            format_func=lambda x: f"{MESES_NOMBRES.get(x, x)} (Mes {x})",
            index=0
        )
    
    with col_mes_info:
        st.info(f"💡 Mostrando registros e informes del mes de **{MESES_NOMBRES.get(mes_seleccionado)}**.")

    st.divider()

    mapa_resumen = {}
    total_visitas_global = 0

    def obtener_clave_fecha(v_obj):
        txt = v_obj.get("texto", "")
        if " (" in txt:
            txt = txt.split(" (")[0]
        partes = txt.strip().split("/")
        if len(partes) >= 2 and partes[0].isdigit() and partes[1].isdigit():
            return (int(partes[1]), int(partes[0]))
        return (99, 99)

    for idx_r, r in enumerate(registros_capillas):
        cap = str(r.get("capilla", "")).strip()
        if cap:
            if cap not in mapa_resumen:
                mapa_resumen[cap] = {"estado": r.get("estado_planilla", "Pendiente"), "visitas": []}
            
            dias_str = str(r.get("dias_visitados", "")).strip()
            if dias_str:
                txt_fecha = dias_str.split(" (")[0].strip()
                partes_f = txt_fecha.split("/")
                mes_registro = partes_f[1].zfill(2) if len(partes_f) >= 2 and partes_f[1].isdigit() else mes_actual_num
                
                if mes_registro == mes_seleccionado:
                    mapa_resumen[cap]["visitas"].append({
                        "row_index": idx_r + 2,
                        "texto": dias_str
                    })
                    total_visitas_global += 1
            
            if r.get("estado_planilla"):
                mapa_resumen[cap]["estado"] = r.get("estado_planilla")

    for cap_nombre in mapa_resumen:
        mapa_resumen[cap_nombre]["visitas"].sort(key=obtener_clave_fecha)

# EXPORTACIÓN
    st.markdown("#### 📥 Exportar Reporte para Auditoría")
    filas_exportar = []
    for zona, capillas in ZONAS_CAPILLAS.items():
        for c in capillas:
            v_list = mapa_resumen.get(c, {}).get("visitas", [])
            fechas_str = ", ".join([v["texto"].split(" (por ")[0] for v in v_list]) if v_list else "Sin visitas"
            filas_exportar.append({
                "Zona": zona,
                "Capilla": c,
                "Estado Planilla": mapa_resumen.get(c, {}).get("estado", "Pendiente"),
                "Total Visitas": len(v_list),
                "Fechas de Visita": fechas_str
            })

    df_export = pd.DataFrame(filas_exportar)
    col_exp_excel, col_exp_pdf = st.columns(2)
    
    with col_exp_excel:
        buffer_excel = io.BytesIO()
        with pd.ExcelWriter(buffer_excel) as writer:
            df_export.to_excel(writer, sheet_name=f"Visitas_{MESES_NOMBRES.get(mes_seleccionado)}", index=False)
        
        st.download_button(
            label="📊 Descargar Informe en Excel (.xlsx)",
            data=buffer_excel.getvalue(),
            file_name=f"Reporte_Capillas_{MESES_NOMBRES.get(mes_seleccionado)}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with col_exp_pdf:
        with st.popover("🖨️ Vista Imprimible / Guardar PDF", use_container_width=True):
            st.markdown(f"### 📋 Auditoría de Visitas - {MESES_NOMBRES.get(mes_seleccionado)}")
            st.caption("Usa la opción de imprimir del navegador (Ctrl + P) y selecciona 'Guardar como PDF'.")
            st.dataframe(df_export, use_container_width=True, hide_index=True)

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
        st.markdown(f"""
            <div style="background-color: #fef2f2; border-left: 5px solid #ef4444; padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                <h4 style="margin:0 0 4px 0; color: #991b1b; font-size:1rem;">🔴 Capillas SIN visitas en {MESES_NOMBRES.get(mes_seleccionado)}</h4>
            </div>
        """, unsafe_allow_html=True)
        if not sin_visitas:
            st.success("¡Excelente! Todas las capillas recibieron al menos una visita este mes.")
        else:
            html_sin = "".join([f'<span class="badge-alerta-roja">⛪ {c}</span>' for c in sin_visitas])
            st.markdown(html_sin, unsafe_allow_html=True)

    with col_rep2:
        st.markdown(f"""
            <div style="background-color: #fefce8; border-left: 5px solid #eab308; padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                <h4 style="margin:0 0 4px 0; color: #854d0e; font-size:1rem;">💛 Capillas visitadas de 1 a 2 veces</h4>
            </div>
        """, unsafe_allow_html=True)
        if not pocas_visitas:
            st.info("No hay capillas en el rango de 1 a 2 visitas.")
        else:
            html_pocas = "".join([f'<span class="badge-alerta-amarilla">⛪ {c} ({cant} visita{"s" if cant > 1 else ""})</span>' for c, cant in pocas_visitas])
            st.markdown(html_pocas, unsafe_allow_html=True)

    st.divider()

    # 2. GENERADOR DE MENSAJE SEMANAL DE PRIORIDADES
    st.markdown("### 📩 Mensaje semanal de prioridades")
    col_saludo, col_vac = st.columns([1, 1])
    with col_saludo:
        saludo_tipo = st.selectbox("Saludo inicial:", ["Buenos días", "Buenas tardes", "Buenas noches"])
    
    CAPILLAS_INDIVIDUALES = ["Bella Vista", "Goya", "El Colorado", "La Leonesa", "San Martin"]

    # --- CUADRO 1: MENSAJE POR ZONAS (GRUPAL) ---
    lineas_zonas = [f"{saludo_tipo}, comparto el informe semanal de las capillas visitadas:\n"]
    
    for zona, capillas in ZONAS_CAPILLAS.items():
        capillas_grupales = [c for c in capillas if c not in CAPILLAS_INDIVIDUALES]
        if not capillas_grupales:
            continue

        lineas_zonas.append(f"📍 *{zona}*")
        capillas_no_visitadas_esta_semana = []
        
        for c in capillas_grupales:
            visitas = mapa_resumen.get(c, {}).get("visitas", [])
            if visitas:
                fechas_limpias = [v["texto"].split(" (por ")[0] for v in visitas]
                fechas_txt = ", ".join(fechas_limpias)
                lineas_zonas.append(f"• {c}: Visitada ({fechas_txt})")
                
                obs_fotos = st.session_state.get(f"faltantes_fotos_{c}", "").strip()
                if obs_fotos:
                    lineas_zonas.append(f"**FALTAN FOTOS:** {obs_fotos}")
            else:
                lineas_zonas.append(f"• {c}: Sin visitas registradas")
                capillas_no_visitadas_esta_semana.append(c)

        if capillas_no_visitadas_esta_semana:
            prioridad_rotacion = capillas_no_visitadas_esta_semana
        else:
            prioridad_rotacion = sorted(capillas_grupales, key=lambda x: len(mapa_resumen.get(x, {}).get("visitas", [])))[:2]
        
        if prioridad_rotacion:
            lineas_zonas.append(f"⚠️ *Prioridad para la próxima semana:* {', '.join(prioridad_rotacion)}")
        
        lineas_zonas.append("")

    lineas_zonas.append("📌 *Recordatorio: Se requiere un mínimo de 4 visitas mensuales por capilla.*")
    txt_zonas_completo = "\n".join(lineas_zonas)

    # --- CUADRO 2: COMUNICADOS DE SEGUIMIENTO INDIVIDUAL ---
    lineas_ind = [f"{saludo_tipo}, comparto el comunicado de seguimiento individual:\n"]
    for c_ind in CAPILLAS_INDIVIDUALES:
        visitas_ind = mapa_resumen.get(c_ind, {}).get("visitas", [])
        if visitas_ind:
            fechas_limpias_ind = [v["texto"].split(" (por ")[0] for v in visitas_ind]
            fechas_txt_ind = ", ".join(fechas_limpias_ind)
            lineas_ind.append(f"• {c_ind}: Visitada ({fechas_txt_ind})")
            
            obs_fotos_ind = st.session_state.get(f"faltantes_fotos_{c_ind}", "").strip()
            if obs_fotos_ind:
                lineas_ind.append(f"**FALTAN FOTOS:** {obs_fotos_ind}")
        else:
            lineas_ind.append(f"• {c_ind}: Sin visitas registradas")

    txt_ind_completo = "\n".join(lineas_ind)

    # --- CUADRO 3: UNIFICADO ---
    txt_unificado_completo = txt_zonas_completo.replace("📌 *Recordatorio: Se requiere un mínimo de 4 visitas mensuales por capilla.*", "").strip() + "\n\n" + "👤 *COMUNICADOS DE SEGUIMIENTO INDIVIDUAL*\n" + "\n".join(lineas_ind[1:]) + "\n\n📌 *Recordatorio: Se requiere un mínimo de 4 visitas mensuales por capilla.*"

    # RENDERIZADO DE LOS 3 CUADROS
    with st.expander("📄 **1. Copiar Informe por Zonas (Grupales)**", expanded=False):
        st.text_area("Texto listo para copiar (Zonas):", value=txt_zonas_completo, height=280, key="txt_area_zonas")

    with st.expander("👤 **2. Copiar Comunicados de Seguimiento Individual**", expanded=False):
        st.text_area("Texto listo para copiar (Seguimiento Individual):", value=txt_ind_completo, height=180, key="txt_area_ind")

    with st.expander("📋 **3. Copiar Informe Completo (Unificado)**", expanded=False):
        st.text_area("Texto listo para copiar (Completo):", value=txt_unificado_completo, height=340, key="txt_area_unificado")

    st.divider()

    # 3. DETALLE Y CONTROL DE INSPECCIÓN POR CAPILLA
    for zona, capillas in ZONAS_CAPILLAS.items():
        st.markdown(f"### 📍 {zona}")
        for c in capillas:
            data_capilla = mapa_resumen.get(c, {"estado": "Pendiente", "visitas": []})
            cant_v = len(data_capilla["visitas"])
            estado_actual = data_capilla["estado"]
            
            st.markdown(f"#### ⛪ {c} &nbsp;&nbsp;|&nbsp;&nbsp; <span style='font-size:0.9rem; color:#0284c7;'>📊 Visitas: <strong>{cant_v}</strong> | Planilla: <strong>{estado_actual}</strong></span>", unsafe_allow_html=True)
            
            col_est, col_add_v = st.columns([1, 1.5])
            
            with col_est:
                idx_default = ["Pendiente", "En Proceso", "Completado"].index(estado_actual) if estado_actual in ["Pendiente", "En Proceso", "Completado"] else 0
                nuevo_estado = st.selectbox("Estado de planilla", ["Pendiente", "En Proceso", "Completado"], index=idx_default, key=f"est_sel_{c}_{mes_seleccionado}")
                
                if nuevo_estado != estado_actual:
                    if ws_resumen:
                        ws_resumen.append_row([zona, c, nuevo_estado, ""])
                        st.success(f"Estado de {c} actualizado a {nuevo_estado}")
                        st.rerun()

            with col_add_v:
                nueva_fecha_v = st.text_input(f"➕ Registrar nueva visita ({MESES_NOMBRES.get(mes_seleccionado)}):", placeholder=f"Ej: 02/{mes_seleccionado}", key=f"in_fecha_{c}_{mes_seleccionado}")
                if st.button(f"📌 Registrar visita en {c}", key=f"btn_add_v_{c}_{mes_seleccionado}", use_container_width=True):
                    if nueva_fecha_v.strip() and ws_resumen:
                        ws_resumen.append_row([
                            zona, 
                            c, 
                            nuevo_estado, 
                            f"{nueva_fecha_v.strip()} (por {st.session_state['usuario_actual']})"
                        ])
                        st.success(f"¡Visita {nueva_fecha_v} guardada para {c}!")
                        st.rerun()

            with st.expander(f"📸 **Cargar / Editar Faltantes de Fotos para {c}**"):
                st.caption("Escribí los faltantes u observaciones técnicas para que se agreguen automáticamente al informe:")
                st.text_area(
                    "Faltantes y Observaciones (Ej: Veredas: perfilado. Cerco olímpico - Drenaje):",
                    key=f"faltantes_fotos_{c}",
                    placeholder="Ej: Veredas: No cumple con las condiciones, por favor perfilarlas. Cerco olímpico - Drenaje - Gestión de residuos",
                    height=80
                )

            st.markdown(f"📅 **Días visitados en {MESES_NOMBRES.get(mes_seleccionado)}:**")
            if not data_capilla["visitas"]:
                st.caption(f"Aún no hay visitas registradas en {MESES_NOMBRES.get(mes_seleccionado)}.")
            else:
                for v_info in data_capilla["visitas"]:
                    c_badge, c_del = st.columns([4, 1])
                    with c_badge:
                        st.markdown(f'<span class="badge-visita">✔ {v_info["texto"]}</span>', unsafe_allow_html=True)
                    with c_del:
                        if st.button("🗑️ Borrar", key=f"del_v_{c}_{v_info['row_index']}_{mes_seleccionado}"):
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
    st.header("📌 Recordatorios Rápidos")
    
    try:
        recs_gsheets = ws_recordatorios.get_all_records()
    except Exception:
        recs_gsheets = []

    with st.form("form_add_rec"):
        txt_rec = st.text_input("Agregar recordatorio:")
        prio_rec = st.selectbox("Prioridad:", OPCIONES_PRIORIDAD_RECORDATORIO)
        if st.form_submit_button("📌 Guardar Recordatorio", type="primary"):
            if txt_rec.strip():
                ws_recordatorios.append_row([str(uuid.uuid4()), txt_rec.strip(), prio_rec, datetime.now().strftime("%Y-%m-%d %H:%M")])
                st.success("¡Recordatorio guardado!")
                st.rerun()

    st.divider()
    if not recs_gsheets:
        st.info("No hay recordatorios pendientes.")
    else:
        for r in recs_gsheets:
            st.markdown(f"""
                <div class="card-note">
                    <strong>📌 {r.get('texto')}</strong><br>
                    <small>Prioridad: {r.get('prioridad', 'Normal')} | {r.get('fecha', '')}</small>
                </div>
            """, unsafe_allow_html=True)
            if st.button("🗑️ Eliminar", key=f"del_rec_{r.get('id')}"):
                cell = ws_recordatorios.find(str(r.get('id')))
                if cell:
                    ws_recordatorios.delete_rows(cell.row)
                st.rerun()

# ==========================================
# 5. GMAIL / OT TRACKING
# ==========================================
with tab_gmail:
    st.header("✉️ Seguimiento de Correos y OTs")
    
    try:
        mails_gsheets = ws_gmail.get_all_records() if ws_gmail else []
    except Exception:
        mails_gsheets = []

    if not mails_gsheets:
        st.info("No hay correos registrados en la base de datos.")
    else:
        st.dataframe(pd.DataFrame(mails_gsheets), use_container_width=True)
