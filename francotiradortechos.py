import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ──────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE DARÍO (v2.8 - Breakout & Volume Sensor)
# ──────────────────────────────────────────────────────────────
MI_PORTFOLIO = {"capital_total": 400000, "riesgo_max_por_operacion": 0.02}

# Lista ampliada para detectar rupturas explosivas
ACTIVOS = {
    "LOMA": "LOMA.BA", "GGAL": "GGAL.BA", "PAMP": "PAMP.BA",
    "YPFD": "YPFD.BA", "VIST": "VIST.BA", "KO": "KO",
    "AAPL": "AAPL", "MSFT": "MSFT", "SPY": "SPY",
    "NVDA": "NVDA", "MELI": "MELI", "TSLA": "TSLA", "META": "META"
}

CONFIG = {
    "comision_total": 0.013,
    "objetivo_breakout": 0.08,    # Buscamos un 8% de subida
    "stop_loss_breakout": 0.03,   # Salida si falla la ruptura
    "ventana_resistencia": 40,
    "filtro_volumen": 1.10        # 10% más de volumen para confirmar compra
}

RADAR_TECHO = []


def analizar_breakout(nombre, ticker):
    print(f"  > Vigilando techos en {nombre}...", end="\r")
    try:
        df = yf.download(ticker, period="1y", progress=False)
        if df is None or len(df) < 50:
            return
        df.columns = [c[0].lower() if isinstance(c, tuple) else c.lower()
                      for c in df.columns]

        df['vol_media'] = df['volume'].rolling(20).mean()
        df['sma200'] = df['close'].rolling(200).mean()

        # Definición de Techo (Máximo de los últimos 40 días)
        resistencia = df['high'].iloc[-(
            CONFIG['ventana_resistencia']+1):-1].max()

        v1 = df.iloc[-1]
        precio_actual = float(v1['close'])
        volumen_actual = float(v1['volume'])
        vol_media = float(v1['vol_media'])
        sma200 = float(v1['sma200'])

        # 1. ¿COMPRA CONFIRMADA? (Ruptura + Volumen + Tendencia)
        if precio_actual > resistencia:
            if volumen_actual > (vol_media * CONFIG['filtro_volumen']) and precio_actual > sma200:
                tp = precio_actual * (1 + CONFIG['objetivo_breakout'])
                sl = precio_actual * (1 - CONFIG['stop_loss_breakout'])
                cantidad = int(
                    (MI_PORTFOLIO['capital_total'] * MI_PORTFOLIO['riesgo_max_por_operacion']) / (precio_actual - sl))

                print(f"\r{'═'*68}")
                print(f"  🚀 ¡BREAKOUT CONFIRMADO!: {nombre}")
                print(
                    f"  Ruptura con fuerza: {((volumen_actual/vol_media)-1)*100:.1f}% volumen extra")
                print(f"{'═'*68}")
                print(
                    f"  ✅ ENTRADA: ${precio_actual:,.2f} | 🚀 TARGET: ${tp:,.2f}")
                print(f"  ⚠️ STOP LOSS: ${sl:,.2f}")
                print(f"  🛒 IOL: Comprar {cantidad} unidades")
                print(f"{'═'*68}")
                return

        # 2. RADAR DE ACECHO CON SENSOR DE VOLUMEN
        distancia_al_techo = (
            (resistencia - precio_actual) / precio_actual) * 100

        if 0 < distancia_al_techo <= 5.0:
            # Si el volumen ya supera la media, ponemos la alerta
            alerta_v = " ⚠️ [VOLUMEN ALTO]" if volumen_actual > vol_media else ""

            if distancia_al_techo < 1.5:
                estado = f"🔥 PRESIÓN ALTA: ¡A punto de romper!{alerta_v}"
            else:
                estado = f"👀 ACECHANDO: Acercándose al techo{alerta_v}"

            RADAR_TECHO.append(
                f"{nombre:<6} | {distancia_al_techo:>4.1f}% del techo | {estado}")

    except:
        return


if __name__ == "__main__":
    print("\n╔════════════════════════════════════════════════════════════════════╗")
    print("║      FRANCOTIRADOR v2.8 — BREAKOUT (VOLUMEN SENSOR)                ║")
    print("╚════════════════════════════════════════════════════════════════════╝")

    for nom, tick in ACTIVOS.items():
        analizar_breakout(nom, tick)

    if RADAR_TECHO:
        print("\n  🚀 RADAR DE RUPTURAS (Vigilando el salto):")
        print(f"  {'─'*68}")
        for item in RADAR_TECHO:
            print(f"  >> {item}")
        print(f"  {'─'*68}")

    print(
        "\n  Escaneo finalizado. Si ves [VOLUMEN ALTO], prepará el dedo, Darío.\n")
