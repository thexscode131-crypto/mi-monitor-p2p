import streamlit as st
import requests
import urllib3
import pandas as pd
import json

# Desactivamos alertas visuales de certificados de internet
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def obtener_top_10_ordenes():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    
    # Payload: los datos requeridos por la base de datos de Binance
    payload = {
        "asset": "USDT", 
        "fiat": "VES", 
        "merchantCheck": False,
        "page": 1, 
        "payTypes": [], 
        "publisherType": None,
        "rows": 10, 
        "tradeType": "BUY"
    }
    
    # El Disfraz (Headers): Le hacemos creer a Binance que somos un navegador real
    headers = {
        "Accept": "*/*",
        "Accept-Language": "es-ES,es;q=0.9",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://p2p.binance.com",
        "Referer": "https://p2p.binance.com/es/trade/sell/USDT?fiat=VES"
    }
    
    try:
        # Enviamos la petición usando json=payload y sumándole las cabeceras (headers)
        response = requests.post(url, json=payload, headers=headers, timeout=12, verify=False)
        data = response.json()
        
        lista_ordenes = []
        
        if data.get("success") and data.get("data"):
            for id_anuncio, anuncio in enumerate(data["data"], start=1):
                comerciante = anuncio["advertiser"]["nickName"]
                precio = float(anuncio["adv"]["price"])
                cantidad_disponible = float(anuncio["adv"]["surplusAmount"])
                limite_minimo = float(anuncio["adv"]["minSingleTransAmount"])
                limite_maximo = float(anuncio["adv"]["maxSingleTransAmount"])
                
                # Métodos de pago aceptados por ese comprador
                metodos_pago = ", ".join([p["name"] for p in anuncio["adv"]["tradeMethods"]])
                
                lista_ordenes.append({
                    "N°": id_anuncio,
                    "Comerciante": comerciante,
                    "Precio (VES)": f"{precio:.2f}",
                    "Disponible (USDT)": f"{cantidad_disponible:.2f}",
                    "Min (VES)": f"{limite_minimo:.2f}",
                    "Max (VES)": f"{limite_maximo:.2f}",
                    "Bancos / Métodos": metodos_pago
                })
            return lista_ordenes
        return None
    except Exception as e:
        # Si ocurre un error, nos lo dirá discretamente aquí abajo
        print(f"Error técnico de conexión: {e}")
        return None

# --- INTERFAZ VISUAL ---
st.set_page_config(page_title="Libro de Órdenes Binance", layout="wide")

st.title("📋 Top 10 Órdenes de Compra en Binance P2P")
st.write("Datos extraídos directamente del mercado en vivo en este instante.")

if st.button("🔄 Actualizar Tabla"):
    st.rerun()

st.markdown("---")

# Buscamos la lista
datos_ordenes = obtener_top_10_ordenes()

if datos_ordenes:
    # Creamos la tabla
    tabla = pd.DataFrame(datos_ordenes)
    # Configuramos el número de orden (N°) como la columna de índice
    tabla.set_index("N°", inplace=True)
    
    # Pintamos la tabla interactiva
    st.dataframe(tabla, use_container_width=True)
else:
    st.error("⚠️ Binance rechazó la conexión.")
    st.info("💡 Solución rápida: Espera 5 segundos y presiona el botón 'Actualizar Tabla' de arriba. A veces Binance limita las consultas muy seguidas.")