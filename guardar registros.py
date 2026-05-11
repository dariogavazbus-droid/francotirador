import yfinance as yf
import pandas as pd
import pandas_ta as ta
import warnings
import os
from datetime import datetime
from colorama import init, Fore, Back, Style

init(autoreset=True)
warnings.filterwarnings('ignore')

# --- CONFIGURACIÓN ---
CAPITAL_TOTAL = 900000
RIESGO_POR_TRADE = 0.02
EXCEL_FILE = "francotirador_historico.xlsx"

ACTIVOS = {
    "LOMA": "LOMA.BA", "GGAL": "GGAL.BA", "PAMP": "PAMP.BA",
    "YPFD": "YPFD.BA", "VIST": "VIST.BA", "KO": "KO",
    "AAPL": "AAPL", "MSFT": "MSFT", "NVDA": "NVDA",
    "MELI": "MELI.BA", "JNJ": "JNJ", "COME": "COME.BA", "SAMI": "SAMI.BA",
    "ETHA": "ETHA"
}


def guardar_en_excel(nuevos_datos):
    # Esta parte debe tener sangría (indentación)
    df_nuevo = pd.DataFrame(nuevos_datos)

    if os.path.exists(EXCEL_FILE):
        # Leer el histórico existente y concatenar
        df_historico = pd.read_excel(EXCEL_FILE)
        df_final = pd.concat([df_historico, df_nuevo], ignore_index=True)
    else:
        df_final = df_nuevo

    # Guardar archivo Excel[cite: 1]
    df_final.to_excel(EXCEL_FILE, index=False)


def analizar_mercado():
    fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M")
    lista_para_excel = []

    print("\n" + "="*120)
    print(f"{Fore.CYAN}{Style.BRIGHT}║      FRANCOTIRADOR v3.7.1 — EXCEL LOGGER (CORREGIDO)              ║")
    print("="*120)

    header = f"{'ACTIVO':<7} | {'PISO %':<7} | {'TECHO %':<7} | {'RSI':<5} | {'VOL':<12} | {'ACCIÓN':<25}"
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
            resistencia = float(df['high'].iloc[-41:-1].max())
            soporte = float(df['low'].iloc[-41:-1].min())
            precio = float(df['close'].iloc[-1])
            rsi_actual = float(df['rsi'].iloc[-1])

            vol_actual = float(df['volume'].iloc[-1])
            vol_media = float(df['volume'].rolling(20).mean().iloc[-1])
            ratio_vol = (vol_actual / vol_media)

            vol_status = "Bajo"
            if ratio_vol > 1.0:
                vol_status = "Normal+"
            if ratio_vol > 1.2:
                vol_status = "ALTO"
            if ratio_vol > 1.5:
                vol_status = "EXPLOSION"

            d_piso = ((precio - soporte) / soporte) * 100
            d_techo = ((resistencia - precio) / precio) * 100

            nota = "Neutro"
            c, t, s, u = "-", 0.0, 0.0, 0
            color_fila = Fore.WHITE

            es_rebote = d_piso < 1.5 and rsi_actual < 45 and ratio_vol > 0.9
            es_ruptura = (d_techo < 1.0 or precio >
                          resistencia) and rsi_actual < 68 and ratio_vol > 1.1

            if es_rebote or es_ruptura:
                color_fila = Fore.BLACK + Back.GREEN + Style.BRIGHT
                c_val = round(precio, 2)
                if es_rebote:
                    s = round(soporte * 0.98, 2)
                    t = round(precio * 1.06, 2)
                else:
                    s = round(resistencia * 0.97, 2)
                    t = round(precio * 1.08, 2)

                distancia_stop = abs(c_val - s)
                u = int((CAPITAL_TOTAL * RIESGO_POR_TRADE) /
                        distancia_stop) if distancia_stop > 0 else 0
                nota = f"DISPARE! ({u} u)"
                c = str(c_val)

            elif rsi_actual > 70:
                color_fila = Fore.RED + Style.BRIGHT
                nota = "CARO"

            # Guardar en la lista para el Excel[cite: 1]
            lista_para_excel.append({
                "Fecha": fecha_hoy,
                "Activo": nombre,
                "Precio": precio,
                "RSI": round(rsi_actual, 2),
                "Volumen": vol_status,
                "Accion": nota,
                "Target": t,
                "Stop Loss": s,
                "Unidades": u,
                "Piso %": round(d_piso, 2),
                "Techo %": round(d_techo, 2)
            })

            linea = f"{nombre:<7} | {d_piso:>5.1f}% | {d_techo:>6.1f}% | {rsi_actual:>5.1f} | {vol_status:<12} | {nota:<25}"
            print(color_fila + linea)

        except Exception:
            continue

    if lista_para_excel:
        guardar_en_excel(lista_para_excel)
        print("\n" + "="*120)
        print(
            f"ÉXITO: Se han guardado {len(lista_para_excel)} registros en {EXCEL_FILE}")


if __name__ == "__main__":
    analizar_mercado()
