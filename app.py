from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
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


# Intentamos conectar y asegurar las pestañas necesarias
try:
  sh = conectar_google_sheets().spreadsheet

  # Verificamos y creamos automáticamente las pestañas si no existen
  try:
    ws_clientes = sh.worksheet("Clientes")
  except:
    ws_clientes = sh.add_worksheet(title="Clientes", rows="100", cols="20")

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
# INTERFAZ DE NAVEGACIÓN
# ============================================
st.sidebar.title("✨ Nay López Skincare")
st.sidebar.markdown("Sistema en la Nube (Google Sheets)")
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

if menu == "Inicio / Dashboard":
  st.title("Panel de Control - Nay López Skincare")
  st.info(
      "¡Bienvenida a tu sistema de gestión estética! Desde aquí puedes"
      " administrar tus pacientes, inventario y finanzas en tiempo real."
  )

elif menu == "Clientes y Ficha Clínica":
  st.title("Gestión de Pacientes y Ficha Estética")

  tab1, tab2 = st.tabs(["Registrar Nuevo Paciente", "Consultar Fichas"])

  with tab1:
    st.subheader("Registro de Paciente")
    nombre = st.text_input("Nombre y Apellido")
    telefono = st.text_input("Teléfono")
    email = st.text_input("Correo Electrónico")
    observaciones = st.text_area("Observaciones / Alergias / Tratamientos")

    if st.button("Guardar Paciente"):
      if nombre:
        ws_clientes.append_row(
            [nombre, telefono, email, observaciones, str(datetime.now())]
        )
        st.success(f"¡Paciente {nombre} registrada con éxito en Google Sheets!")
      else:
        st.warning("Por favor ingresa al menos el nombre del paciente.")

  with tab2:
    st.subheader("Lista de Pacientes Registradas")
    try:
      data = ws_clientes.get_all_records()
      if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
      else:
        st.info("Aún no hay pacientes registradas en la hoja.")
    except Exception as e:
      st.info("Registra tu primera paciente para visualizar la tabla.")

elif menu == "Inventario / Productos":
  st.title("Control de Inventario y Activos de Cabina")

  tab1, tab2 = st.tabs(["Registrar Producto / Insumo", "Ver Inventario"])

  with tab1:
    st.subheader("Agregar Insumo o Producto")
    prod_nombre = st.text_input("Nombre del Producto / Activo")
    prod_categoria = st.selectbox(
        "Categoría",
        [
            "Cosmética / Serum",
            "Insumo Descartable",
            "Aparatología / Equipo",
            "Otro",
        ],
    )
    prod_stock = st.number_input(
        "Cantidad Disponible", min_value=0, step=1, value=1
    )
    prod_costo = st.text_input("Costo Unitario / Notas")

    if st.button("Guardar en Inventario"):
      if prod_nombre:
        ws_inventario.append_row([
            prod_nombre,
            prod_categoria,
            int(prod_stock),
            prod_costo,
            str(datetime.now()),
        ])
        st.success(f"¡Producto '{prod_nombre}' registrado en el inventario!")
      else:
        st.warning("Por favor ingresa el nombre del producto.")

  with tab2:
    st.subheader("Stock Actual en Cabina")
    try:
      data_inv = ws_inventario.get_all_records()
      if data_inv:
        df_inv = pd.DataFrame(data_inv)
        st.dataframe(df_inv, use_container_width=True)
      else:
        st.info("El inventario está vacío actualmente.")
    except Exception as e:
      st.info("Agrega tu primer producto para visualizar la tabla.")

elif menu == "Finanzas / Caja":
  st.title("Control Financiero y Movimientos")

  tab1, tab2 = st.tabs(["Registrar Movimiento", "Historial Financiero"])

  with tab1:
    st.subheader("Registrar Ingreso o Gasto")
    tipo_mov = st.selectbox("Tipo de Movimiento", ["Ingreso", "Gasto"])
    concepto = st.text_input(
        "Concepto (Ej: Servicio Hydra Glow, Compra de Gasas, etc.)"
    )
    monto = st.number_input(
        "Monto ($ o Moneda Local)", min_value=0.0, step=0.50
    )
    metodo_pago = st.selectbox(
        "Método de Pago", ["Efectivo", "Binance USDT", "Zinli", "BNC / Pago Móvil", "Otro"]
    )

    if st.button("Guardar Movimiento"):
      if concepto and monto > 0:
        ws_finanzas.append_row([
            tipo_mov,
            concepto,
            float(monto),
            metodo_pago,
            str(datetime.now()),
        ])
        st.success("¡Movimiento financiero registrado con éxito!")
      else:
        st.warning("Completa el concepto y un monto válido.")

  with tab2:
    st.subheader("Resumen de Ingresos y Gastos")
    try:
      data_fin = ws_finanzas.get_all_records()
      if data_fin:
        df_fin = pd.DataFrame(data_fin)
        st.dataframe(df_fin, use_container_width=True)
      else:
        st.info("No hay movimientos financieros registrados todavía.")
    except Exception as e:
      st.info("Registra un movimiento para ver la tabla financiera.")

elif menu == "Citas y Agenda":
  st.title("Agenda de Citas - Cabina Estética")
  st.write(
      "Módulo listo para agendar tus pacientes y organizar tus horarios de"
      " atención en GIA SHOP o tu estudio."
  )
  st.info("Próximamente calendario interactivo de citas.")
