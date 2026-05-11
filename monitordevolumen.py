import yfinance as yf
import pandas as pd
import pandas_ta as ta
import warnings
from colorama import init, Fore, Back, Style

init(autoreset=True)
warnings.filterwarnings('ignore')

CAPITAL_TOTAL = 900000
RIESGO_POR_TRADE = 0.02

ACTIVOS = {
    "LOMA": "LOMA.BA", "GGAL": "GGAL.BA", "PAMP": "PAMP.BA",
    "YPFD": "YPFD.BA", "VIST": "VIST.BA", "KO": "KO",
    "AAPL": "AAPL", "MSFT": "MSFT", "NVDA": "NVDA",
    "MELI": "MELI.BA", "JNJ": "JNJ", "COME": "COME.BA", "SAMI": "SAMI.BA"
}

def analizar_mercado():
    print("\n" + "="*130)
    print(f"{Fore.CYAN}{Style.BRIGHT}║{'FRANCOTIRADOR v3.7 — TABLERO DE PRESIÓN (VOLUMEN + INTENCIÓN)':^128}║")
    print("="*130)
    header = f"{'ACTIVO':<7} | {'PISO %':<7} | {'RSI':<5} | {'VOLUMEN':<12} | {'PRESIÓN':<15} | {'ACCIÓN':<22} | {'COMPRA':<8} | {'STOP'}"
    print(header)
    print("-"*130)

    for nombre, ticker in ACTIVOS.items():
        try:
            df = yf.download(ticker, period="1y", interval="1d", progress=False)
            if df.empty: continue
            df.columns = [c[0].lower() if isinstance(c, tuple) else c.lower() for c in df.columns]
            
            df['rsi'] = ta.rsi(df['close'], length=14)
            soporte = df['low'].iloc[-41:-1].min()
            precio = float(df['close'].iloc[-1])
            rsi_actual = float(df['rsi'].iloc[-1])
            
            # --- COMPROBADOR DE VOLUMEN Y PRESIÓN ---
            vol_actual = float(df['volume'].iloc[-1])
            vol_media = float(df['volume'].rolling(20).mean().iloc[-1])
            ratio_vol = vol_actual / vol_media
            
            # Cálculo de Presión (Donde cerró respecto al rango del día)
            rango = df['high'].iloc[-1] - df['low'].iloc[-1]
            presion_val = ((df['close'].iloc[-1] - df['low'].iloc[-1]) - (df['high'].iloc[-1] - df['close'].iloc[-1])) / rango if rango != 0 else 0
            
            presion_txt = "⚪ Neutral"
            if ratio_vol > 1.2:
                if presion_val > 0.3: presion_txt = Fore.GREEN + "🟢 COMPRA"
                elif presion_val < -0.3: presion_txt = Fore.RED + "🔴 VENTA"
            
            vol_status = "Bajo"
            if ratio_vol > 1.5: vol_status = "EXPLOSIÓN 🚨"
            elif ratio_vol > 1.2: vol_status = "ALTO 🔥"
            elif ratio_vol > 1.0: vol_status = "Normal+"

            d_piso = ((precio - soporte) / soporte) * 100
            nota = "💤 Neutro"
            c, s = "-", "-"
            color_fila = Fore.WHITE

            # GATILLO: Piso + RSI bajo + Presión de Compra
            if d_piso < 1.8 and rsi_actual < 45:
                color_fila = Fore.BLACK + Back.GREEN + Style.BRIGHT
                c = round(precio, 2)
                s = round(soporte * 0.98, 2) # Tu Stop Loss
                nota = "💥 DISPARE!"

            linea = f"{nombre:<7} | {d_piso:>5.1f}% | {rsi_actual:>5.1f} | {vol_status:<12} | {presion_txt:<24} | {nota:<22} | {c:<8} | {s}"
            print(color_fila + linea)

        except Exception: continue

    print("="*130)

if __name__ == "__main__":
    analizar_mercado()