# arquivo: setup123_alerta_bot.py
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime
import os

# === CONFIGURAÇÕES ===
BOT_TOKEN = '8341816244:AAE6GOR8-GZ2wDtt_MU1Fcq7bfo5TQNvLjg'
CHAT_ID = '18037748'

RANKING_FILE = "ranking_setup123.txt"   # formato: PETR4;8,32
HIST_PERIOD = '120d'  # histórico suficiente para detectar padrão

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

# === LEITURA DO TXT ===
def load_ranking(file_path):
    ativos = []
    linhas_invalidas = []
    if not os.path.exists(file_path):
        print(f"[ERRO] Arquivo {file_path} não encontrado.")
        return ativos, linhas_invalidas

    with open(file_path, 'r', encoding='utf-8') as f:
        for lineno, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split(';')
            if len(parts) < 2:
                linhas_invalidas.append(f"Linha {lineno}: {line}")
                continue
            symbol_raw = parts[0].strip().upper()
            if not symbol_raw.endswith('.SA'):
                symbol = symbol_raw + '.SA'
            else:
                symbol = symbol_raw

            try:
                ld_val = float(parts[1].replace(',', '.'))
            except:
                linhas_invalidas.append(f"Linha {lineno}: {line}")
                continue

            ativos.append((symbol, ld_val))
    return ativos, linhas_invalidas

# === DETECÇÃO DO SETUP 123 COM FILTRO EDEN ===
def detect_setup123(symbol):
    try:
        print(f"[INFO] Verificando {symbol}...")
        t = yf.Ticker(symbol)
        df = t.history(period=HIST_PERIOD, interval='1d')
        if df.empty or len(df) < 20:  # mínimo necessário para EMAs
            print(f"[WARN] Histórico insuficiente para {symbol}.")
            return None

        df = df.dropna().reset_index()

        # === CÁLCULO DAS EMAS ===
        df['EMA8'] = df['Close'].ewm(span=8, adjust=False).mean()
        df['EMA80'] = df['Close'].ewm(span=80, adjust=False).mean()

        # Pega últimos 3 candles
        c1, c2, c3 = df.iloc[-3], df.iloc[-2], df.iloc[-1]

        # CONDIÇÃO DO SETUP 123 (candle do meio tem mínima menor)
        cond_candle = (c2["Low"] < c1["Low"]) and (c2["Low"] < c3["Low"])

        # FILTRO EDEN
        ema8_up = df['EMA8'].iloc[-1] > df['EMA8'].iloc[-2]
        ema80_up = df['EMA80'].iloc[-1] > df['EMA80'].iloc[-2]
        ema8_above_ema80 = df['EMA8'].iloc[-1] > df['EMA80'].iloc[-1]

        cond_eden = ema8_up and ema80_up and ema8_above_ema80

        if cond_candle and cond_eden:
            ultimo_close = c3["Close"]
            setup_acionado = ultimo_close > c3["High"]
            print(f"[ACIONADO] {symbol} - Setup 123 com filtro Eden acionado!")
            return {
                "symbol": symbol,
                "symbol_short": symbol.replace(".SA", ""),
                "data_candle3": c3["Date"].strftime("%d/%m/%Y"),
                "entrada": round(c3["High"], 2),
                "stop": round(c2["Low"], 2),
                "preco_atual": round(ultimo_close, 2),
                "acionado": setup_acionado,
                "EMA8": round(df['EMA8'].iloc[-1],2),
                "EMA80": round(df['EMA80'].iloc[-1],2)
            }
        else:
            print(f"[IGNORADO] {symbol} - Setup não acionado ou filtro Eden não passou.")
            return None
    except Exception as e:
        print(f"[ERRO] {symbol}: {e}")
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
    for symbol, ld in ativos:
        print(f"[PROCESSANDO] {symbol} com LD={ld}")
        data = detect_setup123(symbol)
        if data and data["acionado"]:
            data["ld"] = ld
            results.append(data)
        else:
            print(f"[RESULTADO] {symbol} não acionou o setup.")

    total_filtrados = len(results)
    if not results:
        bot.send_message("Nenhum ativo apresentou Setup 123 acionado com filtro Eden.")
        return

    results.sort(key=lambda x: x["ld"], reverse=True)
    top = results[:MAX_TO_SEND]

    # Cabeçalho da mensagem
    message = f"SETUP 123 COMPRA - TOP {len(top)} ATIVOS (Filtro Eden dos Trades)\n"
    message += f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"

    # Blocos por ativo
    for r in top:
        message += f"{r['symbol_short']} | LD={r['ld']:.2f}\n"
        message += f"Candle3: {r['data_candle3']}\n"
        message += f"Entrada: R${r['entrada']:.2f} | Stop: R${r['stop']:.2f}\n"
        message += f"Preço Atual: R${r['preco_atual']:.2f}\n"
        message += f"EMA8: {r['EMA8']} | EMA80: {r['EMA80']}\n"
        message += "─────────────\n"

    # Resumo estatístico
    message += "\n📌 Estatísticas:\n"
    message += f"• Linhas no arquivo: {total_lidos}\n"
    message += f"• Ativos válidos: {len(ativos)}\n"
    message += f"• Linhas inválidas: {len(linhas_invalidas)}\n"
    message += f"• Setups acionados: {total_filtrados}\n"
    message += f"• Enviados (TOP {MAX_TO_SEND}): {len(top)}\n"

    if linhas_invalidas:
        message += "\n⚠️ Linhas inválidas encontradas:\n"
        for l in linhas_invalidas:
            message += f"- {l}\n"

    bot.send_message(message)
    print("[INFO] Mensagem enviada:\n", message)

if __name__ == "__main__":
    main()
