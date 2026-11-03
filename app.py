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


# Asegurar la conexión y creación automática de pestañas
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
# BARRA LATERAL Y NAVEGACIÓN
# ============================================
st.sidebar.title("✨ Nay López Skincare")
st.sidebar.markdown("Sistema CRM & Protocolos Cosmiátricos")
st.sidebar.markdown("---")

menu = st.sidebar.selectbox(
    "Selecciona un Módulo",
    [
        "📊 Dashboard / Resumen",
        "👩‍⚕️ CRM & Ficha Clínica",
        "⚡ Motor de Protocolos Automáticos",
        "📦 Inventario y Costos (mL/g)",
        "💰 Caja & Finanzas",
        "📅 Agenda de Citas",
    ],
)

# ============================================
# MÓDULO 1: DASHBOARD / RESUMEN
# ============================================
if menu == "📊 Dashboard / Resumen":
  st.title("Panel de Control - Nay López Skincare")
  st.markdown("### ¡Bienvenida a tu estudio estético inteligente! 💜")

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
    ingresos_totales = (
        sum(
            [
                float(x.get("Monto", 0))
                for x in finanzas_data
                if x.get("Tipo") == "Ingreso"
            ]
        )
        if finanzas_data
        else 0.0
    )
  except:
    ingresos_totales = 0.0

  col1, col2, col3 = st.columns(3)
  col1.metric("👥 Total Pacientes", total_pacientes)
  col2.metric("📦 Productos / Activos", total_inventario)
  col3.metric("💰 Ingresos Totales", f"${ingresos_totales:.2f}")

  st.divider()
  st.info(
      "💡 **Consejo:** Utiliza el **Motor de Protocolos Automáticos** para"
      " diseñar los tratamientos de tus pacientes cruzando sus lesiones con"
      " tu inventario de activos."
  )

# ============================================
# MÓDULO 2: CRM & FICHA CLÍNICA
# ============================================
elif menu == "👩‍⚕️ CRM & Ficha Clínica":
  st.title("CRM y Gestión de Historias Clínicas")
  st.markdown("Registro detallado de antecedentes, evaluación y lesiones a tratar.")

  tab1, tab2 = st.tabs(["Registrar Nueva Paciente", "Consultar Base de Datos"])

  with tab1:
    with st.form("form_crm", clear_on_submit=True):
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

        fototipo = st.selectbox(
            "Fototipo Cutáneo (Fitzpatrick)",
            ["Tipo I", "Tipo II", "Tipo III", "Tipo IV", "Tipo V", "Tipo VI"],
        )
        ciclo = st.selectbox(
            "Ciclo Menstrual",
            ["Regular", "Irregular", "Amenorrea", "Menopausia", "No aplica"],
        )

      st.markdown("---")
      st.subheader("🎯 Evaluación y Lesiones a Tratar")
      lesiones = st.text_area(
          "¿Qué lesiones o afecciones desea tratar? (Ej: Acné activo, melasma,"
          " deshidratación, flacidez, líneas de expresión)"
      )

      col3, col4 = st.columns(2)
      with col3:
        enfermedad = st.text_area("¿Padece alguna enfermedad actual?")
        alergias = st.text_area("Alergias conocidas")
      with col4:
        tratamientos_recientes = st.text_area("Tratamientos previos recientes")
        marcapasos = st.radio("¿Posee marcapasos?", ["No", "Sí"])
        placa = st.radio("¿Posee placa u otros implantes metálicos?", ["No", "Sí"])

      obs = st.text_area("Observaciones de la Cosmiatra")
      submit_crm = st.form_submit_button("Guardar Ficha en CRM")

      if submit_crm:
        if nombre:
          tipos_str = ", ".join(
              [
                  t
                  for t, cond in [
                      ("Eudérmica", p_eud),
                      ("Seca", p_sec),
                      ("Grasa", p_gra),
                      ("Mixta", p_mix),
                      ("Alipica", p_ali),
                      ("Deshidratada", p_des),
                      ("Sensible", p_sen),
                  ]
                  if cond
              ]
          )
          ws_clientes.append_row([
              str(datetime.now().strftime("%Y-%m-%d %H:%M")),
              nombre,
              cedula,
              telefono,
              email,
              ocupacion,
              tipos_str,
              fototipo,
              ciclo,
              lesiones,
              enfermedad,
              alergias,
              tratamientos_recientes,
              marcapasos,
              placa,
              obs,
          ])
          st.success(f"¡Paciente {nombre} guardada con éxito en el CRM!")
        else:
          st.warning("Por favor ingresa al menos el nombre y apellido.")

  with tab2:
    st.subheader("📂 Base de Datos de Pacientes")
    try:
      data = ws_clientes.get_all_records()
      if data and len(data) > 0:
        st.dataframe(pd.DataFrame(data), use_container_width=True)
      else:
        st.info("Aún no hay pacientes registradas.")
    except:
      st.info("Registra tu primera paciente para ver la tabla.")

# ============================================
# MÓDULO 3: MOTOR DE PROTOCOLOS AUTOMÁTICOS
# ============================================
elif menu == "⚡ Motor de Protocolos Automáticos":
  st.title("Motor Inteligente de Protocolos Estéticos")
  st.markdown(
      "El sistema analiza las lesiones de la paciente y diseña el tratamiento,"
      " calcula sesiones, costos y la rutina domiciliaria."
  )

  try:
    pacientes_db = ws_clientes.get_all_records()
    nombres = [p.get("Nombre", "") for p in pacientes_db if p.get("Nombre")]
  except:
    nombres = []

  if nombres:
    paciente_elegida = st.selectbox("Seleccionar Paciente", nombres)
    objetivo = st.selectbox(
        "Objetivo o Lesión Principal a Tratar",
        [
            "Limpieza Profunda & Desintoxicación (Hydra Glow Detox)",
            "Control de Acné Activo y Seborregulación",
            "Tratamiento de Hiperpigmentación / Manchas",
            "Rejuvenecimiento Facial con Dermapen",
        ],
    )

    if st.button("Generar Protocolo y Costos Automáticos"):
      st.success("¡Protocolo generado con éxito basado en el historial!")
      st.markdown("---")

      col_a, col_b = st.columns(2)
      with col_a:
        st.subheader("📋 Protocolo de Sesiones en Cabina")
        if "Hydra Glow" in objetivo:
          st.markdown("""
                    * **Sesiones:** 1 sesión inicial (Mantenimiento mensual).
                    * **Aparatología:** Espátula ultrasónica + Hidrodermoabrasión + Crio-reafirmación.
                    * **Activos:** Papaina, Ácido Hialurónico, Soluciones hidratantes.
                    * **Costo Total:** **$35.00**
                    """)
        elif "Acné" in objetivo:
          st.markdown("""
                    * **Sesiones:** 4 sesiones (1 por semana).
                    * **Aparatología:** Alta frecuencia + Luz LED Azul + Espátula.
                    * **Activos:** Papaína, Bromelina, Ácido Mandélico, Niacinamide.
                    * **Costo Total:** **$120.00**
                    """)
        elif "Manchas" in objetivo:
          st.markdown("""
                    * **Sesiones:** 5 sesiones (cada 15 días).
                    * **Aparatología:** Lámpara LED + Espátula ultrasónica.
                    * **Activos:** Ácido Tranexámico, Vitamina C, Ácido Mandélico.
                    * **Costo Total:** **$140.00**
                    """)
        else:
          st.markdown("""
                    * **Sesiones:** 3 sesiones (cada 21 días).
                    * **Aparatología:** Dermapen (Microneedling) + Luz LED Roja.
                    * **Activos:** PDRN/DNA líquido, Péptidos, Ácido Hialurónico.
                    * **Costo Total:** **$150.00**
                    """)

      with col_b:
        st.subheader("🏡 Rutina de Cuidado Diario en Casa")
        st.markdown("""
                1. **Limpieza AM/PM:** Jabón con Niacinamida.
                2. **Tratamiento Activo:** Serum de Bakuchiol o Retinol con Ácido Hialurónico.
                3. **Reparación de Barrera:** Cica Repair Serum.
                4. **Protección:** Fotoprotector solar obligatorio diario.
                """)
  else:
    st.info(
        "⚠️ Debes registrar al menos una paciente en el CRM para activar el"
        " motor de protocolos."
    )

# ============================================
# MÓDULO 4: INVENTARIO Y COSTOS (mL/g)
# ============================================
elif menu == "📦 Inventario y Costos (mL/g)":
  st.title("Control de Inventario y Costos por mL/g")
  st.markdown(
      "Calcula automáticamente el costo por mililitro o gramo de tus cosméticos"
      " y activos."
  )

  tab1, tab2 = st.tabs(["Registrar Producto / Insumo", "Stock y Costos"])

  with tab1:
    with st.form("form_inv", clear_on_submit=True):
      col1, col2 = st.columns(2)
      with col1:
        prod_nombre = st.text_input("Nombre del Producto / Activo / Equipo")
        tipo_med = st.selectbox(
            "Tipo de Medida",
            [
                "Líquido / En Crema (ml)",
                "En Polvo / Sólido (g)",
                "Unidades (Descartables)",
            ],
        )
      with col2:
        costo_usd = st.number_input(
            "Costo Total de Compra ($)", min_value=0.0, step=0.50, value=25.0
        )
        if "ml" in tipo_med or "g" in tipo_med:
          cant_total = st.number_input(
              "Contenido Total (ml o g)", min_value=1.0, value=250.0
          )
        else:
          cant_total = st.number_input(
              "Unidades en el Paquete", min_value=1, value=100
          )

      obs_i = st.text_area("Notas o marca")
      submit_i = st.form_submit_button("Guardar en Inventario")

      if submit_i:
        if prod_nombre:
          costo_unit = costo_usd / cant_total if cant_total > 0 else 0.0
          ws_inventario.append_row([
              str(datetime.now().strftime("%Y-%m-%d %H:%M")),
              prod_nombre,
              tipo_med,
              float(costo_usd),
              float(cant_total),
              round(costo_unit, 4),
              obs_i,
          ])
          st.success(
              f"¡Guardado! Costo por ml/g/unidad: ${costo_unit:.4f}"
          )
        else:
          st.warning("Ingresa el nombre del producto.")

  with tab2:
    st.subheader("📋 Stock Actual y Costos")
    try:
      data_i = ws_inventario.get_all_records()
      if data_i and len(data_i) > 0:
        st.dataframe(pd.DataFrame(data_i), use_container_width=True)
      else:
        st.info("Inventario vacío.")
    except:
      st.info("Agrega un producto para ver la tabla.")

# ============================================
# MÓDULO 5: CAJA Y FINANZAS
# ============================================
elif menu == "💰 Caja & Finanzas":
  st.title("Control Financiero y Caja")
  st.markdown("Registra tus ingresos y gastos de forma directa.")

  tab1, tab2 = st.tabs(["Registrar Movimiento", "Historial y Balance"])

  with tab1:
    with st.form("form_f", clear_on_submit=True):
      col1, col2 = st.columns(2)
      with col1:
        tipo_mov = st.selectbox("Tipo", ["Ingreso", "Gasto"])
        concepto = st.text_input("Concepto (Ej: Tratamiento Hydra Glow)")
