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


# Intentamos conectar y asegurar las pestañas
try:
  sh = conectar_google_sheets().spreadsheet

  # Verificamos y creamos automáticamente la pestaña de Clientes si no existe
  try:
    ws_clientes = sh.worksheet("Clientes")
  except:
    ws_clientes = sh.add_worksheet(title="Clientes", rows="100", cols="20")

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
    ["Inicio / Dashboard", "Clientes y Ficha Clínica", "Citas y Agenda"],
)

if menu == "Inicio / Dashboard":
  st.title("Panel de Control - Nay López Skincare")
  st.info(
      "¡Bienvenida a tu sistema de gestión estética en la nube! Todo está"
      " conectado correctamente."
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
      st.info(
          "Registra tu primera paciente para visualizar la tabla de datos."
      )

elif menu == "Citas y Agenda":
  st.title("Agenda de Citas - Cabina Estética")
  st.write("Próximamente módulo de citas y recordatorios.")
