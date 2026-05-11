import yfinance as yf
import pandas as pd
import pandas_ta as ta
import warnings
import webbrowser
from colorama import init, Fore, Back, Style

init(autoreset=True)
warnings.filterwarnings('ignore')

# --- CONFIGURACIÓN ---
CAPITAL_TOTAL = 900000
RIESGO_POR_TRADE = 0.02

ACTIVOS = {
    "LOMA": "LOMA.BA", "GGAL": "GGAL.BA", "PAMP": "PAMP.BA",
    "YPFD": "YPFD.BA", "VIST": "VIST.BA", "KO": "KO",
    "AAPL": "AAPL", "MSFT": "MSFT", "NVDA": "NVDA",
    "MELI": "MELI", "JNJ": "JNJ", "COME": "COME.BA", "SAMI": "SAMI.BA"
}


def abrir_recursos(nombre):
    """Abre el gráfico correcto y Gemini para CUALQUIER activo"""
    ticker_real = ACTIVOS.get(nombre)
    if not ticker_real:
        print(f"{Fore.RED}Activo no encontrado.")
        return

    # Lógica para TradingView: Si termina en .BA es de Argentina
    if ".BA" in ticker_real:
        tv_symbol = f"BCBA:{nombre}"
    else:
        tv_symbol = nombre  # Para AAPL, KO, MELI, etc.

    url_tv = f"https://es.tradingview.com/chart/?symbol={tv_symbol}"

    # Preparamos el link de Gemini
    prompt = f"Analizá el activo {nombre}. Decime si ves una buena oportunidad de entrada por análisis técnico hoy."
    url_gemini = f"https://gemini.google.com/app?prompt={prompt.replace(' ', '%20')}"

    print(f"{Fore.CYAN}Cazando información para {nombre}...")
    webbrowser.open(url_tv)
    webbrowser.open(url_gemini)


def analizar_mercado():
    print("\n" + "="*120)
    print(f"{Fore.CYAN}{Style.BRIGHT}║      FRANCOTIRADOR v3.6 PC — VERSIÓN TOTAL (TODOS LOS ACTIVOS)           ║")
    print("="*120)
    header = f"{'ACTIVO':<7} | {'PISO %':<7} | {'TECHO %':<7} | {'RSI':<5} | {'VOL':<12} | {'ACCIÓN':<25} | {'COMPRA':<8}"
    print(header)
    print("-"*120)

    for nombre, ticker in ACTIVOS.items():
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
            ratio_vol = (float(df['volume'].iloc[-1]) /
                         float(df['volume'].rolling(20).mean().iloc[-1]))

            d_piso = ((precio - soporte) / soporte) * 100
            d_techo = ((resistencia - precio) / precio) * 100

            # Lógica de colores
            status = "💤 Neutro"
            color_fila = Fore.WHITE
            es_rebote = d_piso < 1.5 and rsi_actual < 45 and ratio_vol > 0.9
            es_ruptura = (d_techo < 1.0 or precio >
                          resistencia) and rsi_actual < 68 and ratio_vol > 1.1

            if es_rebote or es_ruptura:
                color_fila = Fore.BLACK + Back.GREEN + Style.BRIGHT
                status = "💥 ¡DISPARE!"
            elif rsi_actual > 70:
                color_fila = Fore.RED + Style.BRIGHT
                status = "🥵 CARO"
            elif d_techo < 2.5 or d_piso < 2.5 or ratio_vol > 1.5:
                color_fila = Fore.YELLOW + Style.BRIGHT
                status = "⚠️ ATENCIÓN"

            print(
                color_fila + f"{nombre:<7} | {d_piso:>5.1f}% | {d_techo:>6.1f}% | {rsi_actual:>5.1f} | {ratio_vol:>12.2f} | {status:<25} | {precio:>8.2f}")

        except:
            continue

    print("="*120)

    # --- LA PARTE QUE QUERÍAS: FUNCIONA CON TODOS ---
    while True:
        target = input(
            f"\n🎯 Poné el nombre (ej: SAMI, GGAL, KO) para abrir Gráfico + Gemini (o Enter para salir): ").upper()
        if target == "":
            break
        if target in ACTIVOS:
            abrir_recursos(target)
        else:
            print(f"{Fore.RED}Ese activo no está en tu lista.")


if __name__ == "__main__":
    analizar_mercado()
