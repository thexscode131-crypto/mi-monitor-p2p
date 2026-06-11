import streamlit as st
import pandas as pd
import ccxt
import json

# --- CONFIGURACIÓN DE LA PÁGINA WEB ---
st.set_page_config(page_title="Libro de Órdenes P2P", layout="wide")

st.title("📋 Top 10 Órdenes de Compra - Binance P2P Oficial")
st.write("Datos extraídos directamente de Binance usando la infraestructura profesional de CCXT.")

if st.button("🔄 Actualizar Tabla"):
    st.rerun()

st.markdown("---")

try:
    # Inicializamos la conexión oficial a Binance usando CCXT
    exchange = ccxt.binance()
    
    # Parámetros para el P2P de Binance
    payload = {
        "asset": "USDT",
        "fiat": "VES",
        "merchantCheck": False,
        "page": 1,
        "rows": 10,
        "tradeType": "BUY"
    }
    
    # SOLUCIÓN AL ERROR: Convertimos el diccionario en un texto JSON plano
    json_body = json.dumps(payload)
    
    # Hacemos la llamada directa usando el cuerpo ya formateado como texto
    p2p_data = exchange.request(
        path='c2c/adv/search',
        api='public',
        method='POST',
        params={},
        headers={
            'Content-Type': 'application/json'
        },
        body=json_body  # <--- Aquí pasamos el JSON corregido
    )
    
    # Verificamos que Binance haya respondido con datos exitosos
    if p2p_data.get("success") and p2p_data.get("data"):
        lista_ordenes = []
        
        for id_anuncio, anuncio in enumerate(p2p_data["data"], start=1):
            comerciante = anuncio.get("advertiser", {}).get("nickName", "Anónimo")
            precio = float(anuncio.get("adv", {}).get("price", 0))
            cantidad_disponible = float(anuncio.get("adv", {}).get("surplusAmount", 0))
            limite_minimo = float(anuncio.get("adv", {}).get("minSingleTransAmount", 0))
            limite_maximo = float(anuncio.get("adv", {}).get("maxSingleTransAmount", 0))
            
            # Extraemos los métodos de pago aceptados
            metodos = [p.get("name", "Otros") for p in anuncio.get("adv", {}).get("tradeMethods", [])]
            metodos_pago = ", ".join(metodos) if metodos else "Transferencia"
            
            lista_ordenes.append({
                "N°": id_anuncio,
                "Comerciante": comerciante,
                "Precio (VES)": f"{precio:.2f}",
                "Disponible (USDT)": f"{cantidad_disponible:.2f}",
                "Min (VES)": f"{limite_minimo:.2f}",
                "Max (VES)": f"{limite_maximo:.2f}",
                "Bancos / Métodos": metodos_pago
            })
            
        # Armamos la tabla interactiva
        tabla = pd.DataFrame(lista_ordenes)
        tabla.set_index("N°", inplace=True)
        st.dataframe(tabla, use_container_width=True)
        
    else:
        st.error("Binance recibió la consulta pero no devolvió anuncios activos en este momento.")

except Exception as e:
    st.error("Error al conectar con la API oficial de Binance a través de CCXT.")
    st.caption(f"Detalle técnico del fallo: {str(e)}")
