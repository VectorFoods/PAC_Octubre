import streamlit as st # type: ignore
import pandas as pd # type: ignore
import plotly.graph_objs as go # type: ignore

# Definir la función para cargar los datos desde Excel, con cache
@st.cache_data
def cargar_datos():
    try:
        # Ruta al archivo Excel
        file_path = 'data/PAC_Oct.xlsx'
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
    productos_seleccionados_1 = ["6PBD0", "6PPL0", "8PCS0", "8PBS0", "PBD100CC0", "PLL100", "PSR100"]
    productos_seleccionados_2 = ["PL25", "PSR25", "PSV25", "PBD25", "PMP25", "PCC25", "YSM25", "PCT25", "PAP25", "BARQ0", "CDS14", "CQC14", "CSM14", "BAC18", "BCDQ18", "BPA18"]
    
    # Definir las fechas específicas para octubre y septiembre
    fecha_inicio_octubre = pd.to_datetime('2024-10-17')
    fecha_fin_octubre = pd.to_datetime('2024-10-21')
    fecha_inicio_septiembre = pd.to_datetime('2024-09-17')
    fecha_fin_septiembre = pd.to_datetime('2024-09-21')

    # Función para filtrar datos
    def filtrar_datos(df, fecha_inicio, fecha_fin, banners, productos):
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df_filtrado = df[(df['Date'] >= fecha_inicio) & (df['Date'] <= fecha_fin)]
        df_filtrado = df_filtrado[df_filtrado['Banner'].isin(banners) & df_filtrado['Código Homologado'].isin(productos)]
        return df_filtrado

    # Filtrar datos para productos con un 30% de descuento (productos_seleccionados_1)
    datos_octubre_30 = filtrar_datos(df, fecha_inicio_octubre, fecha_fin_octubre, banners_seleccionados, productos_seleccionados_1)
    datos_septiembre_30 = filtrar_datos(df, fecha_inicio_septiembre, fecha_fin_septiembre, banners_seleccionados, productos_seleccionados_1)

    # Filtrar datos para productos con un 20% de descuento (productos_seleccionados_2)
    datos_octubre_20 = filtrar_datos(df, fecha_inicio_octubre, fecha_fin_octubre, banners_seleccionados, productos_seleccionados_2)
    datos_septiembre_20 = filtrar_datos(df, fecha_inicio_septiembre, fecha_fin_septiembre, banners_seleccionados, productos_seleccionados_2)

    # Convertir columnas a numéricas y manejar valores faltantes
    for col in ['Cantidad Vendida Actual', 'Precio']:
        datos_octubre_30[col] = pd.to_numeric(datos_octubre_30[col], errors='coerce').fillna(0)
        datos_septiembre_30[col] = pd.to_numeric(datos_septiembre_30[col], errors='coerce').fillna(0)
        datos_octubre_20[col] = pd.to_numeric(datos_octubre_20[col], errors='coerce').fillna(0)
        datos_septiembre_20[col] = pd.to_numeric(datos_septiembre_20[col], errors='coerce').fillna(0)

    # Agrupar y calcular las ventas para productos con 30% de descuento
    ventas_30_octubre_bruto = (datos_octubre_30['Cantidad Vendida Actual'] * datos_octubre_30['Precio']).groupby(datos_octubre_30['Código Homologado']).sum()
    ventas_30_octubre = ventas_30_octubre_bruto * 0.70
    ventas_30_septiembre = (datos_septiembre_30['Cantidad Vendida Actual'] * datos_septiembre_30['Precio']).groupby(datos_septiembre_30['Código Homologado']).sum()

    # Agrupar y calcular las ventas para productos con 20% de descuento
    ventas_20_octubre_bruto = (datos_octubre_20['Cantidad Vendida Actual'] * datos_octubre_20['Precio']).groupby(datos_octubre_20['Código Homologado']).sum()
    ventas_20_octubre = ventas_20_octubre_bruto * 0.80
    ventas_20_septiembre = (datos_septiembre_20['Cantidad Vendida Actual'] * datos_septiembre_20['Precio']).groupby(datos_septiembre_20['Código Homologado']).sum()

    # Unificar productos en un único DataFrame para el análisis
    ventas_monetarias_octubre = pd.concat([ventas_30_octubre, ventas_20_octubre]).reindex(productos_seleccionados_1 + productos_seleccionados_2, fill_value=0)
    ventas_monetarias_septiembre = pd.concat([ventas_30_septiembre, ventas_20_septiembre]).reindex(productos_seleccionados_1 + productos_seleccionados_2, fill_value=0)

    # Calcular crecimiento monetario y porcentaje
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

    # Agregar fila total
    total_fila = pd.DataFrame({
        'Producto': ['Total'],
        'Ventas Monetarias Septiembre': [ventas_monetarias_septiembre.sum()],
        'Ventas Monetarias Octubre': [ventas_monetarias_octubre.sum()],
        'Crecimiento Monetario': [crecimiento_monetario.sum()],
        'Crecimiento (%)': [(crecimiento_monetario.sum() / ventas_monetarias_septiembre.sum()) * 100]
    })

    utilidad_df = pd.concat([utilidad_df[utilidad_df['Producto'] != 'Total'].sort_values(by='Ventas Monetarias Octubre', ascending=False), total_fila], ignore_index=True)

    # Agrupar datos y calcular ventas en unidades para productos con 30% de descuento (productos_seleccionados_1)
    ventas_unidades_octubre_30 = datos_octubre_30.groupby('Código Homologado').agg({'Cantidad Vendida Actual': 'sum'})['Cantidad Vendida Actual']
    ventas_unidades_septiembre_30 = datos_septiembre_30.groupby('Código Homologado').agg({'Cantidad Vendida Actual': 'sum'})['Cantidad Vendida Actual']

    # Agrupar datos y calcular ventas en unidades para productos con 20% de descuento (productos_seleccionados_2)
    ventas_unidades_octubre_20 = datos_octubre_20.groupby('Código Homologado').agg({'Cantidad Vendida Actual': 'sum'})['Cantidad Vendida Actual']
    ventas_unidades_septiembre_20 = datos_septiembre_20.groupby('Código Homologado').agg({'Cantidad Vendida Actual': 'sum'})['Cantidad Vendida Actual']

    # Combinar las ventas en unidades de ambos conjuntos de productos para septiembre y octubre
    total_ventas_unidades_septiembre = ventas_unidades_septiembre_30.sum() + ventas_unidades_septiembre_20.sum()
    total_ventas_unidades_octubre = ventas_unidades_octubre_30.sum() + ventas_unidades_octubre_20.sum()

    # Calcular el crecimiento en unidades y su porcentaje
    crecimiento_bruto_unidades = total_ventas_unidades_octubre - total_ventas_unidades_septiembre
    crecimiento_bruto_porcentaje_unidades = ((total_ventas_unidades_octubre - total_ventas_unidades_septiembre) / total_ventas_unidades_septiembre) * 100

    # KPI: Crecimiento Real Monetario Total
    crecimiento_real_monetario_total = crecimiento_monetario.sum()

    # KPI: Total Discount in October
    total_descuento_octubre = ventas_30_octubre_bruto.sum() * 0.30 + ventas_20_octubre_bruto.sum() * 0.20

    # Interfaz en Streamlit
    st.title("Farmatodo HOT Sale")

    # Dividir en dos columnas para los KPIs
    col1, col2 = st.columns(2)

    # Columna 1: Primeros cuatro KPIs
    with col1:
        st.metric("Ventas Totales Periodo Anterior", f"{total_ventas_unidades_septiembre:,.0f}")
        st.metric("Ventas Totales Durante la Actividad", f"{total_ventas_unidades_octubre:,.0f}")
        st.metric("Crecimiento Bruto en Unidades", f"{crecimiento_bruto_unidades:,.0f}")
        st.metric("Crecimiento Bruto en Unidades (%)", f"{crecimiento_bruto_porcentaje_unidades:.2f}%")

    # Columna 2: KPIs adicionales
    with col2:
        st.metric("Total Descuento", f"${total_descuento_octubre:,.2f}")
        st.metric("Crecimiento Monetario Total", f"${crecimiento_real_monetario_total:,.2f}")
        
    # Mostrar tabla de utilidad
    st.subheader("Análisis de Utilidad por Producto")
    st.dataframe(utilidad_df)

    # Graficar comparativo de ventas monetarias
    st.subheader("Comparativo de Ventas Monetarias")
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
