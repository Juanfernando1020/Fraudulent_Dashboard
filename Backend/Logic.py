import pandas as pd
import numpy as np

def load_and_process_data(file_path="transactions.csv"):
    """
    Loads the transaction data from a CSV file and performs initial processing.

    Args:
        file_path (str): The path to your CSV dataset.

    Returns:
        pd.DataFrame: The processed DataFrame.
    """
    try:
        df = pd.read_csv('C:/Users/Juan Fer/Desktop/ProyectoAnaliticaStreamLit/Fraudulent_E-Commerce_Transaction_Data.csv')
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found. Please ensure it's in the correct directory.")
        return pd.DataFrame() # Return empty DataFrame on error

    # --- Data Cleaning and Type Conversion ---

    # Rename columns for easier use and consistency with original dashboard idea
    df = df.rename(columns={
        "Transaction ID": "transaction_id",
        "Customer ID": "customer_id",
        "Transaction Amount": "monto",
        "Transaction Date": "fecha",
        "Payment Method": "metodo_pago",
        "Product Category": "categoria_producto",
        "Quantity": "cantidad",
        "Customer Age": "edad_cliente",
        "Customer Location": "ubicacion",
        "Device Used": "dispositivo_usado",
        "IP Address": "ip_address",
        "Shipping Address": "direccion_envio",
        "Billing Address": "direccion_facturacion",
        "Is Fraudulent": "es_fraudulenta", # This is your new fraud flag
        "Account Age Days": "antiguedad_cuenta_dias",
        "Transaction Hour": "hora_transaccion"
    })

    # Convert 'fecha' to datetime objects
    # Assuming 'Transaction Date' is in a format like 'YYYY-MM-DD' or similar
    df['fecha'] = pd.to_datetime(df['fecha'])

    # Create a 'estado' column based on 'es_fraudulenta' for consistent filtering
    df['estado'] = df['es_fraudulenta'].apply(lambda x: "Fraudulenta" if x == 1 else "Válida")

    # Ensure 'monto' is numeric (it's already float64, but good practice)
    df['monto'] = pd.to_numeric(df['monto'])

    # Handle potential missing values (example: fill with a default or drop)
    # For now, let's assume no critical NaNs for these columns, but you can add:
    # df.dropna(subset=['monto', 'fecha', 'metodo_pago', 'ubicacion'], inplace=True)

    print("Data loaded and processed successfully!")
    print(f"Total transactions: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")

    return df

if __name__ == "__main__":
    # This block is for testing your backend logic independently
    # Replace 'transactions.csv' with the actual name of your dataset file
    df_processed = load_and_process_data('transactions.csv')
    if not df_processed.empty:
        print("\nSample of processed data:")
        print(df_processed.head())
        print("\nData types:")
        print(df_processed.info())