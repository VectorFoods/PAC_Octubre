import streamlit as st # type: ignore
import pandas as pd # type: ignore
import matplotlib.pyplot as plt # type: ignore

# Define the data with the specified columns
data = {
    "Nombre de la actividad": [
        "Cajero vendedor Éxito y Carulla Express",
        "Días de precios especiales Éxito, Surtimax y Súper Inter",
        "Olímpica Miércoles de Plaza", 
        "20% OFF Éxito, Carulla, Éxito express, Carulla express",
        "Farmatodo Halloween 20% OFF",
        "Farmatodo 30% OFF",
        "Farmatodo HOT Sale",
        "Olímpica Octubre 20% OFF"
    ],
    "Ventas totales periodo anterior": [10795, 4779, 1491, 1765, 2771, 2673, 6894, 1057],
    "Ventas totales durante la actividad": [11093, 8406, 3215, 1241, 2397, 2551, 6772, 962],
    "Crecimiento bruto en unidades": [298, 3627, 1724, -524, -374, -122, -122, -95],
    "Crecimiento bruto (%)": [2.76, 75.89, 115.63, -29.69, -13.5, -4.56, -1.77, -8.99],
    "Total descuento": [0, 16229042, 6995579, 5808437, 3952672, 5672823, 7780890, 4161680],
    "Crecimiento real monetario": [-24862745, 18890622, 7712207, -17564739, -8201411, -6560302, -5810470, -6293109]
}

# Load the data into a DataFrame
df = pd.DataFrame(data)

# Streamlit page configuration
st.set_page_config(page_title="Tablero de Análisis de KPIs", layout="wide")
st.title("Tablero de Análisis de KPIs")

# KPI Metrics
total_prev_sales = df["Ventas totales periodo anterior"].sum()
total_curr_sales = df["Ventas totales durante la actividad"].sum()
total_units_growth = df["Crecimiento bruto en unidades"].sum()
total_pct_growth = (total_units_growth / total_prev_sales) * 100
total_discount = df["Total descuento"].sum()
total_monetary_growth = df["Crecimiento real monetario"].sum()

st.subheader("Métricas Clave")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Ventas Totales Periodo Anterior", f"{total_prev_sales:,.0f}")
    st.metric("Ventas Totales Actividad", f"{total_curr_sales:,.0f}")
with col2:
    st.metric("Crecimiento Bruto Total Unidades", f"{total_units_growth:,.0f}")
    st.metric("Crecimiento Bruto Total (%)", f"{total_pct_growth:.2f}%")
with col3:
    st.metric("Total Descuentos", f"${total_discount:,.0f}")
    st.metric("Crecimiento Real Monetario Total", f"${total_monetary_growth:,.0f}")

# Display the DataFrame as a table with a total row
st.subheader("Tabla de Datos de KPIs")
total_row = df.sum().to_frame().T
total_row.loc[:, "Nombre de la actividad"] = "Total"
total_row["Crecimiento bruto (%)"] = (total_row["Crecimiento bruto en unidades"] / total_row["Ventas totales periodo anterior"]) * 100
total_row["Crecimiento real monetario"] = total_row["Crecimiento real monetario"].apply(lambda x: f"${x:,.0f}")
display_df = pd.concat([df, total_row], ignore_index=True)
st.write(display_df)

# Plot: Crecimiento Bruto en Unidades por Actividad
st.subheader("Crecimiento Bruto en Unidades por Actividad")
fig1, ax1 = plt.subplots(figsize=(10, 6))
ax1.barh(df.sort_values("Crecimiento bruto en unidades")["Nombre de la actividad"], df.sort_values("Crecimiento bruto en unidades")["Crecimiento bruto en unidades"])
ax1.set_xlabel("Crecimiento Bruto en Unidades")
ax1.set_ylabel("Actividad")
ax1.set_title("Crecimiento Bruto en Unidades por Actividad")
st.pyplot(fig1)

# Plot: Crecimiento Bruto (%) por Actividad
st.subheader("Crecimiento Bruto (%) por Actividad")
fig2, ax2 = plt.subplots(figsize=(10, 6))
ax2.barh(df.sort_values("Crecimiento bruto (%)")["Nombre de la actividad"], df.sort_values("Crecimiento bruto (%)")["Crecimiento bruto (%)"])
ax2.set_xlabel("Crecimiento Bruto (%)")
ax2.set_ylabel("Actividad")
ax2.set_title("Crecimiento Bruto (%) por Actividad")
st.pyplot(fig2)

# Plot: Crecimiento Real Monetario por Actividad
st.subheader("Crecimiento Real Monetario por Actividad")
fig3, ax3 = plt.subplots(figsize=(10, 6))
ax3.barh(df.sort_values("Crecimiento real monetario")["Nombre de la actividad"], df.sort_values("Crecimiento real monetario")["Crecimiento real monetario"] / 1000000)
ax3.set_xlabel("Crecimiento Real Monetario (Millones)")
ax3.set_ylabel("Actividad")
ax3.set_title("Crecimiento Real Monetario por Actividad")
st.pyplot(fig3)