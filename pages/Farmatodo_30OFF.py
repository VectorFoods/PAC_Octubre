import streamlit as st # type: ignore
import pandas as pd # type: ignore
import plotly.graph_objs as go # type: ignore

# Definir la función para cargar los datos desde Excel, con cache
@st.cache_data
def cargar_datos():
    try:
        # Ruta al archivo Excel
        file_path = "PAC_Oct/data/PAC_Oct.xlsx"
        sheet_name = 'Análisis PAC'

        # Leer el archivo Excel y seleccionar la hoja especificada
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        df.columns = df.columns.str.strip()  # Limpiar los nombres de las columnas
        df['Código Homologado'] = df['Código Homologado'].str.strip().str.upper()  # Limpiar y estandarizar
        df['Banner'] = df['Banner'].str.strip()
        return df
    except Exception as e:
        # Si hay un error, devolver un mensaje de error
        st.error(f"Error al cargar los datos: {e}")
        return None

# Cargar los datos
df = cargar_datos()

# Verificar si los datos se cargaron correctamente
if df is not None:
    # Parámetros de selección
    banners_seleccionados = ["Farmatodo"]
    productos_seleccionados = ["6PBD0", "6PPL0", "8PCS0", "8PBS0", "PBD100CC0", "PLL100", "PSR100"]
    
    # Definir las fechas específicas para octubre y septiembre
    fechas_octubre = pd.to_datetime(['2024-10-10', '2024-10-15', '2024-10-20', '2024-10-21', '2024-10-22'])
    fechas_septiembre = pd.to_datetime(['2024-09-10', '2024-09-15', '2024-09-20', '2024-09-21', '2024-09-22'])

    # Función para filtrar datos
    def filtrar_datos(df, fechas, banners, productos):
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df_filtrado = df[df['Date'].isin(fechas)]
        df_filtrado = df_filtrado[df_filtrado['Banner'].isin(banners) & df_filtrado['Código Homologado'].isin(productos)]
        return df_filtrado

    # Filtrar datos para octubre y septiembre usando las fechas específicas
    datos_octubre = filtrar_datos(df, fechas_octubre, banners_seleccionados, productos_seleccionados)
    datos_septiembre = filtrar_datos(df, fechas_septiembre, banners_seleccionados, productos_seleccionados)

    # Asegurar que las columnas numéricas estén correctas
    for col in ['Cantidad Vendida Actual', 'Precio']:
        datos_octubre[col] = pd.to_numeric(datos_octubre[col], errors='coerce').fillna(0)
        datos_septiembre[col] = pd.to_numeric(datos_septiembre[col], errors='coerce').fillna(0)

    # Agrupar datos y calcular métricas
    ventas_agrupadas_octubre = datos_octubre.groupby('Código Homologado').agg({'Cantidad Vendida Actual': 'sum'})['Cantidad Vendida Actual']
    ventas_agrupadas_septiembre = datos_septiembre.groupby('Código Homologado').agg({'Cantidad Vendida Actual': 'sum'})['Cantidad Vendida Actual']

    # Calcular las ventas monetarias para octubre y septiembre
    ventas_monetarias_octubre_bruto = (datos_octubre['Cantidad Vendida Actual'] * datos_octubre['Precio']).groupby(datos_octubre['Código Homologado']).sum()  # Bruto sin descuento
    ventas_monetarias_octubre = ventas_monetarias_octubre_bruto * 0.70  # Aplicar el 30% de descuento
    ventas_monetarias_septiembre = (datos_septiembre['Cantidad Vendida Actual'] * datos_septiembre['Precio']).groupby(datos_septiembre['Código Homologado']).sum()

    # Asegurarse de que todos los productos estén presentes en el índice
    ventas_monetarias_octubre = ventas_monetarias_octubre.reindex(productos_seleccionados, fill_value=0)
    ventas_monetarias_septiembre = ventas_monetarias_septiembre.reindex(productos_seleccionados, fill_value=0)

    # Calcular el crecimiento monetario
    crecimiento_monetario = ventas_monetarias_octubre - ventas_monetarias_septiembre
    crecimiento_porcentaje = (crecimiento_monetario / ventas_monetarias_septiembre.replace(0, pd.NA)) * 100

    # Crear DataFrame de utilidad
    utilidad_df = pd.DataFrame({
        'Producto': ventas_monetarias_octubre.index,
        'Ventas Monetarias Septiembre': ventas_monetarias_septiembre.values,
        'Ventas Monetarias Octubre': ventas_monetarias_octubre.values,
        'Crecimiento Monetario': crecimiento_monetario.values,
        'Crecimiento (%)': crecimiento_porcentaje.values
    }).reset_index(drop=True)

    # Fila total
    total_fila = pd.DataFrame({
        'Producto': ['Total'],
        'Ventas Monetarias Septiembre': [ventas_monetarias_septiembre.sum()],
        'Ventas Monetarias Octubre': [ventas_monetarias_octubre.sum()],
        'Crecimiento Monetario': [crecimiento_monetario.sum()],
        'Crecimiento (%)': [(crecimiento_monetario.sum() / ventas_monetarias_septiembre.sum()) * 100]
    })

    utilidad_df = pd.concat([utilidad_df[utilidad_df['Producto'] != 'Total'].sort_values(by='Ventas Monetarias Octubre', ascending=False), total_fila], ignore_index=True)

    # Calcular el total de ventas en unidades y el crecimiento
    total_ventas_unidades_septiembre = ventas_agrupadas_septiembre.sum()
    total_ventas_unidades_octubre = ventas_agrupadas_octubre.sum()
    crecimiento_bruto_unidades = total_ventas_unidades_octubre - total_ventas_unidades_septiembre
    crecimiento_bruto_porcentaje_unidades = ((total_ventas_unidades_octubre - total_ventas_unidades_septiembre) / total_ventas_unidades_septiembre) * 100

    # KPI: Crecimiento Real Monetario Total
    crecimiento_real_monetario_total = crecimiento_monetario.sum()  # Total Real Monetary Growth

    # KPI: Total Discount in October
    total_descuento_octubre = ventas_monetarias_octubre_bruto.sum() * 0.30  # Total discount in October (30% discount)

    # Interfaz en Streamlit
    st.title("Farmatodo 30% OFF")

    # Dividir en dos columnas para los KPIs
    col1, col2 = st.columns(2)

    # Columna 1: Primeros cuatro KPIs
    with col1:
        st.metric("Ventas Totales Septiembre (Unidades)", f"{total_ventas_unidades_septiembre:,.0f}")
        st.metric("Ventas Totales Octubre (Unidades)", f"{total_ventas_unidades_octubre:,.0f}")
        st.metric("Crecimiento Bruto en Unidades", f"{crecimiento_bruto_unidades:,.0f}")
        st.metric("Crecimiento Bruto en Unidades (%)", f"{crecimiento_bruto_porcentaje_unidades:.2f}%")

    # Columna 2: KPIs adicionales
    with col2:
        st.metric("Total Descuento Octubre", f"${total_descuento_octubre:,.2f}")
        st.metric("Crecimiento Real Monetario Total", f"${crecimiento_real_monetario_total:,.2f}")
        
    # Mostrar tabla de utilidad
    st.subheader("Análisis de Utilidad por Producto")
    st.dataframe(utilidad_df)

    # Graficar comparativo de ventas monetarias
    st.subheader("Comparativo de Ventas Monetarias (Octubre vs Septiembre)")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=utilidad_df[utilidad_df['Producto'] != 'Total']['Producto'],
        x=utilidad_df[utilidad_df['Producto'] != 'Total']['Ventas Monetarias Octubre'],
        name='Octubre',
        orientation='h'
    ))
    fig.add_trace(go.Bar(
        y=utilidad_df[utilidad_df['Producto'] != 'Total']['Producto'],
        x=utilidad_df[utilidad_df['Producto'] != 'Total']['Ventas Monetarias Septiembre'],
        name='Septiembre',
        orientation='h'
    ))
    fig.update_layout(
        title="Comparativo de Ventas Monetarias",
        xaxis_title="Ventas Monetarias",
        barmode='group',
        yaxis=dict(autorange="reversed")
    )
    st.plotly_chart(fig)

else:
    st.error("No se pudo cargar los datos.")
