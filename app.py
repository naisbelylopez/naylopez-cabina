from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st


# ============================================
# CONFIGURACIÓN DE CONEXIÓN CON GOOGLE SHEETS
# ============================================
def conectar_google_sheets():
  # Definimos el alcance (scope) para Google Sheets y Drive
  scope = [
      "https://www.googleapis.com/auth/spreadsheets",
      "https://www.googleapis.com/auth/drive",
  ]

  # Cargamos las credenciales de forma segura y directa con google-auth
  creds_dict = dict(st.secrets["gcp_service_account"])
  creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
  client = gspread.authorize(creds)

  # Abre tu hoja de Google Sheets
  sheet = client.open("NayLopez_Cabina_DB").sheet1
  return sheet

  try:
    # Si estás usando st.secrets en Streamlit Cloud:
    if "gcp_service_account" in st.secrets:
      creds_dict = dict(st.secrets["gcp_service_account"])
      creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
      # Credenciales locales de respaldo (archivo JSON en la misma carpeta)
      creds = ServiceAccountCredentials.from_json_keyfile_name(
          "credentials.json", scope
      )

    client = gspread.authorize(creds)
    # Abre la hoja de cálculo por su nombre exacto en tu Google Drive
    sheet = client.open("NayLopez_Cabina_DB")
    return sheet
  except Exception as e:
    st.error(
        "Error al conectar con Google Sheets. Verifica tus credenciales o el"
        f" nombre de la hoja: {e}"
    )
    return None


# ==========================================
# INTERFAZ DE USUARIO CON STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Nay López Skincare - Sistema Cloud", page_icon="✨", layout="wide"
)

st.sidebar.title("✨ Nay López Skincare")
st.sidebar.subheader("Sistema en la Nube (Google Sheets)")

menu = st.sidebar.selectbox(
    "Navegación", [
        "🏠 Inicio / Dashboard",
        "👥 Clientes y Ficha Clínica",
        "📅 Agenda y Citas",
        "📦 Inventario de Insumos",
        "💰 Caja y Finanzas",
    ]
)

# Intentar conectar a la hoja de cálculo
sh = conectar_google_sheets()

if sh:
  # ------------------------------------------
  # 1. DASHBOARD INICIAL
  # ------------------------------------------
  if menu == "🏠 Inicio / Dashboard":
    st.title("Panel de Control General (Cloud)")
    st.markdown(
        "Tus datos se sincronizan en tiempo real con tu Google Drive."
    )

    try:
      df_clientes = pd.DataFrame(sh.worksheet("Clientes").get_all_records())
      df_citas = pd.DataFrame(sh.worksheet("Citas").get_all_records())
      df_inventario = pd.DataFrame(sh.worksheet("Inventario").get_all_records())
    except Exception:
      df_clientes, df_citas, df_inventario = (
          pd.DataFrame(),
          pd.DataFrame(),
          pd.DataFrame(),
      )

    col1, col2, col3 = st.columns(3)
    with col1:
      st.metric("Total Pacientes Registrados", len(df_clientes))
    with col2:
      if not df_citas.empty and "estado" in df_citas.columns:
        pendientes = len(
            df_citas[
                (df_citas["estado"] == "Agendada")
                | (df_citas["estado"] == "Confirmada")
            ]
        )
        st.metric("Citas Pendientes", pendientes)
      else:
        st.metric("Citas Pendientes", 0)
    with col3:
      if not df_inventario.empty and "stock_actual" in df_inventario.columns:
        # Asegurar tipos numéricos
        df_inventario["stock_actual"] = pd.to_numeric(
            df_inventario["stock_actual"], errors="coerce"
        )
        df_inventario["stock_minimo"] = pd.to_numeric(
            df_inventario["stock_minimo"], errors="coerce"
        )
        criticos = len(
            df_inventario[
                df_inventario["stock_actual"] <= df_inventario["stock_minimo"]
            ]
        )
        st.metric("Insumos en Stock Crítico ⚠️", criticos)
      else:
        st.metric("Insumos en Stock Crítico ⚠️", 0)

  # ------------------------------------------
  # 2. CLIENTES Y FICHA CLÍNICA
  # ------------------------------------------
  elif menu == "👥 Clientes y Ficha Clínica":
    st.title("Gestión de Pacientes y Ficha Estética")
    tab1, tab2 = st.tabs(["Registrar Nuevo Paciente", "Consultar Fichas"])

    ws_clientes = sh.worksheet("Clientes")

    with tab1:
      st.subheader("Nueva Ficha Clínica")
      with st.form("form_cliente_cloud"):
        col1, col2 = st.columns(2)
        with col1:
          nombre = st.text_input("Nombre Completo")
          cedula = st.text_input("Cédula de Identidad (Única)")
          fnac = st.date_input("Fecha de Nacimiento")
          telefono = st.text_input("Teléfono / WhatsApp")
        with col2:
          email = st.text_input("Correo Electrónico")
          ocupacion = st.text_input("Ocupación")
          tipo_piel = st.selectbox(
              "Tipo de Piel",
              [
                  "Eudérmica",
                  "Seborreica",
                  "Alípica",
                  "Deshidratada",
                  "Mixta",
              ],
          )
          fototipo = st.selectbox(
              "Fototipo Cutáneo (Fitzpatrick)",
              ["Tipo I", "Tipo II", "Tipo III", "Tipo IV", "Tipo V", "Tipo VI"],
          )

        st.markdown("---")
        st.subheader("Anamnesis y Antecedentes")
        alergias = st.text_area("Alergias Conocidas")
        embarazo = st.selectbox(
            "¿Está embarazada o en periodo de lactancia?", ["No", "Sí"]
        )
        antecedentes = st.text_area(
            "Medicamentos actuales / Uso de retinoides"
        )

        submitted = st.form_submit_button("Guardar Paciente en la Nube")
        if submitted:
          if nombre and cedula:
            ws_clientes.append_row([
                nombre,
                cedula,
                str(fnac),
                telefono,
                email,
                ocupacion,
                tipo_piel,
                fototipo,
                alergias,
                embarazo,
                antecedentes,
                str(datetime.now()),
            ])
            st.success(
                f"¡Paciente {nombre} guardada exitosamente en Google Sheets!"
            )
          else:
            st.error("Por favor completa el Nombre y la Cédula.")

    with tab2:
      st.subheader("Base de Datos de Pacientes (Google Drive)")
      data = ws_clientes.get_all_records()
      df_c = pd.DataFrame(data)
      if not df_c.empty:
        busqueda = st.text_input("Buscar por Nombre o Cédula")
        if busqueda:
          df_c = df_c[
              df_c["nombre_completo"].str.contains(
                  busqueda, case=False, na=False
              )
              | df_c["cedula"].str.contains(busqueda, case=False, na=False)
          ]
        st.dataframe(df_c)
      else:
        st.info(
            "No hay registros en la hoja de Clientes de tu Google Drive aún."
        )

  # ------------------------------------------
  # 3. AGENDA Y CITAS
  # ------------------------------------------
  elif menu == "📅 Agenda y Citas":
    st.title("Agenda y Control de Citas")
    col_a, col_b = st.columns(2)

    ws_citas = sh.worksheet("Citas")
    ws_clientes = sh.worksheet("Clientes")
    df_cli = pd.DataFrame(ws_clientes.get_all_records())

    with col_a:
      st.subheader("Agendar Nueva Cita")
      if not df_cli.empty and "cedula" in df_cli.columns:
        cliente_dict = dict(
            zip(df_cli["nombre_completo"], df_cli["cedula"], strict=False)
        )
        selected_client_name = st.selectbox(
            "Seleccionar Paciente", list(cliente_dict.keys())
        )
        cedula_asociada = cliente_dict[selected_client_name]

        servicio = st.selectbox(
            "Servicio / Protocolo",
            [
                "Hydra Glow Detox",
                "Limpieza Profunda + Espátula",
                "Peeling Ácido Mandélico 10%",
                "Dermapen con PDRN",
                "Radiofrecuencia Corporal / Maderoterapia",
            ],
        )
        fecha_cita = st.date_input("Fecha de la Cita")
        hora_cita = st.time_input("Hora de la Cita")
        estado_cita = st.selectbox(
            "Estado", ["Agendada", "Confirmada", "Completada", "Cancelada"]
        )
        notas_cita = st.text_area("Notas internas")

        if st.button("Programar Cita"):
          ws_citas.append_row([
              cedula_asociada,
              servicio,
              str(fecha_cita),
              str(hora_cita),
              estado_cita,
              notas_cita,
          ])
          st.success("¡Cita guardada en Google Sheets!")
      else:
        st.warning(
            "Registra al menos una paciente en la pestaña Clientes primero."
        )

    with col_b:
      st.subheader("Citas Registradas")
      citas_data = ws_citas.get_all_records()
      df_citas = pd.DataFrame(citas_data)
      if not df_citas.empty:
        st.dataframe(df_citas)
      else:
        st.info("No hay citas registradas.")

  # ------------------------------------------
  # 4. INVENTARIO DE INSUMOS
  # ------------------------------------------
  elif menu == "📦 Inventario de Insumos":
    st.title("Control de Inventario y Principios Activos")
    tab1, tab2 = st.tabs(["Registrar Producto", "Stock Actual"])
    ws_inv = sh.worksheet("Inventario")

    with tab1:
      with st.form("form_inv_cloud"):
        nombre_prod = st.text_input("Nombre del Insumo / Producto")
        cat_prod = st.selectbox(
            "Categoría",
            [
                "Ácidos / Peelings",
                "Ampollas / Serums",
                "Mascarillas",
                "Descartables",
                "Aparatología",
            ],
        )
        stock_act = st.number_input(
            "Stock Actual", min_value=0.0, format="%.2f"
        )
        unidad = st.selectbox(
            "Unidad de Medida",
            ["Unidades (un)", "Mililitros (ml)", "Gramos (g)"],
        )
        stock_min = st.number_input(
            "Stock Mínimo de Alerta", min_value=0.0, format="%.2f"
        )
        costo = st.number_input(
            "Costo Unitario ($)", min_value=0.0, format="%.2f"
        )
        vencimiento = st.date_input("Fecha de Caducidad (Opcional)")

        if st.form_submit_button("Guardar Insumo"):
          ws_inv.append_row([
              nombre_prod,
              cat_prod,
              stock_act,
              unidad,
              stock_min,
              costo,
              str(vencimiento),
          ])
          st.success("Producto registrado en la nube.")

    with tab2:
      df_inv = pd.DataFrame(ws_inv.get_all_records())
      if not df_inv.empty:
        st.dataframe(df_inv)
      else:
        st.info("Inventario vacío en Google Sheets.")

  # ------------------------------------------
  # 5. CAJA Y FINANZAS
  # ------------------------------------------
  elif menu == "💰 Caja y Finanzas":
    st.title("Control Financiero y Caja")
    col1, col2 = st.columns(2)
    ws_trans = sh.worksheet("Finanzas")
    ws_clientes = sh.worksheet("Clientes")
    df_cli = pd.DataFrame(ws_clientes.get_all_records())

    with col1:
      st.subheader("Registrar Ingreso / Pago")
      if not df_cli.empty and "cedula" in df_cli.columns:
        cliente_dict = dict(
            zip(df_cli["nombre_completo"], df_cli["cedula"], strict=False)
        )
        client_name = st.selectbox(
            "Paciente", list(cliente_dict.keys()), key="pago_c"
        )
        cedula_pago = cliente_dict[client_name]

        concepto = st.selectbox(
            "Concepto", ["Servicio de Cabina", "Venta de Producto / Home Care"]
        )
        detalles = st.text_input("Detalle (Ej. Hydra Glow Detox)")
        monto = st.number_input("Monto Total ($)", min_value=0.0, format="%.2f")
        metodo = st.selectbox(
            "Método de Pago",
            [
                "Efectivo Divisas",
                "Pago Móvil (VES)",
                "USDT / Binance Pay",
                "Efectivo Bolívares",
            ],
        )

        if st.button("Registrar en Caja"):
          ws_trans.append_row([
              str(datetime.now()),
              cedula_pago,
              concepto,
              detalles,
              monto,
              metodo,
          ])
          st.success("¡Transacción registrada en Google Sheets!")
      else:
        st.warning("Registra una paciente primero.")

    with col2:
      st.subheader("Resumen de Caja")
      df_trans = pd.DataFrame(ws_trans.get_all_records())
      if not df_trans.empty and "monto_total" in df_trans.columns:
        df_trans["monto_total"] = pd.to_numeric(
            df_trans["monto_total"], errors="coerce"
        )
        st.dataframe(df_trans)
        total_ingresos = df_trans["monto_total"].sum()
        st.metric("Ingresos Totales ($)", f"${total_ingresos:.2f}")
      else:
        st.info("No hay transacciones registradas.")
else:
  st.warning(
      "Por favor configura tus credenciales de Google Sheets para conectar"
      " el sistema."
  )
