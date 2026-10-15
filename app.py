import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date, timedelta
import uuid
import gspread
from google.oauth2.service_account import Credentials
import json
import tempfile
import os

# Configuración de la conexión a Google Sheets usando los Secrets de Streamlit de forma segura
@st.cache_resource
def init_connection():
    import re
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    raw = st.secrets["gcp_json"].strip()
    raw = re.sub(r",\s*}", "}", raw)  # tolera una coma de más antes de la llave final
    try:
        creds_dict = json.loads(raw, strict=False)
    except json.JSONDecodeError as e:
        st.error("El JSON de los Secrets tiene un error: " + e.msg + ". Línea " + str(e.lineno) + ", columna " + str(e.colno) + ".")
        st.stop()
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)
    
# Conectarse a la planilla y abrir las solapas
client = init_connection()
sheet = client.open_by_key("12zw7JZ3cHMg7wKZWMTsfJmmWrpP4DDjLN9K2K_w715w")

ws_recordatorios = sheet.worksheet("recordatorios")
ws_eventos = sheet.worksheet("eventos")

# Configuración de página
st.set_page_config(
    page_title="Agenda de Capillas - Sistema Privado",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 🔐 MÓDULO DE AUTENTICACIÓN Y LOGIN SEGURO
# ==========================================
USUARIOS_AUTORIZADOS = {
    "admin": "capillas2026",
    "trabajador1": "clave123",
    "encargado": "parroquia2026",
    "Silvia": "Caceresythomas123"
    "Luzmi": "Caceresythomas123"
}

if "usuario_autenticado" not in st.session_state:
    st.session_state["usuario_autenticado"] = False

if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = ""

if not st.session_state["usuario_autenticado"]:
    st.markdown("""
        <style>
        .login-box {
            max-width: 420px;
            margin: 60px auto;
            padding: 30px;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border: 1px solid #cbd5e1;
            text-align: center;
        }
        @media (max-width: 768px) {
            .login-box {
                margin: 20px auto;
                padding: 20px;
            }
        }
        </style>
    """, unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    with col_l2:
        st.markdown("## 🔒 Acceso Restringido")
        st.write("Sistema Interno de Gestión de Capillas")
        
        with st.form("form_login_privado", clear_on_submit=False):
            usr_input = st.text_input("👤 Usuario", placeholder="Ingrese su usuario")
            pass_input = st.text_input("🔑 Contraseña", type="password", placeholder="Ingrese su contraseña")
            btn_login = st.form_submit_button("Ingresar al Sistema", type="primary", use_container_width=True)
            
            if btn_login:
                usr_clean = usr_input.strip()
                pass_clean = pass_input.strip()
                
                if usr_clean in USUARIOS_AUTORIZADOS and USUARIOS_AUTORIZADOS[usr_clean] == pass_clean:
                    st.session_state["usuario_autenticado"] = True
                    st.session_state["usuario_actual"] = usr_clean
                    st.success("¡Acceso concedido!")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")
                    
    st.stop()

c_usr_info, c_logout = st.columns([4, 1])
with c_usr_info:
    st.caption(f"👤 Sesión activa: **{st.session_state['usuario_actual']}** (Acceso Autorizado)")
with c_logout:
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state["usuario_autenticado"] = False
        st.session_state["usuario_actual"] = ""
        st.rerun()

st.divider()

# ==========================================
# CONFIGURACIÓN GENERAL Y ESTADOS
# ==========================================
PALETA_COLORES = {
    "💚 Verde - Confirmado": {"bg": "#d1e7dd", "border": "#0f5132", "text": "#0f5132"},
    "💙 Azul - En proceso": {"bg": "#cff4fc", "border": "#055160", "text": "#055160"},
    "💜 Violeta - Especial": {"bg": "#e2d9f3", "border": "#593196", "text": "#593196"},
    "💛 Amarillo - Pendiente": {"bg": "#fff3cd", "border": "#664d03", "text": "#664d03"},
    "🩷 Rosa - Alerta": {"bg": "#f8d7da", "border": "#842029", "text": "#842029"}
}

CAPILLAS_DEFAULT = [
    "Barrio 1", "Barrio 2", "Barrio 3", "Barrio 4", 
    "Alberdi", "Güiraldes", "Puerto Tirol"
]

MESES_ESP = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
MESES_ESP_CORTO = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

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

if "lista_capillas" not in st.session_state:
    st.session_state["lista_capillas"] = CAPILLAS_DEFAULT.copy()

if "fecha_seleccionada" not in st.session_state:
    st.session_state["fecha_seleccionada"] = date.today()

if "respuestas_checklist" not in st.session_state:
    st.session_state["respuestas_checklist"] = {}

if "observaciones_checklist" not in st.session_state:
    st.session_state["observaciones_checklist"] = {}

if "fotos_checklist" not in st.session_state:
    st.session_state["fotos_checklist"] = {}

if "tareas_personalizadas" not in st.session_state:
    st.session_state["tareas_personalizadas"] = {}

# ESTILOS CSS CON RESPONSIVE DESIGN PARA CELULAR
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

    .card-note {
        background-color: #ffffff;
        border-left: 5px solid #0284c7;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .day-header {
        text-align: center;
        font-weight: bold;
        font-size: 0.88rem;
        color: #334155;
    }
    
    .day-num-hoy {
        font-size: 1.1rem;
        font-weight: bold;
        color: #0284c7;
        border: 2px solid #0284c7;
        background-color: #e0f2fe;
        border-radius: 50%;
        padding: 2px 8px;
        display: inline-block;
    }
    
    .day-num-selected {
        font-size: 1.1rem;
        font-weight: bold;
        color: #ffffff;
        background-color: #0284c7;
        border-radius: 50%;
        padding: 2px 8px;
        display: inline-block;
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

    /* ESTILOS ESPECÍFICOS PARA DISPOSITIVOS MÓVILES (< 768px) */
    @media (max-width: 768px) {
        .block-evento {
            font-size: 0.95rem !important;
            padding: 12px !important;
            margin-bottom: 10px !important;
        }
        .card-note {
            padding: 14px !important;
            margin-bottom: 14px !important;
        }
        button {
            min-height: 44px !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            overflow-x: auto;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 12px;
            font-size: 0.85rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# SELECTOR DE VISTA
st.radio(
    "🖥️ Vista optimizada para:",
    ["💻 Computadora", "📱 Celular"],
    horizontal=True,
    key="selector_modo_dispositivo"
)

# PESTAÑAS PRINCIPALES
tab_cal, tab_check, tab_capillas, tab_notes = st.tabs([
    "📅 1. Agenda Principal", 
    "📝 2. Checklist Digital", 
    "⛪ 3. Resumen de Capillas",
    "📌 4. Recordatorios Rápidos"
])

# ==========================================
# VISTA COMPUTADORA (INTACTA)
# ==========================================
def render_agenda_desktop():
    f_sel = st.session_state["fecha_seleccionada"]
    f_sel_str = f_sel.strftime("%Y-%m-%d")
    hoy_real = date.today()

    eventos_desde_gsheets = ws_eventos.get_all_records()

    col_grilla, col_panel_derecho = st.columns([3.5, 1.1], gap="medium")

    with col_grilla:
        c_act, c_nav_l, c_titulo_m, c_nav_r, _ = st.columns([1, 0.4, 2.5, 0.4, 1])
        
        if c_act.button("Hoy", use_container_width=True, key="btn_hoy_desk"):
            st.session_state["fecha_seleccionada"] = hoy_real
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

        cols_hdr = st.columns([0.6] + [1.8]*7)
        cols_hdr[0].write("")
        
        dias_nombres = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        for idx, d_f in enumerate(dias_semana):
            es_hoy = (d_f == hoy_real)
            es_seleccionado = (d_f == f_sel)
            
            if es_seleccionado:
                clase_num = "day-num-selected"
            elif es_hoy:
                clase_num = "day-num-hoy"
            else:
                clase_num = "day-num-inactive"
            
            badge_mes = ""
            if d_f.day == 1 or idx == 0:
                badge_mes = f"<br><span class='month-badge'>{MESES_ESP_CORTO[d_f.month-1]}</span>"

            cols_hdr[idx+1].markdown(
                f"<div class='day-header'>{dias_nombres[idx]}<br><span class='{clase_num}'>{d_f.day}</span>{badge_mes}</div>", 
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        for hora in range(8, 17):
            cols_h = st.columns([0.6] + [1.8]*7)
            cols_h[0].markdown(f"<span style='color:#64748b; font-size:0.75rem; font-weight:600;'>{hora:02d}:00</span>", unsafe_allow_html=True)
            
            for idx, d_f in enumerate(dias_semana):
                d_str = d_f.strftime("%Y-%m-%d")
                evs_h = [e for e in eventos_desde_gsheets if str(e.get("fecha")) == d_str and int(e.get("inicio", 0)) == hora]
                
                with cols_h[idx+1]:
                    if evs_h:
                        for ev in evs_h:
                            st.markdown(f"""
                                <div class="block-evento" style="background-color: #d1e7dd; color: #0f5132; border-left-color: #0f5132; font-size:0.75rem;">
                                    {ev['title']}<br>
                                    <span style="font-size:0.68rem; opacity:0.85;">⏱️ {int(ev['inicio']):02d}:00 - {int(ev['fin']):02d}:00 hs</span>
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
                        ws_eventos.append_row([
                            str(uuid.uuid4()),
                            tit_t.strip(),
                            f_t.strftime("%Y-%m-%d"),
                            int(h_i),
                            int(h_f),
                            nota_t.strip()
                        ])
                        st.session_state["fecha_seleccionada"] = f_t
                        st.success("¡Agendado en Google Sheets!")
                        st.rerun()
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

    col_cap_input, col_tipo_sel = st.columns([1, 1])
    with col_cap_input:
        capilla_manual = st.text_input("✍️ Nombre de la Capilla:", placeholder="Escribir nombre de la capilla...")
        capilla_lista = st.selectbox("O seleccionar de la lista:", st.session_state["lista_capillas"], key="chk_cap_sel")
        capilla_trabajo = capilla_manual.strip() if capilla_manual.strip() else capilla_lista

    with col_tipo_sel:
        tipo_checklist = st.radio("Tipo de Inspección:", ["🧹 Limpieza", "🌿 Jardinería"], horizontal=True, key="chk_tipo_sel")

    clave_base = f"{f_sel_str}_{capilla_trabajo}_{tipo_checklist}"
    
    if clave_base not in st.session_state["respuestas_checklist"]:
        st.session_state["respuestas_checklist"][clave_base] = {}
    if clave_base not in st.session_state["observaciones_checklist"]:
        st.session_state["observaciones_checklist"][clave_base] = {}
    if clave_base not in st.session_state["fotos_checklist"]:
        st.session_state["fotos_checklist"][clave_base] = {}
    if clave_base not in st.session_state["tareas_personalizadas"]:
        st.session_state["tareas_personalizadas"][clave_base] = []

    st.markdown(f"### Revisión: **{capilla_trabajo}** ({f_sel.strftime('%d/%m/%Y')})")
    
    def render_fila_item(item_nombre):
        st.markdown(f"**{item_nombre}**")
        
        v_act = st.session_state["respuestas_checklist"][clave_base].get(item_nombre, False)
        chk = st.checkbox("Realizado / Completado", value=v_act, key=f"chk_{clave_base}_{item_nombre}")
        st.session_state["respuestas_checklist"][clave_base][item_nombre] = chk
        
        obs_act = st.session_state["observaciones_checklist"][clave_base].get(item_nombre, "")
        obs_val = st.text_input("Observación:", value=obs_act, key=f"obs_{clave_base}_{item_nombre}", placeholder="Detalles u observaciones...")
        st.session_state["observaciones_checklist"][clave_base][item_nombre] = obs_val
            
        foto_subida = st.file_uploader("📷 Adjuntar Foto:", type=["png", "jpg", "jpeg"], key=f"foto_{clave_base}_{item_nombre}")
        if foto_subida is not None:
            st.session_state["fotos_checklist"][clave_base][item_nombre] = foto_subida
            st.image(foto_subida, caption="Foto adjunta", width=160)

    if "Limpieza" in tipo_checklist:
        for cat, items in PDF_CHECKLIST_ITEMS.items():
            with st.expander(cat, expanded=True):
                for item in items:
                    render_fila_item(item)
                    st.markdown("<hr style='margin: 8px 0; border-top: 1px dashed #cbd5e1;'>", unsafe_allow_html=True)
    else:
        with st.expander("🌿 Jardinería y Exteriores", expanded=True):
            for item in CHECKLIST_JARDINERIA_DEFAULT:
                render_fila_item(item)
                st.markdown("<hr style='margin: 8px 0; border-top: 1px dashed #cbd5e1;'>", unsafe_allow_html=True)

    st.markdown("---")
    with st.popover("➕ Añadir tarea personalizada al checklist", use_container_width=True):
        st.markdown("#### Nueva Tarea Extra")
        nueva_tarea_nom = st.text_input("Nombre de la tarea adicional:", placeholder="Ej: Reparar foco del altar")
        if st.button("Guardar Tarea Extra", type="primary", use_container_width=True):
            if nueva_tarea_nom.strip():
                st.session_state["tareas_personalizadas"][clave_base].append(nueva_tarea_nom.strip())
                st.success("¡Tarea personalizada agregada!")
                st.rerun()

    if st.session_state["tareas_personalizadas"][clave_base]:
        with st.expander("⭐ Tareas Personalizadas Agregadas", expanded=True):
            for t_custom in st.session_state["tareas_personalizadas"][clave_base]:
                render_fila_item(f"📌 {t_custom}")
                st.markdown("<hr style='margin: 8px 0; border-top: 1px dashed #cbd5e1;'>", unsafe_allow_html=True)

    st.markdown("#### 💬 Observaciones Generales de la Inspección")
    obs_gen_val = st.text_area("Notas generales:", placeholder="Comentarios finales...", key=f"obs_gen_{clave_base}")

# ==========================================
# 3. PESTAÑA RESUMEN DE CAPILLAS
# ==========================================
with tab_capillas:
    st.header("⛪ Resumen de Capillas")
    for c in st.session_state["lista_capillas"]:
        st.subheader(c)
        st.selectbox(f"Estado de {c}:", ["Pendiente", "En Proceso", "Completado"], key=f"est_{c}")
        st.divider()

# ==========================================
# 4. PESTAÑA RECORDATORIOS RÁPIDOS
# ==========================================
with tab_notes:
    st.header("📌 Bloc de Notas y Recordatorios Rápidos")
    st.caption("Anotá pendientes generales, avisos o recordatorios sin asignarle un día u horario específico.")

    with st.form("form_nueva_nota_libre", clear_on_submit=True):
        titulo_nota = st.text_input("📌 Recordatorio / Nota:", placeholder="Ej: Comprar bolsas de residuos para la capilla Alberdi")
        detalle_nota = st.text_area("✍️ Detalle adicional (opcional):", placeholder="Ej: Pedir en la ferretería de la esquina", height=80)
        prioridad_nota = st.selectbox("Prioridad / Color:", ["💛 Normal", "🩷 Urgente / Importante", "💚 Idea / Nota"])
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
            st.success("¡Recordatorio guardado en Google Sheets!")
            st.rerun()

    st.divider()
    
    recordatorios_desde_gsheets = ws_recordatorios.get_all_records()
    
    st.subheader(f"📋 Recordatorios Guardados ({len(recordatorios_desde_gsheets)})")

    if not recordatorios_desde_gsheets:
        st.info("No hay recordatorios pendientes. Podés agregar uno arriba.")
    else:
        mapa_colores_notas = {
            "💛 Normal": {"border": "#eab308", "bg": "#fefce8"},
            "🩷 Urgente / Importante": {"border": "#ef4444", "bg": "#fef2f2"},
            "💚 Idea / Nota": {"border": "#22c55e", "bg": "#f0fdf4"}
        }

        for idx, nota in enumerate(recordatorios_desde_gsheets):
            tit_txt = nota.get("titulo", "Sin título")
            det_txt = nota.get("detalle", "")
            prio_txt = nota.get("prioridad", "💛 Normal")
            autor_txt = nota.get("creado_por", "Sistema")
            fecha_txt = nota.get("fecha_creacion", "")
            id_txt = str(nota.get("id", ""))

            c_info = mapa_colores_notas.get(prio_txt, {"border": "#0284c7", "bg": "#ffffff"})
            
            with st.container():
                st.markdown(f"""
                    <div class="card-note" style="border-left-color: {c_info['border']}; background-color: {c_info['bg']};">
                        <h4 style="margin:0 0 6px 0; color:#1e293b;">{tit_txt}</h4>
                        <p style="margin:0 0 8px 0; color:#475569; font-size:0.9rem;">{det_txt}</p>
                        <span style="font-size:0.75rem; color:#64748b;">
                            👤 Creado por <strong>{autor_txt}</strong> | 🕒 {fecha_txt}
                        </span>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("✔️ Marcar como resuelto / Borrar", key=f"btn_del_nota_{idx}_{id_txt}", use_container_width=True):
                    if id_txt:
                        cell = ws_recordatorios.find(id_txt)
                        if cell:
                            ws_recordatorios.delete_rows(cell.row)
                    st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)
