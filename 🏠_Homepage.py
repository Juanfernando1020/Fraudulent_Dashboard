import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# Import your backend data loading and processing function
from Backend.Logic import load_and_process_data

# --- Configuration ---
st.set_page_config(
    page_title="Dashboard de Transacciones Reales",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load Data (using backend) ---
# Use st.cache_data to cache the processed DataFrame
@st.cache_data
def get_data():
    # Make sure 'transactions.csv' is in the same directory as app.py
    # or provide the correct path to your dataset.
    return load_and_process_data(file_path="transactions.csv")

df = get_data()

# Check if data loaded correctly
if df.empty:
    st.error("No se pudieron cargar los datos. Por favor, asegúrese de que 'transactions.csv' existe y es accesible.")
    st.stop() # Stop the app if data is not loaded

# --- Sidebar - Filters ---
st.sidebar.header("Filtros de Transacciones")

# Filtro por fecha (using the 'fecha' column from your data)
min_date = df["fecha"].min().date()
max_date = df["fecha"].max().date()
date_range = st.sidebar.date_input(
    "Rango de fechas",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Filtro por monto (using the 'monto' column from your data)
amount_range = st.sidebar.slider(
    "Rango de montos (USD)",
    float(df["monto"].min()),
    float(df["monto"].max()),
    (float(df["monto"].min()), float(df["monto"].max()))
)

# Filtro por método de pago (using 'metodo_pago' from your data)
payment_methods = st.sidebar.multiselect(
    "Método de pago",
    options=df["metodo_pago"].unique(),
    default=df["metodo_pago"].unique()
)

# Filtro por categoría de producto (new filter from your dataset)
product_categories = st.sidebar.multiselect(
    "Categoría de Producto",
    options=df["categoria_producto"].unique(),
    default=df["categoria_producto"].unique()
)

# Filtro por estado (using the new 'estado' column)
status_filter = st.sidebar.radio(
    "Estado de transacción",
    options=["Todas", "Válida", "Fraudulenta"],
    index=0
)

# --- Apply Filters ---
filtered_df = df[
    (df["fecha"].dt.date >= date_range[0]) &
    (df["fecha"].dt.date <= date_range[1]) &
    (df["monto"] >= amount_range[0]) &
    (df["monto"] <= amount_range[1]) &
    (df["metodo_pago"].isin(payment_methods)) &
    (df["categoria_producto"].isin(product_categories)) # Apply new filter
]

if status_filter != "Todas":
    filtered_df = filtered_df[filtered_df["estado"] == status_filter]

# --- Main Header ---
st.title("📊 Dashboard de Análisis de Transacciones Reales")
st.markdown("---")

# --- Key Metrics ---
# Ensure there are transactions after filtering to avoid division by zero
if len(filtered_df) == 0:
    st.warning("No hay transacciones que coincidan con los filtros seleccionados.")
    st.stop() # Stop further execution if no data

col1, col2, col3, col4 = st.columns(4) # Added a column for new metric
with col1:
    st.metric("Total Transacciones", len(filtered_df))
with col2:
    fraud_count = len(filtered_df[filtered_df["es_fraudulenta"] == 1]) # Use 'es_fraudulenta'
    fraud_percentage = f"{fraud_count / len(filtered_df) * 100:.2f}%" if len(filtered_df) > 0 else "0%"
    st.metric("Transacciones Fraudulentas", f"{fraud_count} ({fraud_percentage})")
with col3:
    avg_amount = f"${filtered_df['monto'].mean():.2f}" if len(filtered_df) > 0 else "$0.00"
    st.metric("Monto Promedio", avg_amount)
with col4: # New metric: Average Customer Age
    avg_age = f"{filtered_df['edad_cliente'].mean():.1f} años" if len(filtered_df) > 0 else "N/A"
    st.metric("Edad Promedio Cliente", avg_age)

st.markdown("---")

# --- Charts ---
# Added a new tab for "Análisis por Categoría"
tab1, tab2, tab3, tab4 = st.tabs(["Distribución por Monto", "Mapa de Transacciones", "Análisis por Categoría", "Datos Detallados"])

with tab1:
    fig1 = px.histogram(
        filtered_df,
        x="monto",
        color="estado",
        nbins=20,
        title="Distribución de Transacciones por Monto",
        color_discrete_map={"Válida": "#2ecc71", "Fraudulenta": "#e74c3c"},
        barmode="overlay"
    )
    fig1.update_layout(
        hovermode="x unified",
        xaxis_title="Monto (USD)",
        yaxis_title="Cantidad de Transacciones"
    )
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    # Approximate coordinates for the cities in your dataset
    # You might need to refine these for better accuracy
    city_coords = {
        "New York": (40.7128, -74.0060),
        "Los Angeles": (34.0522, -118.2437),
        "Chicago": (41.8781, -87.6298),
        "Houston": (29.7604, -95.3698),
        "Miami": (25.7617, -80.1918),
        "London": (51.5074, -0.1278),
        "Paris": (48.8566, 2.3522),
        "Tokyo": (35.6895, 139.6917),
        "Sydney": (-33.8688, 151.2093),
        "Berlin": (52.5200, 13.4050),
        "Toronto": (43.6532, -79.3832),
        "Dubai": (25.276987, 55.296249),
        "Singapore": (1.3521, 103.8198),
        "Mexico City": (19.4326, -99.1332),
        "Rio de Janeiro": (-22.9068, -43.1729),
        "Johannesburg": (-26.2041, 28.0473),
        "Cairo": (30.0444, 31.2357),
        "Mumbai": (19.0760, 72.8777),
        "Beijing": (39.9042, 116.4074),
        "Moscow": (55.7558, 37.6173)
    }

    # Filter out locations not in our city_coords map for the map plot
    filtered_df_map = filtered_df[filtered_df['ubicacion'].isin(city_coords.keys())].copy()

    if not filtered_df_map.empty:
        location_counts = filtered_df_map.groupby(["ubicacion", "estado"]).size().unstack(fill_value=0)
        location_counts["total"] = location_counts.sum(axis=1)
        location_counts = location_counts.reset_index()
        location_counts["lat"] = location_counts["ubicacion"].map(lambda x: city_coords.get(x, (np.nan, np.nan))[0])
        location_counts["lon"] = location_counts["ubicacion"].map(lambda x: city_coords.get(x, (np.nan, np.nan))[1])

        # Drop rows where coordinates could not be mapped
        location_counts.dropna(subset=['lat', 'lon'], inplace=True)

        if not location_counts.empty:
            fig2 = px.scatter_mapbox(
                location_counts,
                lat="lat",
                lon="lon",
                size="total",
                color="Fraudulenta" if "Fraudulenta" in location_counts.columns else "total",
                hover_name="ubicacion",
                hover_data={"Válida": True, "Fraudulenta": True, "total": True} if "Fraudulenta" in location_counts.columns else {"total": True},
                size_max=30,
                zoom=1, # Adjust zoom level to see global cities
                title="Mapa de Transacciones por Ubicación",
                mapbox_style="open-street-map"
            )
            fig2.update_layout(
                margin={"r":0,"t":0,"l":0,"b":0},
                mapbox_accesstoken=st.secrets["mapbox_token"] if "mapbox_token" in st.secrets else None # Use Mapbox token if available
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("No hay datos de ubicación válidos para mostrar en el mapa con los filtros seleccionados.")
    else:
        st.warning("No hay datos de ubicación para mostrar en el mapa con los filtros seleccionados.")

with tab3:
    # --- ORIGINAL CODE (CAUSES ERROR) ---
    # category_fraud_counts = filtered_df.groupby(["categoria_producto", "estado"]).size().unstack(fill_value=0)
    # category_fraud_counts = category_fraud_counts.reset_index()
    # fig3 = px.bar(
    #     category_fraud_counts,
    #     x="categoria_producto",
    #     y=["Válida", "Fraudulenta"], # Problematic 'y' argument when no 'Fraudulenta' or 'Válida' column exists
    #     title="Transacciones por Categoría de Producto y Estado",
    #     labels={"value": "Cantidad de Transacciones", "categoria_producto": "Categoría de Producto"},
    #     color_discrete_map={"Válida": "#2ecc71", "Fraudulenta": "#e74c3c"},
    #     barmode="group"
    # )

    # --- CORRECTED CODE FOR fig3 ---
    # Create the counts for each category and state
    category_counts = filtered_df.groupby(["categoria_producto", "estado"]).size().reset_index(name='count')

    # Ensure both 'Válida' and 'Fraudulenta' are present in the 'estado' column of category_counts
    # This is to handle cases where one of the states might be filtered out
    # For instance, if only 'Válida' transactions are present, 'Fraudulenta' column won't exist after unstack.
    # It's safer to plot directly from the long format or ensure all categories are present.

    # Option 1: Using `px.bar` directly on the long format `category_counts`
    # This is often more flexible and less prone to issues with missing columns.
    fig3 = px.bar(
        category_counts,
        x="categoria_producto",
        y="count",
        color="estado", # Use 'estado' column to differentiate colors
        title="Transacciones por Categoría de Producto y Estado",
        labels={"count": "Cantidad de Transacciones", "categoria_producto": "Categoría de Producto"},
        color_discrete_map={"Válida": "#2ecc71", "Fraudulenta": "#e74c3c"},
        barmode="group" # This creates grouped bars for each category
    )

    # Option 2 (Less preferred for this exact scenario, but shows another way to handle data):
    # If you specifically wanted to plot "Válida" and "Fraudulenta" as separate bars from wide format:
    # category_fraud_counts_wide = filtered_df.groupby("categoria_producto")["estado"].value_counts().unstack(fill_value=0)
    #
    # # Handle case where a column might be missing if no such transactions exist after filter
    # if 'Válida' not in category_fraud_counts_wide.columns:
    #     category_fraud_counts_wide['Válida'] = 0
    # if 'Fraudulenta' not in category_fraud_counts_wide.columns:
    #     category_fraud_counts_wide['Fraudulenta'] = 0
    #
    # category_fraud_counts_wide = category_fraud_counts_wide.reset_index()
    #
    # fig3 = px.bar(
    #     category_fraud_counts_wide,
    #     x="categoria_producto",
    #     y=["Válida", "Fraudulenta"], # This now works because the columns 'Válida' and 'Fraudulenta' are guaranteed to exist
    #     title="Transacciones por Categoría de Producto y Estado",
    #     labels={"value": "Cantidad de Transacciones", "categoria_producto": "Categoría de Producto"},
    #     color_discrete_map={"Válida": "#2ecc71", "Fraudulenta": "#e74c3c"},
    #     barmode="group"
    # )

    fig3.update_layout(xaxis_title="Categoría de Producto", yaxis_title="Cantidad de Transacciones")
    st.plotly_chart(fig3, use_container_width=True)

with tab4:
    st.dataframe(
        filtered_df[[
            "transaction_id", "fecha", "monto", "metodo_pago", "ubicacion",
            "categoria_producto", "cantidad", "edad_cliente", "dispositivo_usado",
            "es_fraudulenta", "estado"
        ]].rename(columns={
            "transaction_id": "ID Transacción",
            "fecha": "Fecha/Hora",
            "monto": "Monto (USD)",
            "metodo_pago": "Método de Pago",
            "ubicacion": "Ubicación Cliente",
            "categoria_producto": "Categoría Producto",
            "cantidad": "Cantidad",
            "edad_cliente": "Edad Cliente",
            "dispositivo_usado": "Dispositivo",
            "es_fraudulenta": "Es Fraudulenta (0/1)",
            "estado": "Estado"
        }),
        hide_index=True,
        use_container_width=True
    )

# --- Additional Notes ---
st.sidebar.markdown("---")
st.sidebar.markdown("**Notas:**")
st.sidebar.markdown("- Los datos se cargan desde tu archivo `transactions.csv`.")
st.sidebar.markdown("- Utiliza los filtros para explorar los datos en detalle.")
st.sidebar.markdown("- El mapa requiere coordenadas precisas para cada ubicación en tu dataset. Las coordenadas actuales son aproximadas.")
st.sidebar.markdown("- **Para el mapa de ubicaciones**: Si tienes una cuenta de Mapbox, puedes configurar tu `mapbox_token` en un archivo `.streamlit/secrets.toml` para un mejor renderizado del mapa.")