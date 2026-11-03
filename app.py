from datetime import datetime
import xml.etree.ElementTree as ET
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import requests
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Nay López Skincare", page_icon="✨", layout="wide"
)


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


# ============================================
# TASA OFICIAL BCV EN TIEMPO REAL
# ============================================
@st.cache_data(ttl=3600)  # Guarda la tasa en caché por 1 hora para ser eficientes
def obtener_tasa_bcv():
  try:
    # API pública de referencia para la tasa del BCV en Venezuela
    url = "https://pydolarvenezuela-api.vercel.app/api/v1/dollar/bcv"
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
      data = response.json()
      # Extraemos el valor del dólar oficial
      tasa = data.get("monsters", {}).get("usd", {}).get("price", 0.0)
      if tasa > 0:
        return float(tasa)
  except Exception:
    pass

  # Tasa de respaldo por seguridad en caso de fallo de red
  return 36.50


tasa_bcv_hoy = obtener_tasa_bcv()


# Intentamos conectar y asegurar las pestañas necesarias
try:
  sh = conectar_google_sheets().spreadsheet

  try:
    ws_clientes = sh.worksheet("Clientes")
  except:
    ws_clientes = sh.add_worksheet(title="Clientes", rows="100", cols="20")

  try:
    ws_citas = sh.worksheet("Citas")
  except:
    ws_citas = sh.add_worksheet(title="Citas", rows="100", cols="20")

  try:
    ws_inventario = sh.worksheet("Inventario")
  except:
    ws_inventario = sh.add_worksheet(title="Inventario", rows="100", cols="20")

  try:
    ws_finanzas = sh.worksheet("Finanzas")
  except:
    ws_finanzas = sh.add_worksheet(title="Finanzas", rows="100", cols="20")

except Exception as e:
  st.error(
      f"Error al conectar con Google Sheets. Verifica tus credenciales o el"
      f" nombre de la hoja: {e}"
  )
  st.stop()

# ============================================
# INTERFAZ DE NAVEGACIÓN Y BARRA LATERAL
# ============================================
st.sidebar.title("✨ Nay López Skincare")
st.sidebar.markdown("Sistema en la Nube (Google Sheets)")

# Mostramos la tasa del BCV en la barra lateral de forma visible
st.sidebar.markdown("---")
st.sidebar.metric(
    label="📊 Tasa BCV del Día",
    value=f"Bs. {tasa_bcv_hoy:,.2f}",
    help="Tasa oficial del Banco Central de Venezuela actualizada.",
)
st.sidebar.markdown("---")
st.sidebar.markdown("Navegación")

menu = st.sidebar.selectbox(
    "Selecciona una opción",
    [
        "Inicio / Dashboard",
        "Clientes y Ficha Clínica",
        "Inventario / Productos",
        "Finanzas / Caja",
        "Citas y Agenda",
    ],
)

# ============================================
# MÓDULO 1: DASHBOARD
# ============================================
if menu == "Inicio / Dashboard":
  st.title("Panel de Control - Nay López Skincare")
  st.markdown("### ¡Bienvenida a tu cabina estética en la nube! 💜")

  try:
    clientes_data = ws_clientes.get_all_records()
    total_clientes = len(clientes_data) if clientes_data else 0
  except:
    total_clientes = 0

  try:
    inventario_data = ws_inventario.get_all_records()
    total_productos = len(inventario_data) if inventario_data else 0
  except:
    total_productos = 0

  try:
    finanzas_data = ws_finanzas.get_all_records()
    if finanzas_data:
      df_fin = pd.DataFrame(finanzas_data)
      ingresos_totales_usd = (
          df_fin[df_fin["Tipo"] == "Ingreso"]["MontoUSD"].astype(float).sum()
      )
    else:
      ingresos_totales_usd = 0.0
  except:
    ingresos_totales_usd = 0.0

  ingresos_totales_bs = ingresos_totales_usd * tasa_bcv_hoy

  # Citas para hoy
  fecha_hoy = datetime.now().strftime("%Y-%m-%d")
  citas_hoy_count = 0
  citas_hoy_lista = []
  try:
    citas_data = ws_citas.get_all_records()
    if citas_data:
      for cita in citas_data:
        if str(cita.get("FechaCita", "")).startswith(fecha_hoy):
          citas_hoy_count += 1
          citas_hoy_lista.append(cita)
  except:
    pass

  col1, col2, col3, col4 = st.columns(4)
  with col1:
    st.metric(label="📅 Citas para Hoy", value=f"{citas_hoy_count} citas")
  with col2:
    st.metric(label="👥 Total Pacientes", value=total_clientes)
  with col3:
    st.metric(label="📦 Productos", value=total_productos)
  with col4:
    st.metric(
        label="💰 Ingresos (USD / Bs)",
        value=f"${ingresos_totales_usd:.2f}",
        delta=f"Bs. {ingresos_totales_bs:,.2f}",
    )

  st.divider()
  st.subheader(f"✨ Agenda del Día ({fecha_hoy})")
  if citas_hoy_count > 0:
    st.dataframe(pd.DataFrame(citas_hoy_lista), use_container_width=True)
  else:
    st.info("No tienes citas agendadas para el día de hoy.")

# ============================================
# MÓDULO 2: CLIENTES Y FICHA CLÍNICA
# ============================================
elif menu == "Clientes y Ficha Clínica":
  st.title("Gestión de Pacientes y Ficha Estética")

  tab1, tab2 = st.tabs(["Registrar Nueva Paciente", "Consultar Fichas"])

  with tab1:
    st.subheader("📝 Ficha Clínica y Datos de la Paciente")
    with st.form("form_cliente", clear_on_submit=True):
      col1, col2 = st.columns(2)
      with col1:
        nombre = st.text_input("Nombre y Apellido")
        cedula = st.text_input("Cédula de Identidad")
        telefono = st.text_input("Número de Contacto / WhatsApp")
        email = st.text_input("Correo Electrónico")
        ocupacion = st.text_input("Ocupación")

      with col2:
        st.markdown("**Selecciona los Tipos de Piel:**")
        tp_eudermica = st.checkbox("Eudérmica (Normal)")
        tp_seca = st.checkbox("Seca")
        tp_grasa = st.checkbox("Grasa")
        tp_mixta = st.checkbox("Mixta")
        tp_alipica = st.checkbox("Alipica")
        tp_deshidratada = st.checkbox("Deshidratada")
        tp_sensible = st.checkbox("Sensible")

        fototipo = st.selectbox(
            "Fototipo Cutáneo",
            ["Tipo I", "Tipo II", "Tipo III", "Tipo IV", "Tipo V", "Tipo VI"],
        )
        ciclo_menstrual = st.selectbox(
            "Ciclo Menstrual",
            ["Regular", "Irregular", "Amenorrea", "Menopausia", "No aplica"],
        )

      st.markdown("---")
      col3, col4 = st.columns(2)
      with col3:
        enfermedad = st.text_area("¿Padece alguna enfermedad actual?")
        antecedentes = st.text_area("Antecedentes Médicos")
        alergias = st.text_area("Alergias conocidas")
      with col4:
        tratamientos_recientes = st.text_area("Tratamientos recientes")
        marcapasos = st.radio("¿Posee marcapasos?", ["No", "Sí"])
        placa_metalica = st.radio("¿Posee placa u otros implantes metálicos?", ["No", "Sí"])

      observaciones = st.text_area("Observaciones Generales")
      submit_cli = st.form_submit_button("Guardar Ficha Clínica")

      if submit_cli:
        if nombre:
          tipos = []
          if tp_eudermica:
            tipos.append("Eudérmica")
          if tp_seca:
            tipos.append("Seca")
          if tp_grasa:
            tipos.append("Grasa")
          if tp_mixta:
            tipos.append("Mixta")
          if tp_alipica:
            tipos.append("Alipica")
          if tp_deshidratada:
            tipos.append("Deshidratada")
          if tp_sensible:
            tipos.append("Sensible")

          ws_clientes.append_row([
              str(datetime.now().strftime("%Y-%m-%d %H:%M")),
              nombre,
              cedula,
              telefono,
              email,
              ocupacion,
              ", ".join(tipos) if tipos else "No especificado",
              fototipo,
              ciclo_menstrual,
              enfermedad,
              antecedentes,
              alergias,
              tratamientos_recientes,
              marcapasos,
              placa_metalica,
              observaciones,
          ])
          st.success(f"¡Ficha de {nombre} guardada con éxito!")
        else:
          st.warning("Ingresa al menos el nombre de la paciente.")

  with tab2:
    st.subheader("📂 Base de Datos de Pacientes")
    try:
      data_cli = ws_clientes.get_all_records()
      if data_cli and len(data_cli) > 0:
        st.dataframe(pd.DataFrame(data_cli), use_container_width=True)
      else:
        st.info("Aún no hay pacientes registradas.")
    except:
      st.info("Agrega tu primera paciente para ver la tabla.")

# ============================================
# MÓDULO 3: INVENTARIO Y COSTOS
# ============================================
elif menu == "Inventario / Productos":
  st.title("Control de Inventario y Costos de Cabina")
  st.markdown("Control en Dólares con equivalente automático al BCV.")

  tab1, tab2 = st.tabs(["Registrar Producto", "Stock y Costos"])

  with tab1:
    with st.form("form_inv", clear_on_submit=True):
      col1, col2 = st.columns(2)
      with col1:
        prod_nombre = st.text_input("Nombre del Producto / Activo")
        tipo_medida = st.selectbox(
            "Tipo de Medida",
            [
                "Líquido / En Crema (ml)",
                "En Polvo / Sólido (g)",
                "Unidades (Descartables)",
            ],
        )
      with col2:
        precio_compra_usd = st.number_input(
            "Costo Total de Compra ($)", min_value=0.0, step=0.50, value=25.0
        )
        if "ml" in tipo_medida or "g" in tipo_medida:
          cantidad_total = st.number_input(
              "Contenido Total (ml o g)", min_value=1.0, value=250.0
          )
        else:
          cantidad_total = st.number_input(
              "Unidades en el Paquete", min_value=1, value=100
          )

      obs_inv = st.text_area("Notas o Marca")
      submit_inv = st.form_submit_button("Guardar Producto")

      if submit_inv:
        if prod_nombre:
          costo_unit_usd = (
              precio_compra_usd / cantidad_total if cantidad_total > 0 else 0.0
          )
          costo_unit_bs = costo_unit_usd * tasa_bcv_hoy

          ws_inventario.append_row([
              str(datetime.now().strftime("%Y-%m-%d %H:%M")),
              prod_nombre,
              tipo_medida,
              float(precio_compra_usd),
              float(precio_compra_usd * tasa_bcv_hoy),
              float(cantidad_total),
              round(costo_unit_usd, 4),
              round(costo_unit_bs, 4),
              obs_inv,
          ])
          st.success(
              f"¡Registrado! Costo: ${costo_unit_usd:.4f} (Bs."
              f" {tasa_bcv_hoy * costo_unit_usd:.2f}) por unidad/ml."
          )
        else:
          st.warning("Ingresa el nombre del producto.")

  with tab2:
    st.subheader("📋 Stock y Costos Actuales")
    try:
      data_inv = ws_inventario.get_all_records()
      if data_inv and len(data_inv) > 0:
        st.dataframe(pd.DataFrame(data_inv), use_container_width=True)
      else:
        st.info("Inventario vacío.")
    except:
      st.info("Agrega un producto para ver la tabla.")

# ============================================
# MÓDULO 4: FINANZAS Y CAJA (DOBLE MONEDA)
# ============================================
elif menu == "Finanzas / Caja":
  st.title("Control Financiero y Caja (Dólares y Bolívares BCV)")
  st.markdown(
      f"💱 **Tasa BCV del día:** Bs. {tasa_bcv_hoy:,.2f} por dólar (se aplica a"
      " tus registros)."
  )

  tab1, tab2 = st.tabs(["Registrar Movimiento", "Historial y Balance"])

  with tab1:
    with st.form("form_fin", clear_on_submit=True):
      col1, col2 = st.columns(2)
      with col1:
        tipo_mov = st.selectbox("Tipo de Movimiento", ["Ingreso", "Gasto"])
        concepto = st.text_input(
            "Concepto (Ej: Tratamiento Hydra Glow, Compra Gasas)"
        )
        monto_usd = st.number_input(
            "Monto en Dólares ($)", min_value=0.0, step=0.50, value=15.0
        )
      with col2:
        metodo_pago = st.selectbox(
            "Método de Pago",
            [
                "Efectivo Divisa ($)",
                "Efectivo Bolívares (Bs)",
                "Binance USDT",
                "Zinli",
                "BNC / Pago Móvil",
                "Otro",
            ],
        )
        categoria_fin = st.selectbox(
            "Categoría",
            [
                "Servicio Estético",
                "Venta de Producto",
                "Compra Insumos",
                "Operativo / Alquiler",
                "Otro",
            ],
        )

      # Conversión automática en pantalla para que la veas antes de guardar
      monto_bs_calculado = monto_usd * tasa_bcv_hoy
      st.info(
          f"💡 Equivalente exacto a la tasa del BCV: **Bs."
          f" {monto_bs_calculado:,.2f}**"
      )

      notas_fin = st.text_area("Notas adicionales")
      submit_fin = st.form_submit_button("Guardar Movimiento")

      if submit_fin:
        if concepto and monto_usd > 0:
          ws_finanzas.append_row([
              str(datetime.now().strftime("%Y-%m-%d %H:%M")),
              tipo_mov,
              concepto,
              float(monto_usd),
              float(monto_bs_calculado),
              float(tasa_bcv_hoy),
              metodo_pago,
              categoria_fin,
              notas_fin,
          ])
          st.success(
              f"¡Registrado! ${monto_usd:.2f} (Bs. {monto_bs_calculado:,.2f})"
              " guardado correctamente."
          )
        else:
          st.warning("Completa el concepto y un monto válido en dólares.")

  with tab2:
    st.subheader("📊 Historial Financiero y Balance")
    try:
      data_fin = ws_finanzas.get_all_records()
      if data_fin and len(data_fin) > 0:
        df_fin = pd.DataFrame(data_fin)

        if "Tipo" in df_fin.columns and "MontoUSD" in df_fin.columns:
          ing_usd = (
              df_fin[df_fin["Tipo"] == "Ingreso"]["MontoUSD"]
              .astype(float)
              .sum()
          )
          gas_usd = (
              df_fin[df_fin["Tipo"] == "Gasto"]["MontoUSD"]
              .astype(float)
              .sum()
          )
          bal_usd = ing_usd - gas_usd

          col_m1, col_m2, col_m3 = st.columns(3)
          col_m1.metric(
              "💰 Ingresos Totales",
              f"${ing_usd:.2f}",
              f"Bs. {ing_usd * tasa_bcv_hoy:,.2f}",
          )
          col_m2.metric(
              "📉 Gastos Totales",
              f"${gas_usd:.2f}",
              f"Bs. {gas_usd * tasa_bcv_hoy:,.2f}",
          )
          col_m3.metric(
              "✨ Balance Neto",
              f"${bal_usd:.2f}",
              f"Bs. {bal_usd * tasa_bcv_hoy:,.2f}",
          )
          st.divider()

        st.dataframe(df_fin, use_container_width=True)
      else:
        st.info("Aún no hay movimientos financieros registrados.")
    except:
      st.info("Registra tu primer movimiento financiero para ver la tabla.")

# ============================================
# MÓDULO 5: CITAS Y AGENDA
# ============================================
elif menu == "Citas y Agenda":
  st.title("Agenda de Citas - Cabina Estética")
  st.markdown("Programa tus atenciones en tu estudio o en GIA SHOP.")

  tab1, tab2 = st.tabs(["Agendar Nueva Cita", "Ver Todas las Citas"])

  with tab1:
    with st.form("form_cita", clear_on_submit=True):
      col1, col2 = st.columns(2)
      with col1:
        nombre_cita = st.text_input("Nombre de la Paciente")
        fecha_cita = st.date_input("Fecha de la Cita")
        hora_cita = st.time_input("Hora de la Cita")
      with col2:
        tratamiento_cita = st.selectbox(
            "Tratamiento",
            [
                "Hydra Glow Detox",
                "Peeling Químico / Enzimático",
                "Dermapen",
                "Radiofrecuencia",
                "Masaje Reductor / Corporal",
                "Otro",
            ],
        )
        estado_cita = st.selectbox(
            "Estado", ["Agendada", "Confirmada", "Atendida", "Cancelada"]
        )

      obs_cita = st.text_area("Notas de la cita")
      submit_cita = st.form_submit_button("Agendar Cita")

      if submit_cita:
        if nombre_cita:
          ws_citas.append_row([
              str(fecha_cita),
              str(hora_cita),
              nombre_cita,
              tratamiento_cita,
              estado_cita,
              obs_cita,
          ])
          st.success(f"¡Cita agendada para {nombre_cita} el {fecha_cita}!")
        else:
          st.warning("Ingresa el nombre de la paciente.")

  with tab2:
    st.subheader("📅 Listado de Citas")
    try:
      data_citas = ws_citas.get_all_records()
      if data_citas and len(data_citas) > 0:
        st.dataframe(pd.DataFrame(data_citas), use_container_width=True)
      else:
        st.info("No hay citas registradas en la agenda.")
    except:
      st.info("Agrega tu primera cita para visualizar la agenda.")
