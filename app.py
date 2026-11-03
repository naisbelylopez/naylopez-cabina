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
# ESTILO VISUAL: BLANCO, LILA Y TONOS CÁLIDOS
# ============================================
st.markdown("""
    <style>
    .stApp {
        background-color: #fcfbfd;
        color: #2d2b38;
    }
    div.stMetric, div.stTabs, div.stForm {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #e9d8fd;
        box-shadow: 0 4px 15px rgba(147, 51, 234, 0.04);
    }
    .stButton>button {
        background: linear-gradient(135deg, #a855f7 0%, #c084fc 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.2rem;
        box-shadow: 0 4px 12px rgba(168, 85, 247, 0.25);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #9333ea 0%, #a855f7 100%);
        color: white;
    }
    section[data-testid="stSidebar"] {
        background-color: #f7f2fb;
        border-right: 1px solid #e9d8fd;
    }
    h1, h2, h3 {
        color: #581c87;
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
  try:
    ws_servicios = sh.worksheet("Servicios")
  except:
    ws_servicios = sh.add_worksheet(title="Servicios", rows="100", cols="20")
    ws_servicios.append_row(["Fecha", "NombreServicio", "Sesiones", "PrecioUSD", "Aparatologia", "Activos", "Descripcion"])
except Exception:
  sh = conectar_google_sheets().spreadsheet
  ws_clientes = sh.add_worksheet(title="Clientes", rows="100", cols="20")
  ws_inventario = sh.add_worksheet(title="Inventario", rows="100", cols="20")
  ws_finanzas = sh.add_worksheet(title="Finanzas", rows="100", cols="20")
  ws_citas = sh.add_worksheet(title="Citas", rows="100", cols="20")
  ws_servicios = sh.add_worksheet(title="Servicios", rows="100", cols="20")
  ws_servicios.append_row(["Fecha", "NombreServicio", "Sesiones", "PrecioUSD", "Aparatologia", "Activos", "Descripcion"])

# ============================================
# MENÚ LATERAL
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
  st.markdown("### ✨ Control general de turnos, ingresos y rentabilidad.")

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
    fondo_repo = sum([float(x.get("FondoReposicion", 0)) for x in finanzas_data if x.get("Tipo") == "Ingreso"]) if finanzas_data else 0.0
    sueldo_neto = sum([float(x.get("SueldoCosmiatra", 0)) for x in finanzas_data if x.get("Tipo") == "Ingreso"]) if finanzas_data else 0.0
  except:
    ingresos, egresos, fondo_repo, sueldo_neto = 0.0, 0.0, 0.0, 0.0

  col1, col2, col3, col4 = st.columns(4)
  col1.metric("💰 Ingresos Totales", f"${ingresos:.2f}")
  col2.metric("👩‍⚕️ Tu Sueldo Generado", f"${sueldo_neto:.2f}")
  col3.metric("📦 Fondo Reposición", f"${fondo_repo:.2f}")
  col4.metric("📉 Egresos / Gastos", f"${egresos:.2f}")

  st.divider()
  st.info("💡 **Consejo:** Al registrar los pagos en **Finanzas**, el sistema distribuye automáticamente cuánto va para tu sueldo y cuánto para reposición de materiales.")

# ============================================
# 2. AGENDA
# ============================================
elif menu == "📅 Agenda":
  st.title("Agenda de Citas y Turnos")
  st.markdown("Registra las citas iniciales con los datos básicos de tus clientas.")

  tab1, tab2 = st.tabs(["Agendar Turno", "Ver Calendario"])

  with tab1:
    with st.form("form_citas", clear_on_submit=True):
      col1, col2 = st.columns(2)
      with col1:
        nom_c = st.text_input("Nombre y Apellido de la Clienta")
        ced_c = st.text_input("Cédula de Identidad")
        tel_c = st.text_input("Número de Contacto / WhatsApp")
      with col2:
        fec_c = st.date_input("Fecha del Turno")
        hor_c = st.time_input("Hora del Turno")
        trat_c = st.selectbox("Servicio / Tratamiento", ["Hydra Glow Detox", "Peeling Químico / Enzimático", "Dermapen", "Tratamiento Corporal"])
      
      obs_c = st.text_area("Observaciones del turno")
      if st.form_submit_button("Agendar Turno"):
        if nom_c and ced_c:
          ws_citas.append_row([str(fec_c), str(hor_c), nom_c, ced_c, tel_c, trat_c, "Agendada", obs_c])
          st.success(f"¡Turno agendado con éxito para {nom_c} (Cédula: {ced_c})!")
        else:
          st.warning("Por favor ingresa al menos el nombre y la cédula de la clienta.")

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
  st.title("Catálogo de Servicios y Precios (Tus Precios de Excel)")
  st.markdown("Administra los precios, sesiones y protocolos de tu cabina.")

  tab_s1, tab_s2 = st.tabs(["Registrar / Migrar Protocolo", "Listado de Servicios Activos"])

  with tab_s1:
    with st.form("form_servicios_manual", clear_on_submit=True):
      col_s1, col_s2 = st.columns(2)
      with col_s1:
        s_nombre = st.text_input("Nombre del Tratamiento (Ej: Hydra Glow Detox)")
        s_sesiones = st.text_input("Cantidad de Sesiones (Ej: 1 sesión o Paquete de 4)")
        s_precio = st.number_input("Precio Establecido ($)", min_value=0.0, step=0.50, value=35.0)
      with col_s2:
        s_aparatos = st.text_input("Aparatología Usada")
        s_activos = st.text_input("Principios Activos")
      
      s_desc = st.text_area("Descripción detallada del protocolo")

      if st.form_submit_button("Guardar Protocolo"):
        if s_nombre:
          ws_servicios.append_row([
              str(datetime.now().strftime("%Y-%m-%d %H:%M")),
              s_nombre, s_sesiones, float(s_precio), s_aparatos, s_activos, s_desc
          ])
          st.success(f"¡Protocolo '{s_nombre}' guardado con éxito!")
        else:
          st.warning("Ingresa el nombre del servicio.")

  with tab_s2:
    st.subheader("📋 Tus Protocolos y Precios Registrados")
    try:
      data_serv = ws_servicios.get_all_records()
      if data_serv:
        st.dataframe(pd.DataFrame(data_serv), use_container_width=True)
      else:
        st.info("Aún no hay servicios registrados.")
    except:
      st.info("Registra tu primer servicio.")

# ============================================
# 4. CLIENTES
# ============================================
elif menu == "👥 Clientes":
  st.title("Directorio de Clientes")
  st.markdown("Listado oficial de clientas atendidas y registradas en el sistema.")

  try:
    data_cli = ws_clientes.get_all_records()
    if data_cli:
      df_cli = pd.DataFrame(data_cli)
      st.dataframe(df_cli, use_container_width=True)
    else:
      st.info("Aún no hay clientas registradas en la base de datos de clientes.")
  except:
    st.info("Las clientas aparecerán aquí una vez que guardes su historia clínica.")

# ============================================
# 5. HISTORIA CLÍNICA (CON BÚSQUEDA AUTOMÁTICA DESDE AGENDA)
# ============================================
elif menu == "👩‍⚕️ Historia Clínica":
  st.title("Historia Clínica y Evaluación")
  st.markdown("Busca a la clienta agendada, sus datos se precargarán y al atenderla se guardará en tu directorio de clientes.")

  # Intentamos obtener la lista de clientas agendadas para facilitar la búsqueda
  nombres_agenda = []
  citas_db = []
  try:
    citas_db = ws_citas.get_all_records()
    nombres_agenda = [f"{c.get('NombreClienta', '')} (Cédula: {c.get('Cedula', '')})" for c in citas_db if c.get('NombreClienta')]
  except:
    pass

  clienta_seleccionada = None
  cedula_prefill = ""
  tel_prefill = ""

  if nombres_agenda:
    st.markdown("### 🔍 Buscar Clienta desde la Agenda")
    opcion_agenda = st.selectbox("Selecciona a la clienta que acudió a consulta:", ["-- Ingresar Manualmente --"] + nombres_agenda)
    
    if opcion_agenda != "-- Ingresar Manualmente --":
      # Extraemos los datos de la cita seleccionada
      for c in citas_db:
        if f"{c.get('NombreClienta', '')} (Cédula: {c.get('Cedula', '')})" == opcion_agenda:
          clienta_seleccionada = c.get('NombreClienta', '')
          cedula_prefill = c.get('Cedula', '')
          tel_prefill = c.get('Telefono', '')
          break

  st.markdown("---")
  with st.form("form_hc_inteligente", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
      # Si seleccionó de la agenda, precargamos los datos automáticamente
      nombre = st.text_input("Nombre y Apellido", value=clienta_seleccionada if clienta_seleccionada else "")
      cedula = st.text_input("Cédula de Identidad", value=cedula_prefill if cedula_prefill else "")
      telefono = st.text_input("Número de Contacto / WhatsApp", value=tel_prefill if tel_prefill else "")
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
    lesiones = st.text_area("¿Qué lesiones o afecciones desea tratar?")

    col3, col4 = st.columns(2)
    with col3:
      enfermedad = st.text_area("¿Padece alguna enfermedad actual?")
      alergias = st.text_area("Alergias conocidas")
    with col4:
      tratamientos = st.text_area("Tratamientos recientes")
      marcapasos = st.radio("¿Posee marcapasos?", ["No", "Sí"])
      placa = st.radio("¿Posee placa u otros implantes metálicos?", ["No", "Sí"])

    obs = st.text_area("Observaciones Generales de la Cosmiatra")
    
    if st.form_submit_button("Guardar Atención y Enviar a Clientes"):
      if nombre and cedula:
        tipos_str = ", ".join([t for t, cond in [("Eudérmica", p_eud), ("Seca", p_sec), ("Grasa", p_gra), ("Mixta", p_mix), ("Alipica", p_ali), ("Deshidratada", p_des), ("Sensible", p_sen)] if cond])
        
        # Guardamos directamente en la pestaña Clientes
        ws_clientes.append_row([
            str(datetime.now().strftime("%Y-%m-%d %H:%M")),
            nombre, cedula, telefono, email, ocupacion,
            tipos_str, fototipo, ciclo, lesiones,
            enfermedad, alergias, tratamientos, marcapasos, placa, obs
        ])
        st.success(f"¡Atención finalizada! La historia clínica de {nombre} se ha guardado exitosamente y ya figura en el módulo de Clientes.")
      else:
        st.warning("Por favor asegúrate de que el nombre y la cédula estén llenos.")

# ============================================
# 6. FINANZAS (CON CONTROL DE SUELDO Y REPOSICIÓN)
# ============================================
elif menu == "💰 Finanzas":
  st.title("Control Financiero: Ingresos, Sueldo y Reposición")
  st.markdown("Registra los cobros y visualiza exactamente a dónde va cada porcentaje de tu dinero.")

  tab1, tab2 = st.tabs(["Registrar Ingreso / Gasto", "Reporte de Ganancias y Reposición"])

  with tab1:
    with st.form("form_fin_avanzado", clear_on_submit=True):
      col1, col2 = st.columns(2)
      with col1:
        tipo_mov = st.selectbox("Tipo de Movimiento", ["Ingreso", "Gasto"])
        concepto = st.text_input("Concepto (Ej: Cobro Tratamiento Hydra Glow)")
        monto_total = st.number_input("Monto Total Cobrado ($)", min_value=0.0, step=0.50, value=35.0)
      with col2:
        metodo = st.selectbox("Método de Pago", ["Efectivo", "Binance USDT", "Zinli", "Pago Móvil / Transferencia", "Otro"])
        cat = st.selectbox("Categoría", ["Servicio Estético", "Venta Producto", "Compra Insumos", "Operativo / Alquiler", "Otro"])

      st.markdown("---")
      st.markdown("### 🧮 Distribución Inteligente del Ingreso (Opcional si es Serv. Estético)")
      col_d1, col_d2 = st.columns(2)
      with col_d1:
        porcentaje_sueldo = st.slider("Porcentaje para tu Sueldo (%)", 0, 100, 60)
      with col_d2:
        porcentaje_repo = st.slider("Porcentaje para Fondo de Reposición (%)", 0, 100, 40)

      # Calculamos montos automáticos
      sueldo_calculado = monto_total * (porcentaje_sueldo / 100) if tipo_mov == "Ingreso" else 0.0
      repo_calculado = monto_total * (porcentaje_repo / 100) if tipo_mov == "Ingreso" else 0.0

      if tipo_mov == "Ingreso":
        st.info(f"💡 De los ${monto_total:.2f}: **${sueldo_calculado:.2f}** van para tu sueldo y **${repo_calculado:.2f}** van para reposición de materiales.")

      obs_f = st.text_area("Notas adicionales")
      if st.form_submit_button("Guardar en Caja"):
        if concepto and monto_total > 0:
          ws_finanzas.append_row([
              str(datetime.now().strftime("%Y-%m-%d %H:%M")),
              tipo_mov, concepto, float(monto_total), 
              float(sueldo_calculado), float(repo_calculado),
              metodo, cat, obs_f
          ])
          st.success(f"¡Registrado con éxito en Finanzas!")
        else:
          st.warning("Completa el concepto y un monto válido.")

  with tab2:
    st.subheader("📊 Análisis de Ganancias, Sueldos y Reposición")
    try:
      data_f = ws_finanzas.get_all_records()
      if data_f:
        df_f = pd.DataFrame(data_f)
        ing_tot = df_f[df_f["Tipo"] == "Ingreso"]["Monto"].astype(float).sum() if "Monto" in df_f.columns else 0
        gas_tot = df_f[df_f["Tipo"] == "Gasto"]["Monto"].astype(float).sum() if "Monto" in df_f.columns else 0
        sueldo_tot = df_f["SueldoCosmiatra"].astype(float).sum() if "SueldoCosmiatra" in df_f.columns else 0
        repo_tot = df_f["FondoReposicion"].astype(float).sum() if "FondoReposicion" in df_f.columns else 0

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("💰 Ingresos Totales", f"${ing_tot:.2f}")
        col_m2.metric("👩‍⚕️ Sueldo Acumulado", f"${sueldo_tot:.2f}")
        col_m3.metric("📦 Fondo Reposición", f"${repo_tot:.2f}")
        col_m4.metric("📉 Gastos / Egresos", f"${gas_tot:.2f}")
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
