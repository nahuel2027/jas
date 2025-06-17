import streamlit as st
import sqlite3
import pandas as pd
from helpers import obtener_precio_actual, calcular_rendimiento
from streamlit_autorefresh import st_autorefresh

# ⏱️ Refrescar cada 30 segundos
st_autorefresh(interval=30 * 1000, key="datarefresh")

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
st.caption("Visualizá todas tus inversiones en una sola página, sin tener que entrar a múltiples apps.")

# Formulario para agregar inversión con precio dinámico
with st.form("form_inversion"):
    st.subheader("➕ Agregar nueva inversión")
    activo = st.text_input("Activo (ej: BTC, TSLA, GGAL)").upper()
    precio_actual = None

    if activo:
        precio_actual = obtener_precio_actual(activo)
        if precio_actual > 0:
            st.info(f"💵 Precio actual de {activo}: **${precio_actual:,.2f} USD**")
        else:
            st.warning("⚠️ No se pudo obtener el precio actual para {activo}.")

    cantidad = st.number_input("Cantidad que tenés", min_value=0.0, step=0.01)

    if activo and precio_actual and cantidad > 0:
        valor_total = cantidad * precio_actual
        st.success(f"📈 Valor actual de tu inversión: **${valor_total:,.2f} USD**")

    submitted = st.form_submit_button("Guardar inversión")

    if submitted:
        if activo and precio_actual and cantidad > 0:
            cursor.execute(
                "INSERT INTO inversiones (activo, cantidad, precio_compra) VALUES (?, ?, ?)",
                (activo, cantidad, precio_actual)
            )
            conn.commit()
            st.success(f"✅ Inversión en {activo} registrada con éxito.")
        else:
            st.warning("⚠️ Completá correctamente todos los campos.")

# Cargar y mostrar inversiones
df = pd.read_sql_query("SELECT * FROM inversiones", conn)

if not df.empty:
    st.subheader("📊 Tus Inversiones")

    precios_actuales = []
    rendimientos = []

    for index, row in df.iterrows():
        precio_act = obtener_precio_actual(row["activo"])
        rendimiento = calcular_rendimiento(row["cantidad"], row["precio_compra"], precio_act)
        precios_actuales.append(precio_act)
        rendimientos.append(rendimiento)

    df["Precio actual (USD)"] = precios_actuales
    df["Rendimiento (%)"] = [f"{r:.2f}%" for r in rendimientos]
    df["Valor actual (USD)"] = df["cantidad"] * df["Precio actual (USD)"]

    # Reordenar columnas
    df = df[["activo", "cantidad", "precio_compra", "Precio actual (USD)", "Valor actual (USD)", "Rendimiento (%)"]]

    st.dataframe(df.style.format({
        "precio_compra": "${:,.2f}",
        "Precio actual (USD)": "${:,.2f}",
        "Valor actual (USD)": "${:,.2f}"
    }))

    st.subheader("📈 Rendimiento por activo")
    chart_df = df.copy()
    chart_df["Rendimiento (%)"] = [float(r.replace('%', '')) for r in chart_df["Rendimiento (%)"]]
    st.bar_chart(chart_df.set_index("activo")["Rendimiento (%)"])

else:
    st.info("Todavía no cargaste ninguna inversión.")
