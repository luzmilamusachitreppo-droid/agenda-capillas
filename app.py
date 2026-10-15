import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import uuid
import gspread
from google.oauth2.service_account import Credentials
import json

# Configuración de página
st.set_page_config(
    page_title="Agenda de Capillas - Sistema Privado",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Conexión a Google Sheets
@st.cache_resource
def init_connection():
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
    return gspread.authorize(creds)

client = init_connection()
sheet = client.open_by_key("12zw7JZ3cHMg7wKZWMTsfJmmWrpP4DDjLN9K2K_w715w")

ws_recordatorios = sheet.worksheet("recordatorios")
ws_eventos = sheet.worksheet("eventos")

# Autenticación actualizada con los nuevos usuarios
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

# Encabezado
c_usr, c_out = st.columns([3, 1])
with c_usr:
    st.caption(f"👤 Sesión activa: **{st.session_state['usuario_actual']}**")
with c_out:
    if st.button("🚪 Cerrar", use_container_width=True):
        st.session_state["usuario_autenticado"] = False
        st.rerun()

st.divider()

# Listado ordenado por zonas de tus capillas
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

# Lista plana de todas las capillas para los selectores
todas_las_capillas = []
for z, caps in ZONAS_CAPILLAS.items():
    todas_las_capillas.extend(caps)

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
    </style>
""", unsafe_allow_html=True)

tab_cal, tab_check, tab_capillas, tab_notes = st.tabs([
    "📅 1. Agenda Principal", 
    "📝 2. Checklist Digital", 
    "⛪ 3. Resumen de Capillas",
    "📌 4. Recordatorios Rápidos"
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
                cat_ev = ev.get("categoria", "💚 Verde - Confirmado")
                estilo = PALETA_COLORES.get(cat_ev, PALETA_COLORES["💚 Verde - Confirmado"])
                
                st.markdown(f"""
                    <div style="background-color: {estilo['bg']}; border-left: 5px solid {estilo['border']}; padding: 12px; border-radius: 8px; margin-bottom: 8px; color: {estilo['text']};">
                        <strong>{ev.get('title', 'Sin Título')}</strong><br>
                        ⏱️ {int(ev.get('inicio', 0)):02d}:00 - {int(ev.get('fin', 0)):02d}:00 hs
                        {f'<br>💬 {ev.get("nota")}' if ev.get("nota") else ''}
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("🗑️ Borrar", key=f"del_ev_{ev.get('id')}", use_container_width=True):
                    cell = ws_eventos.find(str(ev.get('id')))
                    if cell:
                        ws_eventos.delete_rows(cell.row)
                    st.rerun()

    with col_der:
        st.markdown("#### ➕ Agregar Tarea")
        with st.form("form_add_evento_col", clear_on_submit=True):
            f_tarea = st.date_input("Fecha:", value=f_sel)
            tit_t = st.selectbox("Capilla / Tarea:", options=todas_las_capillas)
            cat_t = st.selectbox("Situación / Color:", options=list(PALETA_COLORES.keys()))
            nota_t = st.text_area("Detalle adicional", placeholder="Notas...", height=68)
            
            c1, c2 = st.columns(2)
            h_i = c1.number_input("Inicio", min_value=7, max_value=20, value=8)
            h_f = c2.number_input("Fin", min_value=8, max_value=21, value=12)
            
            if st.form_submit_button("Guardar en Agenda", type="primary", use_container_width=True):
                if tit_t.strip():
                    ws_eventos.append_row([
                        str(uuid.uuid4()),
                        tit_t.strip(),
                        f_tarea.strftime("%Y-%m-%d"),
                        int(h_i),
                        int(h_f),
                        nota_t.strip(),
                        cat_t
                    ])
                    st.session_state["fecha_seleccionada"] = f_tarea
                    st.success("¡Agregado con éxito!")
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
# 3. RESUMEN DE CAPILLAS (ORGANIZADO POR ZONAS)
# ==========================================
with tab_capillas:
    st.header("⛪ Resumen de Capillas por Zona")
    
    for zona, capillas in ZONAS_CAPILLAS.items():
        st.markdown(f"### 📍 {zona}")
        for c in capillas:
            col_cap, col_est = st.columns([2, 1])
            with col_cap:
                st.write(f"• **{c}**")
            with col_est:
                st.selectbox(f"Estado {c}", ["Pendiente", "En Proceso", "Completado"], key=f"est_{c}", label_visibility="collapsed")
        st.divider()

# ==========================================
# 4. RECORDATORIOS RÁPIDOS
# ==========================================
with tab_notes:
    st.markdown("## 📌 Recordatorios")

    with st.form("form_nueva_nota_libre", clear_on_submit=True):
        titulo_nota = st.text_input("Nota:", placeholder="Ej: Comprar bolsas de residuos para la capilla Alberdi")
        detalle_nota = st.text_area("Detalle:", placeholder="Ej: Pedir en la ferretería de la esquina", height=80)
        prioridad_nota = st.selectbox("Prioridad:", ["💛 Normal", "🩷 Urgente / Importante", "💚 Idea / Nota"])
        btn_guardar_nota = st.form_submit_button("➕ Añadir", type="primary", use_container_width=True)

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
            "💛 Normal": {"border": "#eab308", "bg": "#fefce8"},
            "🩷 Urgente / Importante": {"border": "#ef4444", "bg": "#fef2f2"},
            "💚 Idea / Nota": {"border": "#22c55e", "bg": "#f0fdf4"}
        }

        for idx, nota in enumerate(recs):
            tit = nota.get("titulo", "Sin título")
            det = nota.get("detalle", "")
            prio = nota.get("prioridad", "💛 Normal")
            autor = nota.get("creado_por", "Sistema")
            fec = nota.get("fecha_creacion", "")
            id_n = str(nota.get("id", ""))

            c_info = mapa_colores_notas.get(prio, {"border": "#0284c7", "bg": "#ffffff"})
            
            with st.container():
                st.markdown(f"""
                    <div class="card-note" style="border-left-color: {c_info['border']}; background-color: {c_info['bg']};">
                        <h4 style="margin:0 0 6px 0; color:#1e293b;">{tit}</h4>
                        <p style="margin:0 0 8px 0; color:#475569; font-size:0.9rem;">{det}</p>
                        <span style="font-size:0.75rem; color:#64748b;">
                            👤 Creado por <strong>{autor}</strong> | 🕒 {fec}
                        </span>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("Borrar", key=f"btn_del_nota_{idx}_{id_n}", use_container_width=True):
                    if id_n:
                        cell = ws_recordatorios.find(id_n)
                        if cell:
                            ws_recordatorios.delete_rows(cell.row)
                    st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)
