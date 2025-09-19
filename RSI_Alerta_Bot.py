# arquivo: top5_rsi2_ld.py
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime
import os

# === CONFIGURAÇÕES ===
BOT_TOKEN = '8341816244:AAE6GOR8-GZ2wDtt_MU1Fcq7bfo5TQNvLjg'
CHAT_ID = '18037748'

RANKING_FILE = "ranking_rsi.txt"   # formato: PETR4;10;8,32
SMA_PERIOD = 200
EMA_PERIOD = 21
RSI_PERIOD = 2
HIST_PERIOD = '520d'

MAX_TO_SEND = 5

# === TELEGRAM ===
class TelegramBot:
    def __init__(self, token, chat_id):
        self.url = f"https://api.telegram.org/bot{token}/sendMessage"
        self.chat_id = chat_id

    def send_message(self, text):
        try:
            r = requests.post(self.url, data={"chat_id": self.chat_id, "text": text}, timeout=10)
            return r.status_code == 200
        except Exception as e:
            print("Erro Telegram:", e)
            return False

# === INDICADORES ===
def calculate_rsi(prices, period=RSI_PERIOD):
    delta = prices.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi.iloc[-1], 2)

# === LEITURA DO TXT ===
def load_ranking(file_path):
    ativos = []
    linhas_invalidas = []
    if not os.path.exists(file_path):
        print(f"Arquivo {file_path} não encontrado.")
        return ativos, linhas_invalidas

    with open(file_path, 'r', encoding='utf-8') as f:
        for lineno, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split(';')
            if len(parts) < 3:
                linhas_invalidas.append(f"Linha {lineno}: {line}")
                continue
            symbol_raw = parts[0].strip().upper()
            if not symbol_raw.endswith('.SA'):
                symbol = symbol_raw + '.SA'
            else:
                symbol = symbol_raw

            try:
                rsi_ref = float(parts[1].replace(',', '.'))
                ld_val = float(parts[2].replace(',', '.'))
            except:
                linhas_invalidas.append(f"Linha {lineno}: {line}")
                continue

            ativos.append((symbol, rsi_ref, ld_val))
    return ativos, linhas_invalidas

# === ANÁLISE DE UM ATIVO ===
def analyze_asset(symbol, rsi_ref, ld_val):
    try:
        t = yf.Ticker(symbol)
        df = t.history(period=HIST_PERIOD, interval='1d')
        if df.empty:
            return None

        closes = df['Close'].dropna()
        if len(closes) < SMA_PERIOD:
            return None

        price = float(closes.iloc[-1])
        sma200 = closes.rolling(window=SMA_PERIOD).mean().iloc[-1]
        ema21 = closes.ewm(span=EMA_PERIOD, adjust=False).mean().iloc[-1]
        rsi2 = calculate_rsi(closes, RSI_PERIOD)

        # Filtros:
        if price <= sma200:  # filtro SMA200
            return None
        if rsi2 >= rsi_ref:  # filtro RSI2
            return None

        dist_to_ema21 = ((price - ema21) / ema21) * 100 if ema21 != 0 else None

        return {
            "symbol": symbol,
            "symbol_short": symbol.replace('.SA',''),
            "price": round(price, 2),
            "ld": ld_val,
            "rsi2": rsi2,
            "rsi_ref": rsi_ref,
            "sma200": round(sma200, 2),
            "ema21": round(ema21, 2),
            "dist_to_ema21": round(dist_to_ema21, 2) if dist_to_ema21 is not None else None
        }
    except Exception as e:
        print(f"Erro em {symbol}: {e}")
        return None

# === PRINCIPAL ===
def main():
    bot = TelegramBot(BOT_TOKEN, CHAT_ID)

    ativos, linhas_invalidas = load_ranking(RANKING_FILE)
    total_lidos = len(ativos) + len(linhas_invalidas)
    if not ativos and not linhas_invalidas:
        bot.send_message("Nenhum ativo válido encontrado no ranking.")
        return

    results = []
    for symbol, rsi_ref, ld in ativos:
        data = analyze_asset(symbol, rsi_ref, ld)
        if data:
            results.append(data)

    total_filtrados = len(results)
    if not results:
        bot.send_message("Nenhum ativo passou nos filtros SMA200 e RSI2 < referência.")
        return

    results.sort(key=lambda x: x["ld"], reverse=True)
    top = results[:MAX_TO_SEND]

    # Cabeçalho da mensagem
    message = f"SETUP IFR - TOP {len(top)} ATIVOS\n"
    message += f"Filtros: Preço > SMA{SMA_PERIOD} | RSI{RSI_PERIOD} < referência\n"
    message += f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"

    # Blocos por ativo
    for r in top:
        dist = f"{r['dist_to_ema21']:+.2f}%" if r['dist_to_ema21'] is not None else "N/A"
        message += f"{r['symbol_short']} | LD={r['ld']:.2f}\n"
        message += f"RSI2={r['rsi2']:.2f} (<{r['rsi_ref']})\n"
        message += f"Preço=R${r['price']:.2f}\n"
        message += f"EMA{EMA_PERIOD}=R${r['ema21']:.2f} ({dist})\n"
        message += f"SMA{SMA_PERIOD}=R${r['sma200']:.2f}\n"
        message += "─────────────\n"

    # Resumo estatístico
    message += "\n📌 Estatísticas:\n"
    message += f"• Linhas no arquivo: {total_lidos}\n"
    message += f"• Ativos válidos: {len(ativos)}\n"
    message += f"• Linhas inválidas: {len(linhas_invalidas)}\n"
    message += f"• Passaram nos filtros: {total_filtrados}\n"
    message += f"• Enviados (TOP {MAX_TO_SEND}): {len(top)}\n"

    if linhas_invalidas:
        message += "\n⚠️ Linhas inválidas encontradas:\n"
        for l in linhas_invalidas:
            message += f"- {l}\n"

    bot.send_message(message)
    print("Mensagem enviada:\n", message)

if __name__ == "__main__":
    main()
