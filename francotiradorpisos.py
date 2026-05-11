import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ──────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE DARÍO (Francotirador v2.8 - Tactical Edition)
# ──────────────────────────────────────────────────────────────
MI_PORTFOLIO = {"capital_total": 400000, "riesgo_max_por_operacion": 0.02}

# Activos ideales para REBOTE (Soportes firmes)
ACTIVOS = {
    "LOMA": "LOMA.BA", "GGAL": "GGAL.BA", "PAMP": "PAMP.BA",
    "YPFD": "YPFD.BA", "VIST": "VIST.BA", "KO": "KO",
    "AAPL": "AAPL", "MSFT": "MSFT", "SPY": "SPY",
    "WMT": "WMT",   # Walmart: Muy prolija en soportes
    "MCD": "MCD",   # McDonald's: Refugio seguro
    "JNJ": "JNJ"    # Johnson & Johnson: Movimientos lentos y predecibles
}

CONFIG = {
    "comision_total": 0.013,
    "objetivo_neto": 0.05,
    "stop_loss_pct": 0.015,
    "ratio_minimo": 2.5,
    "sma_larga": 200,
    "sma_corta": 20,
    "zona_soporte_pct": 0.07  # Radar con alcance del 7%
}

EN_LA_MIRA = []


def analizar_activo(nombre, ticker):
    print(f"  > Escaneando {nombre}...", end="\r")
    try:
        df = yf.download(ticker, period="1y", progress=False)
        if df is None or len(df) < 200:
            return
        df.columns = [c[0].lower() if isinstance(c, tuple) else c.lower()
                      for c in df.columns]

        # Cálculo de Indicadores
        df['sma200'] = df['close'].rolling(200).mean()
        df['sma20'] = df['close'].rolling(20).mean()
        df['vol_media'] = df['volume'].rolling(20).mean()
        df['rango'] = df['high'] - df['low']
        df['rango_medio'] = df['rango'].rolling(10).mean()

        v1, v2 = df.iloc[-1], df.iloc[-2]
        precio = float(v1['close'])

        # Filtro de Tendencia (Solo arriba de la SMA200)
        if precio < v1['sma200']:
            return

        # Identificación de Soporte Cercano
        ventana = 60
        puntos_soporte = df.tail(ventana)['low'].nsmallest(3).values
        soporte = next((s for s in puntos_soporte if s < precio and (
            precio - s) / precio < CONFIG['zona_soporte_pct']), None)

        if soporte:
            p = "Ninguno"
            es_vela_relevante = v1['rango'] > (v1['rango_medio'] * 0.7)

            # Reconocimiento de Patrones (Velas)
            if abs(v1['low'] - v2['low']) / precio < 0.001:
                p = "ABSORCIÓN (TWEEZER)"
            elif v1['close'] > v2['high'] and v1['open'] < v2['low']:
                p = "ENVOLVENTE ALCISTA"
            elif (v1['open'] - v1['low']) > (abs(v1['close']-v1['open']) * 2):
                p = "MARTILLO"

            # CASO 1: SEÑAL DE COMPRA CONFIRMADA
            if p != "Ninguno" and es_vela_relevante:
                tp = precio * \
                    (1 + (CONFIG['objetivo_neto'] + CONFIG['comision_total']))
                sl = soporte * (1 - CONFIG['stop_loss_pct'])
                ratio = (tp - precio) / (precio -
                                         sl) if (precio - sl) > 0 else 0

                if ratio >= CONFIG['ratio_minimo']:
                    score = 1 + (1 if v1['volume'] > v1['vol_media']
                                 else 0) + (1 if precio > v1['sma20'] else 0)
                    estrellas = "⭐" * score
                    cantidad = int(
                        (MI_PORTFOLIO['capital_total'] * MI_PORTFOLIO['riesgo_max_por_operacion']) / (precio - sl))

                    print(f"\r{'═'*65}")
                    print(f"  🎯 {estrellas} RECOMENDACIÓN: COMPRAR {nombre}")
                    print(f"  TIPO: {p}")
                    print(f"{'═'*65}")
                    print(
                        f"  ✅ PRECIO ENTRADA: ${precio:,.2f} | 🚀 TARGET: ${tp:,.2f}")
                    print(f"  ⚠️ PRECIO SALIDA (SL): ${sl:,.2f}")
                    print(f"  🛒 IOL: Comprar {cantidad} unidades")
                    print(f"{'═'*65}")
                    return

            # CASO 2: ACCIÓN EN EL RADAR (Sin patrón todavía)
            distancia = ((precio - soporte) / precio) * 100
            if distancia < 1.5:
                frase = "🎯 OBJETIVO EN MIRA: ¡Preparar gatillo!"
            elif distancia < 3.5:
                frase = "🔍 ZONA DE INTERÉS: Siguiendo de cerca"
            else:
                frase = "📡 EN APROXIMACIÓN: Falta un poco"

            EN_LA_MIRA.append(
                f"{nombre:<6} | {distancia:>4.1f}% del rebote | {frase}")
    except:
        return


if __name__ == "__main__":
    print("\n╔═══════════════════════════════════════════════════════════════╗")
    print("║     FRANCOTIRADOR v2.8 — ELITE & RADAR (TACTICAL)             ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    for nom, tick in ACTIVOS.items():
        analizar_activo(nom, tick)

    if EN_LA_MIRA:
        print("\n  👀 RADAR DE ACCIONES (Buscando el piso):")
        print(f"  {'─'*65}")
        for item in EN_LA_MIRA:
            print(f"  >> {item}")
        print(f"  {'─'*65}")

    print("\n  Escaneo finalizado. Buena jornada de trading, Darío.\n")
