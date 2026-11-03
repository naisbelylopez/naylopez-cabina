import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st

# ==========================================
# CONFIGURACIÓN DE LA BASE DE DATOS SQLITE
# ==========================================
DB_NAME = "cabina_estetica.db"


def init_db():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()

  # Tabla de Clientes y Ficha Clínica
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_completo TEXT NOT NULL,
            cedula TEXT UNIQUE NOT NULL,
            fecha_nacimiento TEXT,
            telefono TEXT,
            email TEXT,
            ocupacion TEXT,
            tipo_piel TEXT,
            fototipo TEXT,
            alergias TEXT,
            embarazo_lactancia TEXT,
            antecedentes_medicos TEXT,
            fecha_registro TEXT
        )
    """)

  # Tabla de Citas / Agenda
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cedula_cliente TEXT,
            servicio TEXT,
            fecha TEXT,
            hora TEXT,
            estado TEXT,
            notas TEXT,
            FOREIGN KEY(cedula_cliente) REFERENCES clientes(cedula)
        )
    """)

  # Tabla de Inventario
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_producto TEXT NOT NULL,
            categoria TEXT,
            stock_actual REAL,
            unidad_medida TEXT,
            stock_minimo REAL,
            costo_unitario REAL,
            vencimiento TEXT
        )
    """)

  # Tabla de Finanzas / Caja
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora TEXT,
            cedula_cliente TEXT,
            tipo_concepto TEXT,
            descripcion TEXT,
            monto_total REAL,
            metodo_pago TEXT
        )
    """)

  conn.commit()
  conn.close()


init_db()

# ==========================================
# INTERFAZ DE USUARIO CON STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Nay López Skincare - Sistema de Cabina",
    page_icon="✨",
    layout="wide",
)

st.sidebar.title("✨ Nay López Skincare")
st.sidebar.subheader("Sistema Operativo de Cabina")

menu = st.sidebar.selectbox(
    "Navegación", [
        "🏠 Inicio / Dashboard",
        "👥 Clientes y Ficha Clínica",
        "📅 Agenda y Citas",
        "📦 Inventario de Insumos",
        "💰 Caja y Finanzas",
    ]
)

# ------------------------------------------
# 1. DASHBOARD INICIAL
# ------------------------------------------
if menu == "🏠 Inicio / Dashboard":
  st.title("Panel de Control General")
  st.markdown(
      "Bienvenida a tu sistema operativo de cabina. Aquí tienes un resumen"
      " rápido del estado de tu estudio."
  )

  conn = sqlite3.connect(DB_NAME)
  df_clientes = pd.read_sql_query("SELECT * FROM clientes", conn)
  df_citas = pd.read_sql_query(
      "SELECT * FROM citas WHERE estado = 'Agendada' OR estado = 'Confirmada'",
      conn,
  )
  df_inventario = pd.read_sql_query("SELECT * FROM inventario", conn)
  conn.close()

  col1, col2, col3 = st.columns(3)
  with col1:
    st.metric("Total Pacientes Registrados", len(df_clientes))
  with col2:
    st.metric("Citas Pendientes", len(df_citas))
  with col3:
    if not df_inventario.empty:
      criticos = len(
          df_inventario[
              df_inventario["stock_actual"] <= df_inventario["stock_minimo"]
          ]
      )
      st.metric("Insumos en Stock Crítico ⚠️", criticos)
    else:
      st.metric("Insumos en Stock Crítico ⚠️", 0)

  st.divider()
  st.subheader("⚠️ Alertas Rápidas de Inventario")
  if not df_inventario.empty:
    bajos = df_inventario[
        df_inventario["stock_actual"] <= df_inventario["stock_minimo"]
    ]
    if not bajos.empty:
      st.warning(
          "Los siguientes productos están por debajo del stock mínimo recomendado:"
      )
      st.dataframe(
          bajos[[
              "nombre_producto",
              "categoria",
              "stock_actual",
              "unidad_medida",
              "stock_minimo",
          ]]
      )
    else:
      st.success("¡Todo el inventario se encuentra en niveles óptimos!")
  else:
    st.info(
        "No hay productos registrados en el inventario todavía. Ve al módulo"
        " correspondiente para agregarlos."
    )

# ------------------------------------------
# 2. CLIENTES Y FICHA CLÍNICA
# ------------------------------------------
elif menu == "👥 Clientes y Ficha Clínica":
  st.title("Gestión de Pacientes y Ficha Estética")

  tab1, tab2 = st.tabs(["Registrar Nuevo Paciente", "Consultar Fichas"])

  with tab1:
    st.subheader("Nueva Ficha Clínica")
    with st.form("form_cliente"):
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
      alergias = st.text_area("Alergias Conocidas (Fármacos, cosméticos, etc.)")
      embarazo = st.selectbox(
          "¿Está embarazada o en periodo de lactancia?", ["No", "Sí"]
      )
      antecedentes = st.text_area(
          "Medicamentos actuales / Uso de retinoides en casa"
      )

      submitted = st.form_submit_button("Guardar Paciente y Ficha")
      if submitted:
        if nombre and cedula:
          try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                """
                            INSERT INTO clientes (nombre_completo, cedula, fecha_nacimiento, telefono, email, ocupacion, tipo_piel, fototipo, alergias, embarazo_lactancia, antecedentes_medicos, fecha_registro)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                (
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
                ),
            )
            conn.commit()
            conn.close()
            st.success(
                f"¡Paciente {nombre} registrada con éxito en el sistema!"
            )
          except sqlite3.IntegrityError:
            st.error(
                "Error: Ya existe una paciente registrada con la cédula"
                f" {cedula}."
            )
        else:
          st.error("Por favor completa al menos el Nombre y la Cédula.")

  with tab2:
    st.subheader("Base de Datos de Pacientes")
    conn = sqlite3.connect(DB_NAME)
    df_c = pd.read_sql_query("SELECT * FROM clientes", conn)
    conn.close()
    if not df_c.empty:
      busqueda = st.text_input("Buscar por Nombre o Cédula")
      if busqueda:
        df_c = df_c[
            df_c["nombre_completo"].str.contains(busqueda, case=False, na=False)
            | df_c["cedula"].str.contains(busqueda, case=False, na=False)
        ]
      st.dataframe(df_c)
    else:
      st.info("No hay pacientes registrados todavía.")

# ------------------------------------------
# 3. AGENDA Y CITAS
# ------------------------------------------
elif menu == "📅 Agenda y Citas":
  st.title("Agenda y Control de Citas")

  col_a, col_b = st.columns(2)

  with col_a:
    st.subheader("Agendar Nueva Cita")
    conn = sqlite3.connect(DB_NAME)
    df_cli = pd.read_sql_query(
        "SELECT cedula, nombre_completo FROM clientes", conn
    )
    conn.close()

    if not df_cli.empty:
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
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            """
                    INSERT INTO citas (cedula_cliente, servicio, fecha, hora, estado, notas)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
            (
                cedula_asociada,
                servicio,
                str(fecha_cita),
                str(hora_cita),
                estado_cita,
                notas_cita,
            ),
        )
        conn.commit()
        conn.close()
        st.success("¡Cita agendada correctamente!")
    else:
      st.warning(
          "Primero debes registrar al menos una paciente en la sección de"
          " Clientes."
      )

  with col_b:
    st.subheader("Calendario de Citas Registradas")
    conn = sqlite3.connect(DB_NAME)
    df_citas = pd.read_sql_query(
        """
            SELECT c.nombre_completo, t.servicio, t.fecha, t.hora, t.estado 
            FROM citas t 
            JOIN clientes c ON t.cedula_cliente = c.cedula
        """,
        conn,
    )
    conn.close()
    if not df_citas.empty:
      st.dataframe(df_citas)
    else:
      st.info("No hay citas programadas.")

# ------------------------------------------
# 4. INVENTARIO DE INSUMOS
# ------------------------------------------
elif menu == "📦 Inventario de Insumos":
  st.title("Control de Inventario y Principios Activos")

  tab1, tab2 = st.tabs(["Registrar / Agregar Producto", "Stock Actual"])

  with tab1:
    with st.form("form_inventario"):
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
          "Unidad de Medida", ["Unidades (un)", "Mililitros (ml)", "Gramos (g)"]
      )
      stock_min = st.number_input(
          "Stock Mínimo de Alerta", min_value=0.0, format="%.2f"
      )
      costo = st.number_input(
          "Costo Unitario ($)", min_value=0.0, format="%.2f"
      )
      vencimiento = st.date_input("Fecha de Caducidad (Opcional)")

      submitted_inv = st.form_submit_button("Guardar en Inventario")
      if submitted_inv:
        if nombre_prod:
          conn = sqlite3.connect(DB_NAME)
          cursor = conn.cursor()
          cursor.execute(
              """
                        INSERT INTO inventario (nombre_producto, categoria, stock_actual, unidad_medida, stock_minimo, costo_unitario, vencimiento)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
              (
                  nombre_prod,
                  cat_prod,
                  stock_act,
                  unidad,
                  stock_min,
                  costo,
                  str(vencimiento),
              ),
          )
          conn.commit()
          conn.close()
          st.success(f"Producto '{nombre_prod}' registrado con éxito.")
        else:
          st.error("El nombre del producto es obligatorio.")

  with tab2:
    conn = sqlite3.connect(DB_NAME)
    df_inv = pd.read_sql_query("SELECT * FROM inventario", conn)
    conn.close()
    if not df_inv.empty:
      st.dataframe(df_inv)
    else:
      st.info("El inventario está vacío.")

# ------------------------------------------
# 5. CAJA Y FINANZAS
# ------------------------------------------
elif menu == "💰 Caja y Finanzas":
  st.title("Control Financiero y Caja")

  col1, col2 = st.columns(2)

  with col1:
    st.subheader("Registrar Ingreso / Pago")
    conn = sqlite3.connect(DB_NAME)
    df_cli = pd.read_sql_query(
        "SELECT cedula, nombre_completo FROM clientes", conn
    )
    conn.close()

    if not df_cli.empty:
      cliente_dict = dict(
          zip(df_cli["nombre_completo"], df_cli["cedula"], strict=False)
      )
      client_name = st.selectbox(
          "Paciente", list(cliente_dict.keys()), key="pago_cliente"
      )
      cedula_pago = cliente_dict[client_name]

      concepto = st.selectbox(
          "Concepto", ["Servicio de Cabina", "Venta de Producto / Home Care"]
      )
      descripcion_pago = st.text_input("Detalle (Ej. Hydra Glow Detox)")
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

      if st.button("Registrar Transacción"):
        if monto > 0:
          conn = sqlite3.connect(DB_NAME)
          cursor = conn.cursor()
          cursor.execute(
              """
                        INSERT INTO transacciones (fecha_hora, cedula_cliente, tipo_concepto, descripcion, monto_total, metodo_pago)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """,
              (
                  str(datetime.now()),
                  cedula_pago,
                  concepto,
                  descripcion_pago,
                  monto,
                  metodo,
              ),
          )
          conn.commit()
          conn.close()
          st.success("¡Transacción registrada y sumada a caja exitosamente!")
        else:
          st.error("El monto debe ser mayor a cero.")
    else:
      st.warning("Registra una paciente antes de procesar transacciones.")

  with col2:
    st.subheader("Resumen y Cierre de Caja")
    conn = sqlite3.connect(DB_NAME)
    df_trans = pd.read_sql_query("SELECT * FROM transacciones", conn)
    conn.close()

    if not df_trans.empty:
      st.dataframe(df_trans[[
          "fecha_hora",
          "tipo_concepto",
          "descripcion",
          "monto_total",
          "metodo_pago",
      ]])
      total_ingresos = df_trans["monto_total"].sum()
      st.metric("Ingresos Totales Registrados ($)", f"${total_ingresos:.2f}")

      st.markdown("### Desglose por Método de Pago")
      desglose = df_trans.groupby("metodo_pago")["monto_total"].sum()
      st.write(desglose)
    else:
      st.info("No hay transacciones registradas.")
