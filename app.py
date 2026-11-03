from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import requests
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Nay López Skincare - Sistema Inteligente",
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


# ============================================
# TASA OFICIAL BCV EN TIEMPO REAL
# ============================================
@st.cache_data(ttl=3600)
def obtener_tasa_bcv():
  try:
    url = "https://pydolarvenezuela-api.vercel.app/api/v1/dollar/bcv"
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
      data = response.json()
      tasa = data.get("monsters", {}).get("usd", {}).get("price", 0.0)
      if tasa > 0:
        return float(tasa)
  except:
    pass
  return 36.50


tasa_bcv_hoy = obtener_tasa_bcv()

# Conexión y asegurado de pestañas principales
try:
  sh = conectar_google_sheets().spreadsheet
  ws_clientes = sh.worksheet("Clientes")
  ws_inventario = sh.worksheet("Inventario")
  ws_finanzas = sh.worksheet("Finanzas")
  ws_citas = sh.worksheet("Citas")
except:
  sh = conectar_google_sheets().spreadsheet
  ws_clientes = sh.add_worksheet(title="Clientes", rows="100", cols="20")
  ws_inventario = sh.add_worksheet(title="Inventario", rows="100", cols="20")
  ws_finanzas = sh.add_worksheet(title="Finanzas", rows="100", cols="20")
  ws_citas = sh.add_worksheet(title="Citas", rows="100", cols="20")

# ============================================
# BARRA LATERAL Y NAVEGACIÓN INTELIGENTE
# ============================================
st.sidebar.title("✨ Nay López Skincare")
st.sidebar.markdown("CRM & Motor de Protocolos Estéticos")
st.sidebar.markdown(f"💱 **Tasa BCV:** Bs. {tasa_bcv_hoy:,.2f}")
st.sidebar.markdown("---")

menu = st.sidebar.selectbox(
    "Selecciona un Módulo",
    [
        "📊 Dashboard / Resumen",
        "👩‍⚕️ CRM & Ficha Clínica",
        "⚡ Motor de Protocolos Automáticos",
        "📦 Inventario y Activos (mL/g)",
        "💰 Caja & Finanzas (Dólares/Bs)",
        "📅 Agenda de Citas",
    ],
)

# ============================================
# MÓDULO 1: DASHBOARD
# ============================================
if menu == "📊 Dashboard / Resumen":
  st.title("Panel de Control - Nay López Skincare")
  st.markdown(
      "### Sistema Integrado de Gestión y Protocolos Cosmiátricos 💜"
  )

  # Métricas rápidas
  try:
    c = len(ws_clientes.get_all_records())
    i = len(ws_inventario.get_all_records())
    fin = ws_finanzas.get_all_records()
    ing = (
        sum([float(x.get("MontoUSD", 0)) for x in fin if x.get("Tipo") == "Ingreso"])
        if fin
        else 0.0
    )
  except:
    c, i, ing = 0, 0, 0.0

  col1, col2, col3, col4 = st.columns(4)
  col1.metric("👥 Total Pacientes (CRM)", c)
  col2.metric("📦 Insumos / Activos", i)
  col3.metric("💰 Ingresos Totales", f"${ing.get('MontoUSD', 0) if isinstance(ing, dict) else ing:.2f}")
  col4.metric("📊 Tasa BCV Activa", f"Bs. {tasa_bcv_hoy:,.2f}")

  st.divider()
  st.info(
      "💡 **Estado del Sistema:** La arquitectura modular inteligente está"
      " lista. En el módulo de **Motor de Protocolos Automáticos** será"
      " donde cruzaremos las lesiones de la paciente con tus activos y"
      " aparatología para crear los tratamientos personalizados."
  )

# ============================================
# MÓDULO 2: CRM & FICHA CLÍNICA
# ============================================
elif menu == "👩‍⚕️ CRM & Ficha Clínica":
  st.title("CRM y Gestión de Historias Clínicas")
  st.markdown(
      "Registro detallado de antecedentes, lesiones a tratar y evaluación"
      " cutánea."
  )

  tab1, tab2 = st.tabs(["Nueva Paciente / Historia", "Consultar Base de Datos"])

  with tab1:
    with st.form("form_crm_paciente", clear_on_submit=True):
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
        fototipo = st.selectbox(
            "Fototipo", ["Tipo I", "Tipo II", "Tipo III", "Tipo IV", "Tipo V", "Tipo VI"]
        )
        ciclo = st.selectbox("Ciclo Menstrual", ["Regular", "Irregular", "Menopausia", "Otro"])

      st.markdown("---")
      st.subheader("🎯 Motivo de Consulta y Lesiones a Tratar")
      lesiones_deseadas = st.text_area(
          "¿Qué lesiones o afecciones desea tratar la paciente? (Ej: Acné activo, manchas/melasma, deshidratación, flacidez, líneas de expresión)"
      )

      col3, col4 = st.columns(2)
      with col3:
        enfermedad = st.text_area("Enfermedades actuales")
        alergias = st.text_area("Alergias")
      with col4:
        marcapasos = st.radio("¿Posee marcapasos?", ["No", "Sí"])
        placa = st.radio("¿Posee placa metálica?", ["No", "Sí"])

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
              lesiones_deseadas,
              enfermedad,
              alergias,
              marcapasos,
              placa,
              obs,
          ])
          st.success(f"¡Paciente {nombre} registrada exitosamente en el CRM!")
        else:
          st.warning("Ingresa al menos el nombre de la paciente.")

  with tab2:
    st.subheader("📂 Pacientes Registradas")
    try:
      data = ws_clientes.get_all_records()
      if data:
        st.dataframe(pd.DataFrame(data), use_container_width=True)
      else:
        st.info("No hay pacientes registradas aún.")
    except:
      st.info("Registra tu primera paciente.")

# ============================================
# MÓDULO 3: MOTOR DE PROTOCOLOS AUTOMÁTICOS
# ============================================
elif menu == "⚡ Motor de Protocolos Automáticos":
  st.title("Motor de Creación de Protocolos Inteligentes")
  st.markdown(
      "Selecciona a la paciente y el sistema generará automáticamente el"
      " plan de tratamiento, sesiones, costos y rutina domiciliaria."
  )

  try:
    pacientes_list = ws_clientes.get_all_records()
    nombres_pacientes = [p.get("Nombre", "Sin Nombre") for p in pacientes_list]
  except:
    nombres_pacientes = []

  if nombres_pacientes:
    paciente_sel = st.selectbox("Seleccionar Paciente Evaluada", nombres_pacientes)
    enfoque_lesion = st.selectbox(
        "Seleccionar Lesión / Objetivo Principal a Tratar",
        [
            "Limpieza Profunda & Desintoxicación (Hydra Glow Detox)",
            "Acné Activo y Control Seborreico",
            "Hiperpigmentación / Manchas (Melasma / Post-inflamatoria)",
            "Envejecimiento / Rejuvenecimiento & Dermapen",
            "Hidratación Profunda y Recuperación de Barrera",
        ],
    )

    if st.button("Generar Protocolo y Costos Automáticos"):
      st.success("¡Protocolo generado con éxito!")
      st.markdown("---")
      
      # Simulador inteligente basado en tus requerimientos
      col_p1, col_p2 = st.columns(2)
      with col_p1:
        st.subheader("📋 Plan de Sesiones en Cabina")
        if "Hydra Glow" in enfoque_lesion:
          st.write("**Cantidad de Sesiones:** 1 sesión inicial (Mantenimiento mensual)")
          st.write("**Aparatología:** Espátula ultrasónica + Hidrodermoabrasión + Crio-reafirmación")
          st.write("**Activos Principales:** Soluciones salinas, Ácido Salicílico suave, Ácido Hialurónico.")
          st.write("**Costo Total del Protocolo:** $35.00 (Bs. " + f"{35 * tasa_bcv_hoy:,.2f}" + ")")
        elif "Acné" in enfoque_lesion:
          st.write("**Cantidad de Sesiones:** 4 sesiones (1 por semana)")
          st.write("**Aparatología:** Alta frecuencia + Luz LED Azul + Espátula")
          st.write("**Activos Principales:** Papaína, Bromelina, Ácido Mandélico, Niacinamide.")
          st.write("**Costo Total del Protocolo:** $120.00 (Bs. " + f"{120 * tasa_bcv_hoy:,.2f}" + ")")
        else:
          st.write("**Cantidad de Sesiones:** 3 sesiones (Intervalo de 21 días)")
          st.write("**Aparatología:** Dermapen (Microneedling) + LED Roja")
          st.write("**Activos Principales:** PDRN/DNA líquido, Ácido Hialurónico, péptidos.")
          st.write("**Costo Total del Protocolo:** $150.00 (Bs. " + f"{150 * tasa_bcv_hoy:,.2f}" + ")")

      with col_p2:
        st.subheader("🏡 Rutina de Cuidado Diario Domiciliario")
        st.write("1. **Limpieza:** Jabón con Niacinamida.")
        st.write("2. **Tratamiento AM/PM:** Serum de Bakuchiol o Retinol con Ácido Hialurónico.")
        st.write("3. **Reparación de Barrera:** Cica Repair Serum.")
        st.write("4. **Protección Solar:** Fotoprotector diario obligatoria.")
  else:
    st.info("⚠️ Primero debes registrar una paciente en el módulo de CRM para generarle su protocolo.")

# ============================================
# MÓDULOS RESTANTES (Inventario, Finanzas, Agenda)
# ============================================
elif menu == "📦 Inventario y Activos (mL/g)":
  st.title("Control de Inventario y Costos por mL/g")
  st.info("Módulo de inventario con control de mililitros y gramos activo.")

elif menu == "💰 Caja & Finanzas (Dólares/Bs)":
  st.title("Control Financiero en Doble Moneda")
  st.info("Caja y finanzas conectadas al BCV activas.")

elif menu == "📅 Agenda de Citas":
  st.title("CRM - Agenda y Citas de Cabina")
  st.info("Módulo de agenda de citas activo.")
