import streamlit as st
import requests
import pandas as pd

# --- CONFIGURACIÓN DE LA PÁGINA WEB ---
st.set_page_config(page_title="Libro de Órdenes P2P", layout="wide")

st.title("📋 Top 10 Órdenes de Compra - Binance P2P")
st.write("Datos en tiempo real obtenidos a través de un servidor espejo en la nube.")

# Botón para refrescar la tabla cuando quieras
if st.button("🔄 Actualizar Tabla"):
    st.rerun()

st.markdown("---")

# --- CONEXIÓN AL SERVIDOR ESPEJO EN LA NUBE ---
url_espejo = "https://p2p-api.bavm.com.ar/v1/p2p/binance/fiat/VES/asset/USDT/trade/BUY"

try:
    # Hacemos la consulta al servidor alternativo
    response = requests.get(url_espejo, timeout=12)
    
    if response.status_code == 200:
        data = response.json()
        lista_ordenes = []
        
        # Procesamos exactamente las primeras 10 órdenes del libro
        for id_anuncio, anuncio in enumerate(data[:10], start=1):
            lista_ordenes.append({
                "N°": id_anuncio,
                "Comerciante": anuncio.get("username", "Anónimo"),
                "Precio (VES)": f"{float(anuncio.get('price', 0)):.2f}",
                "Disponible (USDT)": f"{float(anuncio.get('max_amount', 0)):.2f}",
                "Min (VES)": f"{float(anuncio.get('min_limit', 0)):.2f}",
                "Max (VES)": f"{float(anuncio.get('max_limit', 0)):.2f}",
                "Bancos / Métodos": ", ".join(anuncio.get("payments", ["Transferencia"]))
            })
        
        # Convertimos los datos en una tabla interactiva de Pandas
        tabla = pd.DataFrame(lista_ordenes)
        tabla.set_index("N°", inplace=True)
        
        # Mostramos la tabla en la pantalla de Streamlit
        st.dataframe(tabla, use_container_width=True)
        
    else:
        st.error(f"El servidor de respaldo respondió con un error técnico (Código: {response.status_code})")

except Exception as e:
    st.error("Hubo un problema temporal al conectar con la base de datos de respaldo.")
    st.caption(f"Detalle del error: {str(e)}")
