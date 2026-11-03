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

  # Pestaña de Clientes
  try:
    ws_clientes = sh.worksheet("Clientes")
  except:
    ws_clientes = sh.add_worksheet(title="Clientes", rows="100", cols="20")
    ws_clientes.append_row([
        "Fecha",
        "Nombre",
        "Teléfono",
        "Email",
        "Tipo de Piel",
        "Fototipo",
        "Observaciones",
        "Tratamiento",
    ])

  # Pestaña de Citas / Agenda (Para las citas del día)
  try:
    ws_citas = sh.worksheet("Citas")
  except:
    ws_citas = sh.add_worksheet(title="Citas", rows="100", cols="20")
    ws_citas.append_row(
        ["FechaCita", "Hora", "Cliente", "Tratamiento", "Estado"]
    )

  # Pestaña de Inventario
  try:
    ws_inventario = sh.worksheet("Inventario")
  except:
    ws_inventario = sh.add_worksheet(title="Inventario", rows="100", cols="20")
    ws_inventario.append_row(
        ["Producto", "Categoria", "Stock", "Costo", "Fecha"]
    )

  # Pestaña de Finanzas
  try:
    ws_finanzas = sh.worksheet("Finanzas")
  except:
    ws_finanzas = sh.add_worksheet(title="Finanzas", rows="100", cols="20")
    ws_finanzas.append_row(["Tipo", "Concepto", "Monto", "MetodoPago", "Fecha"])

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

# ============================================
# MÓDULO 1: DASHBOARD / RESUMEN GENERAL
# ============================================
if menu == "Inicio / Dashboard":
  st.title("Panel de Control - Nay López Skincare")
  st.markdown("### ¡Bienvenida a tu cabina estética en la nube! 💜")
  st.write(
      "Aquí tienes el resumen general de tu actividad y las pacientes programadas"
      " para hoy."
  )

  # Obtenemos datos de las hojas de cálculo de forma segura
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
      # Filtramos los ingresos para sumarlos
      ingresos_totales = (
          df_fin[df_fin["Tipo"] == "Ingreso"]["Monto"].astype(float).sum()
      )
    else:
      ingresos_totales = 0.0
  except:
    ingresos_totales = 0.0

  # Citas para hoy
  fecha_hoy = datetime.now().strftime("%Y-%m-%d")
  citas_hoy_count = 0
  citas_hoy_lista = []
  try:
    citas_data = ws_citas.get_all_records()
    if citas_data:
      for cita in citas_data:
        # Comparamos si la fecha de la cita coincide con hoy
        if str(cita.get("FechaCita", "")).startswith(fecha_hoy):
          citas_hoy_count += 1
          citas_hoy_lista.append(cita)
  except:
    pass

  # Mostramos métricas visuales en columnas (KPIs)
  col1, col2, col3, col4 = st.columns(4)

  with col1:
    st.metric(
        label="📅 Pacientes para Hoy",
        value=f"{citas_hoy_count} citas",
        help="Citas agendadas para el día de hoy",
    )
  with col2:
    st.metric(label="👥 Total Pacientes", value=total_clientes)
  with col3:
    st.metric(label="📦 Productos en Inventario", value=total_productos)
  with col4:
    st.metric(label="💰 Ingresos Registrados", value=f"${ingresos_totales:.2f}")

  st.divider()

  # Sección de pacientes a atender hoy detalladas
  st.subheader(f"✨ Agenda del Día ({fecha_hoy})")
  if citas_hoy_count > 0:
    df_citas_hoy = pd.DataFrame(citas_hoy_lista)
    st.dataframe(df_citas_hoy, use_container_width=True)
  else:
    st.info(
        "No tienes citas agendadas para el día de hoy. (Puedes ir al módulo de"
        " Citas y Agenda para programar)."
    )

elif menu == "Clientes y Ficha Clínica":
  st.title("Gestión de Pacientes y Ficha Estética")
  st.markdown(
      "Historia clínica completa y registro detallado de cada paciente."
  )

  tab1, tab2 = st.tabs(["Registrar Nueva Paciente", "Consultar Fichas"])

  with tab1:
    st.subheader("📝 Ficha Clínica y Datos de la Paciente")

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
          "Fototipo Cutáneo (Fitzpatrick)",
          ["Tipo I", "Tipo II", "Tipo III", "Tipo IV", "Tipo V", "Tipo VI"],
      )

      ciclo_menstrual = st.selectbox(
          "¿Cómo es su ciclo menstrual?",
          ["Regular", "Irregular", "Ausente / Amenorrea", "Menopausia", "No aplica"],
      )

    st.markdown("---")
    st.subheader("🔍 Antecedentes y Seguridad en Cabina")

    col3, col4 = st.columns(2)
    with col3:
      enfermedad = st.text_area("¿Padece alguna enfermedad actual?")
      antecedentes = st.text_area("Antecedentes Médicos")
      alergias = st.text_area("Alergias conocidas")

    with col4:
      tratamientos_recientes = st.text_area(
          "Tratamientos estéticos / médicos recientes"
      )
      marcapasos = st.radio("¿Posee marcapasos?", ["No", "Sí"])
      placa_metalica = st.radio(
          "¿Posee placa u otros implantes metálicos?", ["No", "Sí"]
      )

    observaciones = st.text_area("Observaciones Generales de la Cosmiatra")

    if st.button("Guardar Ficha Clínica Completa"):
      if nombre:
        tipos_seleccionados = []
        if tp_eudermica:
          tipos_seleccionados.append("Eudérmica")
        if tp_seca:
          tipos_seleccionados.append("Seca")
        if tp_grasa:
          tipos_seleccionados.append("Grasa")
        if tp_mixta:
          tipos_seleccionados.append("Mixta")
        if tp_alipica:
          tipos_seleccionados.append("Alipica")
        if tp_deshidratada:
          tipos_seleccionados.append("Deshidratada")
        if tp_sensible:
          tipos_seleccionados.append("Sensible")

        tipo_piel_str = (
            ", ".join(tipos_seleccionados)
            if tipos_seleccionados
            else "No especificado"
        )

        ws_clientes.append_row([
            str(datetime.now().strftime("%Y-%m-%d %H:%M")),
            nombre,
            cedula,
            telefono,
            email,
            ocupacion,
            tipo_piel_str,
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
        st.success(
            f"¡Ficha clínica de {nombre} guardada con éxito en Google Sheets!"
        )
      else:
        st.warning("Por favor ingresa al menos el nombre y apellido de la paciente.")

  with tab2:
    st.subheader("📂 Base de Datos de Pacientes y Fichas Clínicas")
    try:
      data_clientes = ws_clientes.get_all_records()
      # Validamos si hay datos reales cargados
      if data_clientes and len(data_clientes) > 0:
        df_clientes = pd.DataFrame(data_clientes)
        st.dataframe(df_clientes, use_container_width=True)
      else:
        st.info(
            "📋 Aún no hay pacientes registradas en la hoja. Ve a la pestaña"
            " 'Registrar Nueva Paciente' para agregar la primera."
        )
    except Exception:
      st.info(
          "📋 Tu base de datos está lista. Agrega tu primera paciente para"
          " visualizar la tabla aquí."
      )
elif menu == "Inventario / Productos":
  st.title("Control de Inventario y Costos de Cabina")
  st.markdown(
      "Gestiona tus insumos descartables (unidades) y tus cosméticos"
      " profesionales (mililitros/gramos) de forma ágil."
  )

  tab1, tab2 = st.tabs(["Registrar Producto / Insumo", "Stock y Costos Actuales"])

  with tab1:
    st.subheader("📦 Agregar Producto o Insumo a la Cabina")
    st.info(
        "💡 Rellena los datos. Al hacer clic en guardar, el formulario se"
        " limpiará automáticamente para que puedas ingresar el siguiente"
        " producto."
    )

    # Creamos un formulario interactivo que limpia los campos al enviar
    with st.form("form_inventario", clear_on_submit=True):
      col1, col2 = st.columns(2)
      with col1:
        prod_nombre = st.text_input(
            "Nombre del Producto / Activo (Ej: Limpiador, Gasa, Ácido Mandélico)"
        )
        tipo_medida = st.selectbox(
            "Tipo de Inventario",
            [
                "Líquido / En Crema (Mililitros - ml)",
                "En Polvo / Sólido (Gramos - g)",
                "Unidades (Descartables / Venta)",
            ],
        )

      with col2:
        precio_compra = st.number_input(
            "Costo Total de Compra ($)", min_value=0.0, step=0.50, value=25.0
        )
        
        if "ml" in tipo_medida or "g" in tipo_medida:
          cantidad_total = st.number_input(
              "Contenido Total del Envase (ml o g)",
              min_value=1.0,
              step=1.0,
              value=250.0,
          )
        else:
          cantidad_total = st.number_input(
              "Cantidad de Unidades en el Paquete",
              min_value=1,
              step=1,
              value=100,
          )

      observaciones_prod = st.text_area(
          "Notas o marca del producto (Ej: Uso exclusivo para Hydra Glow Detox)"
      )

      # Botón de envío del formulario
      submit_button = st.form_submit_button(
          "Guardar y Limpiar para el Siguiente"
      )

      if submit_button:
        if prod_nombre:
          if cantidad_total > 0:
            costo_unitario = precio_compra / cantidad_total
          else:
            costo_unitario = 0.0

          # Guardamos en la hoja de inventario
          ws_inventario.append_row([
              str(datetime.now().strftime("%Y-%m-%d %H:%M")),
              prod_nombre,
              tipo_medida,
              float(precio_compra),
              float(cantidad_total),
              round(costo_unitario, 4),
              observaciones_prod,
          ])
          st.success(
              f"¡'{prod_nombre}' registrado con éxito! Costo por"
              f" {'ml/g' if 'ml' in tipo_medida or 'g' in tipo_medida else 'unidad'}:"
              f" ${costo_unitario:.4f}"
          )
        else:
          st.warning("Por favor ingresa al menos el nombre del producto.")

  with tab2:
    st.subheader("📋 Stock Actual y Costos por Unidad/Mililitro")
    st.markdown(
        "Aquí puedes ver en tiempo real todo lo que tienes registrado en tu"
        " base de datos."
    )
    try:
      data_inv = ws_inventario.get_all_records()
      if data_inv and len(data_inv) > 0:
        df_inv = pd.DataFrame(data_inv)
        st.dataframe(df_inv, use_container_width=True)
      else:
        st.info(
            "📦 El inventario está vacío. Agrega tu primer producto en la pestaña"
            " de al lado."
        )
    except Exception:
      st.info(
          "📦 Agrega tu primer producto para visualizar la tabla de costos y"
          " stock."
      )

elif menu == "Finanzas / Caja":
  st.title("Control Financiero y Caja")
  st.markdown("Registra tus ingresos por tratamientos y controla los gastos de tu cabina.")

  tab1, tab2 = st.tabs(["Registrar Movimiento", "Historial y Resumen"])

  with tab1:
    st.subheader("💵 Registrar Ingreso o Gasto")
    st.info("💡 El formulario se limpiará automáticamente al guardar para agilizar tus registros.")

    with st.form("form_finanzas", clear_on_submit=True):
      col1, col2 = st.columns(2)
      with col1:
        tipo_mov = st.selectbox("Tipo de Movimiento", ["Ingreso", "Gasto"])
        concepto = st.text_input("Concepto (Ej: Limpieza facial Hydra Glow, Compra de gasas, etc.)")
        monto = st.number_input("Monto ($)", min_value=0.0, step=0.50, value=10.0)

      with col2:
        metodo_pago = st.selectbox(
            "Método de Pago", 
            ["Efectivo", "Binance USDT", "Zinli", "BNC / Pago Móvil", "Otro"]
        )
        categoria_fin = st.selectbox(
            "Categoría",
            [
                "Servicio Estético / Tratamiento",
                "Venta de Producto Domiciliario",
                "Compra de Insumos / Cosméticos",
                "Servicios / Alquiler / Operativo",
                "Otro"
            ]
        )

      notas_fin = st.text_area("Notas adicionales (Opcional)")

      submit_fin = st.form_submit_button("Guardar Movimiento en Caja")

      if submit_fin:
        if concepto and monto > 0:
          ws_finanzas.append_row([
              str(datetime.now().strftime("%Y-%m-%d %H:%M")),
              tipo_mov,
              concepto,
              float(monto),
              metodo_pago,
              categoria_fin,
              notas_fin
          ])
          st.success(f"¡Movimiento de tipo '{tipo_mov}' registrado con éxito en Google Sheets!")
        else:
          st.warning("Por favor completa el concepto y asegúrate de colocar un monto válido.")

  with tab2:
    st.subheader("📊 Historial de Movimientos y Balance")
    try:
      data_fin = ws_finanzas.get_all_records()
      if data_fin and len(data_fin) > 0:
        df_fin = pd.DataFrame(data_fin)
        
        # Mostramos métricas rápidas de ingresos vs gastos si las columnas existen
        if "Tipo" in df_fin.columns and "Monto" in df_fin.columns:
          ingresos_df = df_fin[df_fin["Tipo"] == "Ingreso"]["Monto"].astype(float).sum()
          gastos_df = df_fin[df_fin["Tipo"] == "Gasto"]["Monto"].astype(float).sum()
          balance_df = ingresos_df - gastos_df

          col_m1, col_m2, col_m3 = st.columns(3)
          col_m1.metric("💰 Total Ingresos", f"${ingresos_df:.2f}")
          col_m2.metric("📉 Total Gastos", f"${gastos_df:.2f}")
          col_m3.metric("✨ Balance Neto", f"${balance_df:.2f}")
          st.divider()

        st.dataframe(df_fin, use_container_width=True)
      else:
        st.info("📂 Aún no hay movimientos financieros registrados. ¡Agrega el primero en la pestaña de al lado!")
    except Exception:
      st.info("📂 Registra tu primer movimiento para visualizar la tabla y el balance financiero.")
elif menu == "Citas y Agenda":
  st.title("Agenda de Citas - Cabina Estética")
  st.info("Módulo en espera.")
