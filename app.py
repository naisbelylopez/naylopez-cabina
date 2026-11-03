from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Nay López Skincare",
    page_icon="✨",
    layout="wide",
)

# ============================================
# ESTILO VISUAL ELEGANTE (TIPO APP MODERNA)
# ============================================
st.markdown("""
    <style>
    .stApp {
        background-color: #0e0e10;
        color: #f3f4f6;
    }
    div.stMetric, div.stTabs, div.stForm {
        background-color: #18181b;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #27272a;
    }
    .stButton>button {
        background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        box-shadow: 0 4px 12px rgba(168, 85, 247, 0.3);
    }
    .stButton>button:hover {
        opacity: 0.9;
        color: white;
    }
    section[data-testid="stSidebar"] {
        background-color: #121215;
        border-right: 1px solid #27272a;
    }
    h1, h2, h3 {
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)


# ============================================
# CONEXIÓN SEGURA CON GOOGLE SHEETS
# ============================================
def conectar_google_sheets():
  scope = [
      "https://www.googleapis.com/auth/spreadsheets",
      "https://www.googleapis.com/auth/drive",
  ]
  creds_dict = dict(st.secrets["gcp_service_account"])
  creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
  client = gspread.authorize(creds)
  sheet = client.open("NayLopez_Cabina_DB").sheet1
  return sheet


try:
  sh = conectar_google_sheets().spreadsheet
  ws_clientes = sh.worksheet("Clientes")
  ws_inventario = sh.worksheet("Inventario")
  ws_finanzas = sh.worksheet("Finanzas")
  ws_citas = sh.worksheet("Citas")
except Exception:
  sh = conectar_google_sheets().spreadsheet
  ws_clientes = sh.add_worksheet(title="Clientes", rows="100", cols="20")
  ws_inventario = sh.add_worksheet(title="Inventario", rows="100", cols="20")
  ws_finanzas = sh.add_worksheet(title="Finanzas", rows="100", cols="20")
  ws_citas = sh.add_worksheet(title="Citas", rows="100", cols="20")

# ============================================
# MENÚ LATERAL (ESTILO DE LA REFERENCIA)
# ============================================
st.sidebar.title("✨ Nay López Skincare")
st.sidebar.markdown("Panel de Control Profesional")
st.sidebar.markdown("---")

menu = st.sidebar.selectbox(
    "Menú Principal",
    [
        "📊 Dashboard Principal",
        "📅 Agenda",
        "🧴 Servicios",
        "👥 Clientes",
        "👩‍⚕️ Historia Clínica",
        "💰 Finanzas",
        "📦 Inventario de Productos",
    ],
)

# ============================================
# 1. DASHBOARD PRINCIPAL
# ============================================
if menu == "📊 Dashboard Principal":
  st.title("Dashboard Principal - Nay López Skincare")
  st.markdown("### ✨ Turnos, servicios y seguimiento de clientas.")

  try:
    total_pacientes = len(ws_clientes.get_all_records())
  except:
    total_pacientes = 0

  try:
    total_inventario = len(ws_inventario.get_all_records())
  except:
    total_inventario = 0

  try:
    finanzas_data = ws_finanzas.get_all_records()
    ingresos = sum([float(x.get("Monto", 0)) for x in finanzas_data if x.get("Tipo") == "Ingreso"]) if finanzas_data else 0.0
    egresos = sum([float(x.get("Monto", 0)) for x in finanzas_data if x.get("Tipo") == "Gasto"]) if finanzas_data else 0.0
  except:
    ingresos, egresos = 0.0, 0.0

  col1, col2, col3, col4 = st.columns(4)
  col1.metric("👥 Total Clientes", total_pacientes)
  col2.metric("📦 Productos", total_inventario)
  col3.metric("💰 Ingresos", f"${ingresos:.2f}")
  col4.metric("📉 Egresos", f"${egresos:.2f}")

  st.divider()
  st.info("💡 **Bienvenida a tu estudio.** Utiliza el menú lateral para navegar por los diferentes módulos de gestión.")

# ============================================
# 2. AGENDA
# ============================================
elif menu == "📅 Agenda":
  st.title("Agenda de Citas y Turnos")
  st.markdown("Organiza y programa la atención de tus clientas en cabina.")

  tab1, tab2 = st.tabs(["Agendar Turno", "Ver Calendario"])

  with tab1:
    with st.form("form_citas", clear_on_submit=True):
      col1, col2 = st.columns(2)
      with col1:
        nom_c = st.text_input("Nombre de la Clienta")
        fec_c = st.date_input("Fecha del Turno")
        hor_c = st.time_input("Hora del Turno")
      with col2:
        trat_c = st.selectbox("Servicio / Tratamiento", ["Hydra Glow Detox", "Peeling Químico / Enzimático", "Dermapen", "Tratamiento Corporal"])
        est_c = st.selectbox("Estado", ["Agendada", "Confirmada", "Atendida", "Cancelada"])
      
      obs_c = st.text_area("Observaciones del turno")
      if st.form_submit_button("Guardar Turno"):
        if nom_c:
          ws_citas.append_row([str(fec_c), str(hor_c), nom_c, trat_c, est_c, obs_c])
          st.success(f"¡Turno agendado con éxito para {nom_c}!")
        else:
          st.warning("Ingresa el nombre de la clienta.")

  with tab2:
    st.subheader("📅 Turnos Registrados")
    try:
      data_c = ws_citas.get_all_records()
      if data_c:
        st.dataframe(pd.DataFrame(data_c), use_container_width=True)
      else:
        st.info("No hay turnos registrados en la agenda.")
    except:
      st.info("Agrega tu primer turno para visualizar la agenda.")

# ============================================
# 3. SERVICIOS
# ============================================
elif menu == "🧴 Servicios":
  st.title("Catálogo de Servicios y Protocolos")
  st.markdown("Gestiona los tratamientos que ofreces, sus sesiones y rutinas asociadas.")

  st.info("✨ **Tus protocolos activos en cabina:**")
  col_s1, col_s2 = st.columns(2)
  with col_s1:
    st.markdown("### 💎 Hydra Glow Detox")
    st.write("**Descripción:** Limpieza profunda e hidratación extrema.")
    st.write("**Sesiones:** 1 sesión (Mantenimiento mensual).")
    st.write("**Precio Sugerido:** $35.00")
    
    st.markdown("### 🌿 Control de Acné")
    st.write("**Descripción:** Tratamiento seborregulador y bacteriostático.")
    st.write("**Sesiones:** 4 sesiones (1 por semana).")
    st.write("**Precio Sugerido:** $120.00")

  with col_s2:
    st.markdown("### 🌸 Tratamiento de Manchas")
    st.write("**Descripción:** Despigmentación gradual con activos seguros.")
    st.write("**Sesiones:** 5 sesiones (cada 15 días).")
    st.write("**Precio Sugerido:** $140.00")

    st.markdown("### 🪄 Dermapen (Rejuvenecimiento)")
    st.write("**Descripción:** Inducción de colágeno con microagujas.")
    st.write("**Sesiones:** 3 sesiones (cada 21 días).")
    st.write("**Precio Sugerido:** $150.00")

# ============================================
# 4. CLIENTES
# ============================================
elif menu == "👥 Clientes":
  st.title("Gestión de Clientes")
  st.markdown("Directorio general de clientas registradas en tu estudio.")

  try:
    data_cli = ws_clientes.get_all_records()
    if data_cli:
      df_cli = pd.DataFrame(data_cli)
      # Mostramos columnas principales para el directorio
      cols_mostrar = [c for c in ["Fecha", "Nombre", "Cedula", "Telefono", "Email", "Ocupacion"] if c in df_cli.columns]
      st.dataframe(df_cli[cols_mostrar], use_container_width=True)
    else:
      st.info("Aún no hay clientas registradas. Dirígete a 'Historia Clínica' para dar de alta la primera.")
  except:
    st.info("Registra tu primera clienta para visualizar el listado.")

# ============================================
# 5. HISTORIA CLÍNICA
# ============================================
elif menu == "👩‍⚕️ Historia Clínica":
  st.title("Historia Clínica y Evaluación")
  st.markdown("Registro detallado de antecedentes, tipo de piel, lesiones y seguridad en cabina.")

  with st.form("form_hc", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
      nombre = st.text_input("Nombre y Apellido")
      cedula = st.text_input("Cédula de Identidad")
      telefono = st.text_input("Número de Contacto / WhatsApp")
      email = st.text_input("Correo Electrónico")
      ocupacion = st.text_input("Ocupación")
    with col2:
      st.markdown("**Tipos de Piel:**")
      p_eud = st.checkbox("Eudérmica")
      p_sec = st.checkbox("Seca")
      p_gra = st.checkbox("Grasa")
      p_mix = st.checkbox("Mixta")
      p_ali = st.checkbox("Alipica")
      p_des = st.checkbox("Deshidratada")
      p_sen = st.checkbox("Sensible")

      fototipo = st.selectbox("Fototipo Cutáneo (Fitzpatrick)", ["Tipo I", "Tipo II", "Tipo III", "Tipo IV", "Tipo V", "Tipo VI"])
      ciclo = st.selectbox("Ciclo Menstrual", ["Regular", "Irregular", "Amenorrea", "Menopausia", "No aplica"])

    st.markdown("---")
    st.subheader("🎯 Lesiones y Antecedentes Clínicos")
    lesiones = st.text_area("¿Qué lesiones o afecciones desea tratar? (Acné, melasma, flacidez, etc.)")

    col3, col4 = st.columns(2)
    with col3:
      enfermedad = st.text_area("¿Padece alguna enfermedad actual?")
      alergias = st.text_area("Alergias conocidas")
    with col4:
      tratamientos = st.text_area("Tratamientos recientes")
      marcapasos = st.radio("¿Posee marcapasos?", ["No", "Sí"])
      placa = st.radio("¿Posee placa u otros implantes metálicos?", ["No", "Sí"])

    obs = st.text_area("Observaciones Generales de la Cosmiatra")
    
    if st.form_submit_button("Guardar Historia Clínica"):
      if nombre:
        tipos_str = ", ".join([t for t, cond in [("Eudérmica", p_eud), ("Seca", p_sec), ("Grasa", p_gra), ("Mixta", p_mix), ("Alipica", p_ali), ("Deshidratada", p_des), ("Sensible", p_sen)] if cond])
        ws_clientes.append_row([
            str(datetime.now().strftime("%Y-%m-%d %H:%M")),
            nombre, cedula, telefono, email, ocupacion,
            tipos_str, fototipo, ciclo, lesiones,
            enfermedad, alergias, tratamientos, marcapasos, placa, obs
        ])
        st.success(f"¡Historia clínica de {nombre} guardada con éxito!")
      else:
        st.warning("Por favor ingresa al menos el nombre y apellido.")

# ============================================
# 6. FINANZAS (CONTROL DE INGRESOS Y EGRESOS)
# ============================================
elif menu == "💰 Finanzas":
  st.title("Control de Finanzas (Ingresos y Egresos)")
  st.markdown("Monitorea detalladamente a dónde va cada dólar y controla el flujo de caja.")

  tab1, tab2 = st.tabs(["Registrar Movimiento", "Historial y Balance"])

  with tab1:
    with st.form("form_fin", clear_on_submit=True):
      col1, col2 = st.columns(2)
      with col1:
        tipo_mov = st.selectbox("Tipo de Movimiento", ["Ingreso", "Gasto"])
        concepto = st.text_input("Concepto (Ej: Cobro Tratamiento Hydra Glow, Compra Gasas)")
        monto = st.number_input("Monto ($)", min_value=0.0, step=0.50, value=20.0)
      with col2:
        metodo = st.selectbox("Método de Pago", ["Efectivo", "Binance USDT", "Zinli", "Pago Móvil / Transferencia", "Otro"])
        cat = st.selectbox("Categoría", ["Servicio Estético", "Venta Producto", "Compra Insumos", "Operativo / Alquiler", "Otro"])

      obs_f = st.text_area("Notas adicionales")
      if st.form_submit_button("Guardar Movimiento"):
        if concepto and monto > 0:
          ws_finanzas.append_row([
              str(datetime.now().strftime("%Y-%m-%d %H:%M")),
              tipo_mov, concepto, float(monto), metodo, cat, obs_f
          ])
          st.success(f"¡Movimiento de tipo '{tipo_mov}' registrado por ${monto:.2f}!")
        else:
          st.warning("Completa el concepto y un monto válido.")

  with tab2:
    st.subheader("📊 Historial de Ingresos y Egresos")
    try:
      data_f = ws_finanzas.get_all_records()
      if data_f:
        df_f = pd.DataFrame(data_f)
        ing = df_f[df_f["Tipo"] == "Ingreso"]["Monto"].astype(float).sum() if "Monto" in df_f.columns else 0
        gas = df_f[df_f["Tipo"] == "Gasto"]["Monto"].astype(float).sum() if "Monto" in df_f.columns else 0
        bal = ing - gas

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("💰 Total Ingresos", f"${ing:.2f}")
        col_m2.metric("📉 Total Egresos", f"${gas:.2f}")
        col_m3.metric("✨ Balance Neto", f"${bal:.2f}")
        st.divider()

        st.dataframe(df_f, use_container_width=True)
      else:
        st.info("Aún no hay movimientos financieros registrados.")
    except:
      st.info("Registra tu primer movimiento para ver el balance.")

# ============================================
# 7. INVENTARIO DE PRODUCTOS
# ============================================
elif menu == "📦 Inventario de Productos":
  st.title("Inventario de Productos y Activos")
  st.markdown("Control de stock en mililitros, gramos o unidades (descartables).")

  tab1, tab2 = st.tabs(["Registrar Producto", "Stock Actual"])

  with tab1:
    with st.form("form_inv", clear_on_submit=True):
      col1, col2 = st.columns(2)
      with col1:
        prod_nombre = st.text_input("Nombre del Producto / Activo / Equipo")
        tipo_med = st.selectbox("Tipo de Medida", ["Líquido / En Crema (ml)", "En Polvo / Sólido (g)", "Unidades (Descartables)"])
      with col2:
        costo_usd = st.number_input("Costo Total de Compra ($)", min_value=0.0, step=0.50, value=25.0)
        if "ml" in tipo_med or "g" in tipo_med:
          cant_total = st.number_input("Contenido Total (ml o g)", min_value=1.0, value=250.0)
        else:
          cant_total = st.number_input("Unidades en el Paquete", min_value=1, value=100)

      obs_i = st.text_area("Notas o marca del producto")
      if st.form_submit_button("Guardar en Inventario"):
        if prod_nombre:
          costo_unit = costo_usd / cant_total if cant_total > 0 else 0.0
          ws_inventario.append_row([
              str(datetime.now().strftime("%Y-%m-%d %H:%M")),
              prod_nombre, tipo_med, float(costo_usd), float(cant_total), round(costo_unit, 4), obs_i
          ])
          st.success(f"¡Guardado! Costo unitario/ml/g: ${costo_unit:.4f}")
        else:
          st.warning("Ingresa el nombre del producto.")

  with tab2:
    st.subheader("📋 Stock Actual en Cabina")
    try:
      data_i = ws_inventario.get_all_records()
      if data_i:
        st.dataframe(pd.DataFrame(data_i), use_container_width=True)
      else:
        st.info("El inventario está vacío actualmente.")
    except:
      st.info("Agrega tu primer producto para ver la tabla de stock.")
