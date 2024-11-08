import streamlit as st # type: ignore
import pandas as pd # type: ignore
import plotly.graph_objs as go # type: ignore

# Definir la función para cargar los datos desde Excel, con cache
@st.cache_data
def cargar_datos():
    try:
        # Ruta al archivo Excel (cambiar a la ruta del archivo cargado por el usuario si es necesario)
        file_path = 'data/PAC_Oct.xlsx'  # Reemplaza con la ruta adecuada si necesitas el archivo exacto
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
    banners_seleccionados = ["Carulla", "Carulla Express", "Éxito", "Éxito Express"]
    productos_seleccionados = ["8PCN0", "12P0"]

    # Fechas específicas para el periodo de actividad comercial (octubre y noviembre) y periodo anterior (agosto y septiembre)
    fechas_actividad_comercial = pd.to_datetime([
        '2024-10-04', '2024-10-05', '2024-10-06', 
        '2024-10-11', '2024-10-12', '2024-10-13', 
        '2024-10-18', '2024-10-19', '2024-10-20', 
        '2024-10-25', '2024-10-26', '2024-10-27', 
        '2024-11-01', '2024-11-02', '2024-11-03'
    ])
    fechas_periodo_anterior = pd.to_datetime([
        '2024-08-30', '2024-08-31', '2024-09-01', 
        '2024-09-06', '2024-09-07', '2024-09-08', 
        '2024-09-13', '2024-09-14', '2024-09-15', 
        '2024-09-20', '2024-09-21', '2024-09-22', 
        '2024-09-27', '2024-09-28', '2024-09-29'
    ])

    # Función para filtrar datos por fechas específicas
    def filtrar_datos(df, fechas, banners, productos):
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df_filtrado = df[df['Date'].isin(fechas)]
        df_filtrado = df_filtrado[df_filtrado['Banner'].isin(banners) & df_filtrado['Código Homologado'].isin(productos)]
        return df_filtrado

    # Filtrar datos para actividad comercial y periodo anterior usando las fechas específicas
    datos_actividad_comercial = filtrar_datos(df, fechas_actividad_comercial, banners_seleccionados, productos_seleccionados)
    datos_periodo_anterior = filtrar_datos(df, fechas_periodo_anterior, banners_seleccionados, productos_seleccionados)

    # Asegurar que las columnas numéricas estén correctas
    for col in ['Cantidad Vendida Actual', 'Precio']:
        datos_actividad_comercial[col] = pd.to_numeric(datos_actividad_comercial[col], errors='coerce').fillna(0)
        datos_periodo_anterior[col] = pd.to_numeric(datos_periodo_anterior[col], errors='coerce').fillna(0)

    # Agrupar datos y calcular métricas
    ventas_agrupadas_actividad_comercial = datos_actividad_comercial.groupby('Código Homologado').agg({'Cantidad Vendida Actual': 'sum'})['Cantidad Vendida Actual']
    ventas_agrupadas_periodo_anterior = datos_periodo_anterior.groupby('Código Homologado').agg({'Cantidad Vendida Actual': 'sum'})['Cantidad Vendida Actual']

    # Calcular las ventas monetarias para la actividad comercial y el periodo anterior
    ventas_monetarias_actividad_bruto = (datos_actividad_comercial['Cantidad Vendida Actual'] * datos_actividad_comercial['Precio']).groupby(datos_actividad_comercial['Código Homologado']).sum()
    ventas_monetarias_actividad = ventas_monetarias_actividad_bruto * 0.80  # Aplicar el 20% de descuento
    ventas_monetarias_periodo_anterior = (datos_periodo_anterior['Cantidad Vendida Actual'] * datos_periodo_anterior['Precio']).groupby(datos_periodo_anterior['Código Homologado']).sum()

    # Asegurarse de que todos los productos estén presentes en el índice
    ventas_monetarias_actividad = ventas_monetarias_actividad.reindex(productos_seleccionados, fill_value=0)
    ventas_monetarias_periodo_anterior = ventas_monetarias_periodo_anterior.reindex(productos_seleccionados, fill_value=0)

    # Calcular el crecimiento monetario
    crecimiento_monetario = ventas_monetarias_actividad - ventas_monetarias_periodo_anterior
    crecimiento_porcentaje = (crecimiento_monetario / ventas_monetarias_periodo_anterior.replace(0, pd.NA)) * 100

    # Crear DataFrame de utilidad
    utilidad_df = pd.DataFrame({
        'Producto': ventas_monetarias_actividad.index,
        'Ventas Monetarias Periodo Anterior': ventas_monetarias_periodo_anterior.values,
        'Ventas Monetarias Actividad Comercial': ventas_monetarias_actividad.values,
        'Crecimiento Monetario': crecimiento_monetario.values,
        'Crecimiento (%)': crecimiento_porcentaje.values
    }).reset_index(drop=True)

    # Fila total
    total_fila = pd.DataFrame({
        'Producto': ['Total'],
        'Ventas Monetarias Periodo Anterior': [ventas_monetarias_periodo_anterior.sum()],
        'Ventas Monetarias Actividad Comercial': [ventas_monetarias_actividad.sum()],
        'Crecimiento Monetario': [crecimiento_monetario.sum()],
        'Crecimiento (%)': [(crecimiento_monetario.sum() / ventas_monetarias_periodo_anterior.sum()) * 100]
    })

    utilidad_df = pd.concat([utilidad_df[utilidad_df['Producto'] != 'Total'].sort_values(by='Ventas Monetarias Actividad Comercial', ascending=False), total_fila], ignore_index=True)

    # Calcular el total de ventas en unidades y el crecimiento
    total_ventas_unidades_periodo_anterior = ventas_agrupadas_periodo_anterior.sum()
    total_ventas_unidades_actividad_comercial = ventas_agrupadas_actividad_comercial.sum()
    crecimiento_bruto_unidades = total_ventas_unidades_actividad_comercial - total_ventas_unidades_periodo_anterior
    crecimiento_bruto_porcentaje_unidades = ((total_ventas_unidades_actividad_comercial - total_ventas_unidades_periodo_anterior) / total_ventas_unidades_periodo_anterior) * 100

    # KPI: Crecimiento Real Monetario Total
    crecimiento_real_monetario_total = crecimiento_monetario.sum()  # Total Real Monetary Growth

    # KPI: Total Discount in October
    total_descuento_octubre = ventas_monetarias_actividad_bruto.sum() * 0.20  # Total discount in October (20% discount)

    # Interfaz en Streamlit
    st.title("20% OFF Éxito, Carulla, Éxito express, Carulla express")

    # Dividir en dos columnas para los KPIs
    col1, col2 = st.columns(2)

    # Columna 1: Primeros cuatro KPIs
    with col1:
        st.metric("Ventas Totales Periodo Anterior (Unidades)", f"{total_ventas_unidades_periodo_anterior:,.0f}")
        st.metric("Ventas Totales Actividad Comercial (Unidades)", f"{total_ventas_unidades_actividad_comercial:,.0f}")
        st.metric("Crecimiento Bruto en Unidades", f"{crecimiento_bruto_unidades:,.0f}")
        st.metric("Crecimiento Bruto en Unidades (%)", f"{crecimiento_bruto_porcentaje_unidades:.2f}%")

    # Columna 2: KPIs adicionales
    with col2:
        st.metric("Total Descuento Actividad Comercial", f"${total_descuento_octubre:,.0f}")
        st.metric("Crecimiento Real Monetario Total", f"${crecimiento_real_monetario_total:,.0f}")
        
    # Mostrar tabla de utilidad
    st.subheader("Análisis de Utilidad por Producto")
    st.dataframe(utilidad_df)

    # Graficar comparativo de ventas monetarias
    st.subheader("Comparativo de Ventas Monetarias (Actividad Comercial vs Periodo Anterior)")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=utilidad_df[utilidad_df['Producto'] != 'Total']['Producto'],
        x=utilidad_df[utilidad_df['Producto'] != 'Total']['Ventas Monetarias Actividad Comercial'],
        name='Actividad Comercial',
        orientation='h'
    ))
    fig.add_trace(go.Bar(
        y=utilidad_df[utilidad_df['Producto'] != 'Total']['Producto'],
        x=utilidad_df[utilidad_df['Producto'] != 'Total']['Ventas Monetarias Periodo Anterior'],
        name='Periodo Anterior',
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
