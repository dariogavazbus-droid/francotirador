import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# 1. CONFIGURACIÓN WIDE (Optimizado para Celular y PC)
st.set_page_config(page_title="Francotirador v3.6 Pro", layout="wide")

# Estilos profesionales y corrección para evitar traducciones raras
st.markdown("""
    <style>
    .reportview-container { background: #0e1117; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2e7d32; color: white; font-weight: bold; }
    .status-box { padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #30363d; background-color: #161b22; }
    .notranslate { translate: no; }
    /* Estilo para el botón de Gemini */
    .stLinkButton>a { background-color: #1a73e8 !important; color: white !important; border-radius: 5px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏹 Francotirador v3.6 Pro")
st.write("Panel con Gráficos en Vivo + Consultoría Gemini")

# --- Configuración de Capital ---
with st.expander("💰 Configuración de Capital"):
    cap_total = st.number_input("Capital Total ($)", value=900000)
    riesgo_per = st.slider("Riesgo por trade (%)", 0.5, 5.0, 2.0) / 100

activos = {
    "LOMA": "LOMA.BA", "GGAL": "GGAL.BA", "PAMP": "PAMP.BA",
    "YPFD": "YPFD.BA", "VIST": "VIST.BA", "KO": "KO",
    "AAPL": "AAPL", "MSFT": "MSFT", "NVDA": "NVDA",
    "MELI": "MELI.BA", "JNJ": "JNJ", "COME": "COME.BA", "SAMI": "SAMI.BA"
}

if st.button('🚀 ANALIZAR MERCADO'):
    resultados = []
    barra = st.progress(0)

    for i, (nombre, ticker) in enumerate(activos.items()):
        try:
            df = yf.download(ticker, period="1y",
                             interval="1d", progress=False)
            if df.empty:
                continue
            df.columns = [c[0].lower() if isinstance(
                c, tuple) else c.lower() for c in df.columns]

            df['rsi'] = ta.rsi(df['close'], length=14)
            resistencia = df['high'].iloc[-41:-1].max()
            soporte = df['low'].iloc[-41:-1].min()
            precio = float(df['close'].iloc[-1])
            rsi_actual = float(df['rsi'].iloc[-1])
            vol_actual = float(df['volume'].iloc[-1])
            vol_media = float(df['volume'].rolling(20).mean().iloc[-1])
            ratio_vol = (vol_actual / vol_media)

            d_piso = ((precio - soporte) / soporte) * 100
            d_techo = ((resistencia - precio) / precio) * 100

            es_rebote = d_piso < 1.5 and rsi_actual < 45 and ratio_vol > 0.9
            es_ruptura = (d_techo < 1.0 or precio >
                          resistencia) and rsi_actual < 68 and ratio_vol > 1.1

            status = "💤 Neutro"
            color = "#ffffff"
            compra, target, stop, uni = "-", "-", "-", "-"

            if es_rebote or es_ruptura:
                status = "💥 ¡DISPARE!"
                color = "#00c853"
                compra = round(precio, 2)
                stop = round(soporte * 0.98,
                             2) if es_rebote else round(resistencia * 0.97, 2)
                distancia = abs(compra - stop)
                uni = int((cap_total * riesgo_per) /
                          distancia) if distancia > 0 else 0
            elif rsi_actual > 70:
                status = "🥵 CARO"
                color = "#d32f2f"
            elif d_techo < 2.5 or d_piso < 2.5 or ratio_vol > 1.5:
                status = "⚠️ OJO / VOL"
                color = "#fbc02d"

            resultados.append({
                "ACTIVO": nombre, "PISO %": f"{d_piso:.1f}%", "RSI": round(rsi_actual, 1),
                "ACCIÓN": status, "COMPRA": compra, "STOP": stop, "UNI": uni, "hex": color
            })
        except:
            pass
        barra.progress((i + 1) / len(activos))

    # --- Renderizado de Tarjetas con Gráficos y Gemini ---
    cols = st.columns(3)
    for index, r in enumerate(resultados):
        with cols[index % 3]:
            # El Expander permite que la App sea compacta en el celu
            with st.expander(f"{r['ACTIVO']} | {r['ACCIÓN']}"):
                st.markdown(f"""
                    <div class="status-box notranslate" style="border-left: 8px solid {r['hex']};">
                        <div style="font-size: 0.95em; color: #b0b0b0;">
                            Piso: <b>{r['PISO %']}</b> | RSI: <b>{r['RSI']}</b>
                        </div>
                        {f'<div style="margin-top: 8px; color: #00c853;"><b>IN: {r["COMPRA"]} | SL: {r["STOP"]} | Unidades: {r["UNI"]}</b></div>' if r['COMPRA'] != '-' else ''}
                    </div>
                    """, unsafe_allow_html=True)

                # 1. GRÁFICO REAL-TIME (TradingView)
                # Mapeo simple de tickers para el Widget
                tv_map = {"MELI": "MELI", "GGAL": "BCBA:GGAL", "LOMA": "BCBA:LOMA",
                          "YPFD": "BCBA:YPFD", "PAMP": "BCBA:PAMP", "VIST": "NYSE:VIST"}
                symbol = tv_map.get(r['ACTIVO'], r['ACTIVO'])

                chart_html = f"""
                <div style="height:250px;">
                    <iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview_76d87&symbol={symbol}&interval=D&hidesidetoolbar=1&symboledit=0&saveimage=1&toolbarbg=f1f3f6&studies=[]&theme=dark&style=1&timezone=America%2FArgentina%2FBuenos_Aires" 
                            width="100%" height="250" frameborder="0" allowtransparency="true" scrolling="no" allowfullscreen></iframe>
                </div>
                """
                st.components.v1.html(chart_html, height=260)

                # 2. BOTÓN DE CONSULTA Atu amigo GEMINI
                prompt = f"Analizá el activo {r['ACTIVO']}. El precio es {r['COMPRA']}, el RSI está en {r['RSI']} y la distancia al piso es {r['PISO %']}. ¿Qué opinas de una entrada ahora?"
                url_gemini = f"https://gemini.google.com/app?prompt={prompt.replace(' ', '%20')}"
                st.link_button("🤖 Consultar a Gemini", url_gemini)

st.caption("v3.6 Pro - Gráficos + IA - San Juan")
