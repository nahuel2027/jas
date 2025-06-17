import streamlit as st
import sqlite3
import pandas as pd
from helpers import obtener_precio_actual, calcular_rendimiento

# Conexión a base de datos SQLite
conn = sqlite3.connect('inversiones.db', check_same_thread=False)
cursor = conn.cursor()

# Crear tabla si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS inversiones (
    id INTEGER PRIMARY KEY,
    activo TEXT,
    cantidad REAL,
    precio_compra REAL
)
''')
conn.commit()

st.title("💰 Inversiones AR")

# Formulario para agregar inversión con precio dinámico
with st.form("form_inversion"):
    st.subheader("➕ Agregar nueva inversión")
    activo = st.text_input("Activo (ej: BTC, TSLA, GGAL)").upper()
    precio_actual = None

    if activo:
        precio_actual = obtener_precio_actual(activo)
        if precio_actual > 0:
            st.info(f"💵 Precio actual de {activo}: **${precio_actual:.2f} USD**")
        else:
            st.warning("⚠️ No se pudo obtener el precio actual.")

    cantidad = st.number_input("Cantidad que tenés", min_value=0.0, step=0.01)

    if activo and precio_actual and cantidad > 0:
        valor_total = cantidad * precio_actual
        st.success(f"📈 Valor actual de tu inversión: **${valor_total:.2f} USD**")

    submitted = st.form_submit_button("Guardar inversión")

    if submitted:
        if activo and precio_actual and cantidad > 0:
            cursor.execute(
                "INSERT INTO inversiones (activo, cantidad, precio_compra) VALUES (?, ?, ?)",
                (activo, cantidad, precio_actual)
            )
            conn.commit()
            st.success(f"✅ Inversión en {activo} registrada con precio actual ${precio_actual:.2f}")
        else:
            st.warning("⚠️ Completá el activo y una cantidad válida.")

# Cargar inversiones
df = pd.read_sql_query("SELECT * FROM inversiones", conn)

if not df.empty:
    st.subheader("📊 Tus Inversiones")

    precios_actuales = []
    rendimientos = []

    for index, row in df.iterrows():
        precio_actual = obtener_precio_actual(row["activo"])
        rendimiento = calcular_rendimiento(row["cantidad"], row["precio_compra"], precio_actual)
        precios_actuales.append(precio_actual)
        rendimientos.append(rendimiento)

    df["Precio actual"] = precios_actuales
    df["Rendimiento"] = rendimientos

    st.dataframe(df)

    st.bar_chart(df.set_index("activo")["Rendimiento"])
else:
    st.info("Todavía no cargaste ninguna inversión.")

