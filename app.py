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
  
  # Verificamos o creamos las hojas con sus cabeceras exactas para evitar fallos
  def asegurar_hoja(nombre_hoja, cabeceras):
    try:
      ws = sh.worksheet(nombre_hoja)
    except:
      ws = sh.add_worksheet(title=nombre_hoja, rows="100", cols="20")
      ws.append_row(cabeceras)
    return ws

  ws_clientes = asegurar_hoja("Clientes", ["Fecha", "Nombre", "Cedula", "Telefono", "Email", "Ocupacion", "TipoPiel", "Fototipo", "Ciclo", "Lesiones", "Enfermedades", "Alergias", "Tratamientos", "Marcapasos", "Placa", "Observaciones"])
  ws_inventario = asegurar_hoja("Inventario", ["Fecha", "Nombre", "Tipo", "CostoUSD", "Cantidad", "CostoUnit", "Notas"])
  ws_finanzas = asegurar_hoja("Finanzas", ["Fecha", "Tipo", "Concepto", "Monto", "SueldoCosmiatra", "FondoReposicion", "Metodo", "Categoria", "Notas"])
  ws_citas = asegurar_hoja("Citas", ["Fecha", "Hora", "NombreClienta", "Cedula", "Telefono", "Tratamiento", "Estado", "Observaciones"])
  ws_servicios = asegurar_hoja("Servicios", ["Fecha", "NombreServicio", "Sesiones", "PrecioUSD", "SueldoFijoUSD", "Aparatologia", "Activos", "Descripcion"])

except Exception as e:
  st.error(f"Error al conectar con Google Sheets: {e}")
  st.stop()

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
        "🧴 Servicios y Tarifas",
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
    clientes_records = ws_clientes.get_all_records()
    total_pacientes = len(clientes_records) if clientes_records else 0
  except:
    total_pacientes = 0

  try:
    inventario_records = ws_inventario.get_all_records()
    total_inventario = len(inventario_records) if inventario_records else 0
  except:
    total_inventario = 0

  try:
    finanzas_data = ws_finanzas.get_all_records()
    ingresos = sum([float(str(x.get("Monto", 0)).strip() or 0) for x in finanzas_data if str(x.get("Tipo", "")).strip() == "Ingreso"]) if finanzas_data else 0.0
    egresos = sum([float(str(x.get("Monto", 0)).strip() or 0) for x in finanzas_data if str(x.get("Tipo", "")).strip() == "Gasto"]) if finanzas_data else 0.0
    fondo_repo = sum([float(str(x.get("FondoReposicion", 0)).strip() or 0) for x in finanzas_data if str(x.get("Tipo", "")).strip() == "Ingreso"]) if finanzas_data else 0.0
    sueldo_neto = sum([float(str(x.get("SueldoCosmiatra", 0)).strip() or 0) for x in finanzas_data if str(x.get("Tipo", "")).strip() == "Ingreso"]) if finanzas_data else 0.0
  except:
    ingresos, egresos, fondo_repo, sueldo_neto = 0.0, 0.0, 0.0, 0.0

  col1, col2, col3, col4 = st.columns(4)
  col1.metric("💰 Ingresos Totales", f"${ingresos:.2f}")
  col2.metric("👩‍⚕️ Tu Sueldo Acumulado", f"${sueldo_neto:.2f}")
  col3.metric("📦 Fondo Reposición", f"${fondo_repo:.2f}")
  col4.metric("📉 Egresos / Gastos", f"${egresos:.2f}")

  st.divider()
  st.info("💡 **Dashboard Sincronizado:** Los totales se calculan directamente en tiempo real desde la caja.")

# ============================================
# 2. AGENDA
# ============================================
elif menu == "📅 Agenda":
  st.title("Agenda de Citas y Turnos")
  st.markdown("Al agendar un turno, la clienta se registra automáticamente en tu base de datos.")

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
      if st.form_submit_button("Agendar Turno y Registrar Cliente"):
        if nom_c and ced_c:
          # Guardamos en Citas
          ws_citas.append_row([str(fec_c), str(hor_c), nom_c, str(ced_c).strip(), tel_c, trat_c, "Agendada", obs_c])
          
          # Verificamos en Clientes por cédula exacta
          try:
            cli_data = ws_clientes.get_all_records()
            cedulas_existentes = [str(x.get("Cedula", "")).strip() for x in cli_data]
          except:
            cedulas_existentes = []

          if str(ced_c).strip() not in cedulas_existentes:
            ws_clientes.append_row([
                str(datetime.now().strftime("%Y-%m-%d %H:%M")),
                nom_c, str(ced_c).strip(), tel_c, "", "", "", "", "", "", "", "", "", "", "", ""
            ])

          st.success(f"¡Turno agendado y clienta {nom_c} registrada con éxito!")
        else:
          st.warning("Por favor ingresa al menos el nombre y la cédula.")

  with tab2:
    st.subheader("📅 Turnos Registrados")
    try:
      data_c = ws_citas.get_all_records()
      if data_c:
        st.dataframe(pd.DataFrame(data_c), use_container_width=True)
      else:
        st.info("No hay turnos registrados en la agenda.")
    except:
      st.info("Agrega tu primer turno.")

# ============================================
# 3. SERVICIOS Y TARIFAS
# ============================================
elif menu == "🧴 Servicios y Tarifas":
  st.title("Catálogo de Servicios y Protocolos")
  st.markdown("Define tus precios y el sueldo específico que ganas por cada protocolo.")

  tab_s1, tab_s2 = st.tabs(["Registrar / Migrar Protocolo", "Listado de Servicios Activos"])

  with tab_s1:
    with st.form("form_servicios_manual", clear_on_submit=True):
      col_s1, col_s2 = st.columns(2)
      with col_s1:
        s_nombre = st.text_input("Nombre del Tratamiento (Ej: Hydra Glow Detox)")
        s_sesiones = st.text_input("Cantidad de Sesiones (Ej: 1 sesión o Paquete)")
        s_precio = st.number_input("Precio de Venta al Público ($)", min_value=0.0, step=0.50, value=35.0)
        s_sueldo = st.number_input("Tu Sueldo Fijo por este Servicio ($)", min_value=0.0, step=0.50, value=5.0)
      with col_s2:
        s_aparatos = st.text_input("Aparatología Usada")
        s_activos = st.text_input("Principios Activos")
      
      s_desc = st.text_area("Descripción detallada del protocolo")

      if st.form_submit_button("Guardar Protocolo y Tarifas"):
        if s_nombre:
          ws_servicios.append_row([
              str(datetime.now().strftime("%Y-%m-%d %H:%M")),
              s_nombre, s_sesiones, float(s_precio), float(s_sueldo), s_aparatos, s_activos, s_desc
          ])
          st.success(f"¡Protocolo '{s_nombre}' guardado con su sueldo asignado de ${s_sueldo:.2f}!")
        else:
          st.warning("Ingresa el nombre del servicio.")

  with tab_s2:
    st.subheader("📋 Tus Protocolos y Tarifas Registradas")
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
  st.markdown("Listado oficial de clientas registradas en el sistema.")

  try:
    data_cli = ws_clientes.get_all_records()
    if data_cli:
      df_cli = pd.DataFrame(data_cli)
      st.dataframe(df_cli, use_container_width=True)
    else:
      st.info("Aún no hay clientas registradas.")
  except:
    st.info("Las clientas aparecerán aquí automáticamente.")

# ============================================
# 5. HISTORIA CLÍNICA (BÚSQUEDA PERFECTA POR CÉDULA)
# ============================================
elif menu == "👩‍⚕️ Historia Clínica":
  st.title("Historia Clínica y Evaluación")
  st.markdown("Escribe la cédula de la clienta para autocompletar sus datos al instante.")

  # Cargamos registros de Citas y Clientes de forma segura
  citas_db = []
  clientes_db = []
  try:
    citas_db = ws_citas.get_all_records()
    clientes_db = ws_clientes.get_all_records()
  except:
    pass

  # Campo directo para introducir la cédula y buscar
  cedula_ingresada = st.text_input("🔍 Ingresa o escribe la Cédula de Identidad de la Clienta:")

  nombre_prefill = ""
  telefono_prefill = ""

  if cedula_ingresada:
    ced_busq = cedula_ingresada.strip()
    # Buscamos en Citas
    for c in citas_db:
      if str(c.get("Cedula", "")).strip() == ced_busq:
        nombre_prefill = c.get("NombreClienta", "")
        telefono_prefill = c.get("Telefono", "")
        break
    # Si no está en citas, buscamos en Clientes
    if not nombre_prefill:
      for cli in clientes_db:
        if str(cli.get("Cedula", "")).strip() == ced_busq:
          nombre_prefill = cli.get("Nombre", "")
          telefono_prefill = cli.get("Telefono", "")
          break

    if nombre_prefill:
      st.success(f"✨ ¡Datos encontrados para la cédula {ced_busq}: **{nombre_prefill}**!")
    else:
      st.warning("No hay registros previos con esta cédula, puedes completar su nombre manualmente.")

  st.markdown("---")
  with st.form("form_hc_autocompletada", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
      nombre = st.text_input("Nombre y Apellido", value=nombre_prefill)
      cedula = st.text_input("Cédula de Identidad", value=cedula_ingresada if cedula_ingresada else "")
      telefono = st.text_input("Número de Contacto / WhatsApp", value=telefono_prefill)
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
    
    if st.form_submit_button("Guardar Ficha y Actualizar Cliente"):
      if nombre and cedula:
        tipos_str = ", ".join([t for t, cond in [("Eudérmica", p_eud), ("Seca", p_sec), ("Grasa", p_gra), ("Mixta", p_mix), ("Alipica", p_ali), ("Deshidratada", p_des), ("Sensible", p_sen)] if cond])
        
        ws_clientes.append_row([
            str(datetime.now().strftime("%Y-%m-%d %H:%M")),
            nombre, str(cedula).strip(), telefono, email, ocupacion,
            tipos_str, fototipo, ciclo, lesiones,
            enfermedad, alergias, tratamientos, marcapasos, placa, obs
        ])
        st.success(f"¡Historia clínica de {nombre} guardada y actualizada con éxito!")
      else:
        st.warning("Por favor asegúrate de que el nombre y la cédula estén llenos.")

# ============================================
# 6. FINANZAS (CONEXIÓN EXACTA CON DASHBOARD)
# ============================================
elif menu == "💰 Finanzas":
  st.title("Control Financiero y Distribución de Ganancias")
  st.markdown("Calcula automáticamente tu sueldo fijo por servicio y el fondo para reposición.")

  tab1, tab2 = st.tabs(["Registrar Ingreso / Gasto", "Reporte de Ganancias y Reposición"])

  with tab1:
    with st.form("form_fin_protocolo", clear_on_submit=True):
      col1, col2 = st.columns(2)
      with col1:
        tipo_mov = st.selectbox("Tipo de Movimiento", ["Ingreso", "Gasto"])
        concepto = st.text_input("Concepto (Ej: Cobro Tratamiento Hydra Glow)")
        monto_total = st.number_input("Monto Total Cobrado ($)", min_value=0.0, step=0.50, value=35.0)
      with col2:
        metodo = st.selectbox("Método de Pago", ["Efectivo", "Binance USDT", "Zinli", "Pago Móvil / Transferencia", "Otro"])
        cat = st.selectbox("Categoría", ["Servicio Estético", "Venta Producto", "Compra Insumos", "Operativo / Alquiler", "Otro"])

      st.markdown("---")
      st.markdown("### 🧮 Desglose Automático (Sueldo Fijo + Fondo de Reposición)")
      
      sueldo_sugerido = 5.0
      serv_db = []
      try:
        serv_db = ws_servicios.get_all_records()
        nombres_serv = [s.get("NombreServicio", "") for s in serv_db]
      except:
        nombres_serv = []

      if nombres_serv and tipo_mov == "Ingreso":
        serv_elegido = st.selectbox("Selecciona el servicio realizado para aplicar su sueldo fijo:", nombres_serv)
        for s in serv_db:
          if s.get("NombreServicio", "") == serv_elegido:
            sueldo_sugerido = float(s.get("SueldoFijoUSD", 5.0))
            break
      else:
        sueldo_sugerido = st.number_input("Tu sueldo fijo para este servicio ($):", min_value=0.0, value=5.0)

      sueldo_cosmiatra = sueldo_sugerido if tipo_mov == "Ingreso" else 0.0
      fondo_reposicion = (monto_total - sueldo_cosmiatra) if (tipo_mov == "Ingreso" and monto_total > sueldo_cosmiatra) else 0.0

      if tipo_mov == "Ingreso":
        st.info(f"💡 Del cobro total de **${monto_total:.2f}**: **${sueldo_cosmiatra:.2f}** van para tu sueldo y **${fondo_reposicion:.2f}** van destinados al fondo de reposición.")

      obs_f = st.text_area("Notas adicionales")
      if st.form_submit_button("Guardar Movimiento en Caja"):
        if concepto and monto_total > 0:
          ws_finanzas.append_row([
              str(datetime.now().strftime("%Y-%m-%d %H:%M")),
              tipo_mov, 
              concepto, 
              float(monto_total), 
              float(sueldo_cosmiatra), 
              float(fondo_reposicion),
              metodo, 
              cat, 
              obs_f
          ])
          st.success(f"¡Movimiento registrado con éxito y sincronizado con el Dashboard!")
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
        sueldo_tot =
