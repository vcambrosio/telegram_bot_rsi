# Monitor RSI - Versão Simplificada com Token e Chat ID corretos

import pandas as pd
import yfinance as yf
import requests
from datetime import datetime
import pytz
import sys
import time

# ==================== CONFIGURAÇÕES FIXAS ====================
CHAT_ID = '18037748'
BOT_TOKEN = '8341816244:AAE6GOR8-GZ2wDtt_MU1Fcq7bfo5TQNvLjg'

# ==================== CONFIGURAÇÕES ====================
MM_PERIOD = 200                 # Período da média móvel

# ==================== CONFIGURAÇÕES RSI ====================
RSI_PERIOD = 2                # Período do RSI
RSI_SOBRECOMPRADO = 70         # Valor para considerar sobrecomprado
RSI_SOBREVENDIDO = 25          # Valor para considerar sobrevendido

# Todos os ativos
ATIVOS = [
'BOVA11.SA',   
'PETR4.SA',   
'VALE3.SA',   
'BBAS3.SA',   
'MGLU3.SA',   
'ITUB4.SA',   
'SEQL3.SA'
]


class TelegramBot:
    """Classe para enviar mensagens via Telegram usando requests"""
    
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    def send_message(self, text):
        """Envia mensagem para o Telegram (sem formatação)"""
        try:
            data = {
                'chat_id': self.chat_id,
                'text': text
            }
            
            response = requests.post(self.url, data=data, timeout=10)
            
            # Debug detalhado
            print(f"📤 Tentativa de envio para Telegram")
            print(f"📝 Tamanho da mensagem: {len(text)} caracteres")
            print(f"📋 Status code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Erro no Telegram: {response.text}")
                return False
                
            return True
            
        except requests.exceptions.Timeout:
            print(f"❌ Timeout ao enviar mensagem para Telegram")
            return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Erro de conexão ao enviar para Telegram")
            return False
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem: {e}")
            return False

def calculate_rsi(prices, period=RSI_PERIOD):
    """Calcula RSI"""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.ewm(com=period-1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period-1, min_periods=period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi.iloc[-1], 2)

def calculate_moving_average(prices, period=MM_PERIOD):
    """Calcula média móvel aritmética"""
    if len(prices) < period:
        return None, None
    
    try:
        ma = prices.rolling(window=period).mean()
        current_ma = ma.iloc[-1]
        current_price = prices.iloc[-1]
        
        relative_position = ((current_price - current_ma) / current_ma) * 100
        return round(current_ma, 2), round(relative_position, 2)
    except Exception:
        return None, None

def get_rsi_data(symbol):
    """Obtém dados e calcula RSI para um ativo"""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period='250d', interval='1d')
        
        if data.empty or len(data) < 50:
            return None
        
        rsi = calculate_rsi(data['Close'])
        price = data['Close'].iloc[-1]
        variation = ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
        
        # Calcula média móvel
        ma_value, ma_relative = calculate_moving_average(data['Close'], MM_PERIOD)
        
        return {
            'symbol': symbol.replace('.SA', ''),
            'rsi': rsi,
            'price': price,
            'variation': variation,
            'date': data.index[-1].strftime('%d/%m/%Y'),
            'ma_value': ma_value,
            'ma_relative': ma_relative
        }
    except Exception as e:
        print(f"Erro ao processar {symbol}: {e}")
        return None

def format_signal(rsi):
    """Formata sinal baseado no RSI"""
    if rsi <= 20:
        return "🚀 FORTE COMPRA", "🟢"
    elif rsi <= RSI_SOBREVENDIDO:
        return "📈 COMPRA", "🟢"
    elif rsi >= 80:
        return "⚠️ FORTE VENDA", "🔴"
    elif rsi >= RSI_SOBRECOMPRADO:
        return "📉 VENDA", "🔴"
    elif rsi < 40:
        return "👀 ATENÇÃO COMPRA", "🟡"
    elif rsi > 60:
        return "👀 ATENÇÃO VENDA", "🟡"
    else:
        return "➡️ NEUTRO", "⚪"

def is_compra_opportunity(data):
    """Verifica se é uma oportunidade de compra (RSI abaixo do sobrevendido E preço acima da MM)"""
    if data['ma_value'] is None:
        return False
    return data['rsi'] <= RSI_SOBREVENDIDO and data['price'] > data['ma_value']

def is_venda_opportunity(data):
    """Verifica se é uma oportunidade de venda (RSI acima del sobrecomprado E preço abaixo da MM)"""
    if data['ma_value'] is None:
        return False
    return data['rsi'] >= RSI_SOBRECOMPRADO and data['price'] < data['ma_value']

def run_analysis():
    """
    Executa análise de RSI e envia para Telegram
    """
    print("📄 Iniciando análise de RSI...")
    print("=" * 80)
    
    results = []
    
    for symbol in ATIVOS:
        print(f"Processando {symbol}...", end=" ")
        
        data = get_rsi_data(symbol)
        if data is None:
            print("❌ ERRO")
            continue
        
        signal, color = format_signal(data['rsi'])
        results.append(data)
        
        mm_info = f" | MM{MM_PERIOD}: R${data['ma_value']:.2f} ({data['ma_relative']:+.1f}%)" if data['ma_value'] is not None else " | MM: N/A"
        print(f"✅ | RSI: {data['rsi']} ({signal}) | Preço: R${data['price']:.2f}{mm_info}")
    
    print("\n" + "=" * 80)
    print("📊 RESUMO DA ANÁLISE")
    print("=" * 80)
    
    if results:
        results.sort(key=lambda x: x['rsi'])
        
        print(f"\n📈 TODOS OS ATIVOS ANALISADOS ({len(results)}):")
        print("-" * 70)
        
        for data in results:
            signal, color = format_signal(data['rsi'])
            mm_info = f" | MM{MM_PERIOD}: R${data['ma_value']:.2f} ({data['ma_relative']:+.1f}%)" if data['ma_value'] is not None else " | MM: N/A"
            print(f"{color} {data['symbol']}: RSI {data['rsi']} | {signal} | Preço: R${data['price']:.2f}{mm_info}")
        
        # Oportunidades de compra
        compras = [r for r in results if is_compra_opportunity(r)]
        if compras:
            print(f"\n🟢 OPORTUNIDADES DE COMPRA ({len(compras)}):")
            print(f"   (RSI ≤ {RSI_SOBREVENDIDO} E preço > MM{MM_PERIOD})")
            for r in sorted(compras, key=lambda x: x['rsi']):
                mm_info = f" | MM: R${r['ma_value']:.2f} ({r['ma_relative']:+.1f}%)" if r['ma_value'] is not None else " | MM: N/A"
                print(f"   • {r['symbol']}: RSI {r['rsi']} - Preço: R${r['price']:.2f}{mm_info}")
                print(f"     COMPROVAÇÃO: R${r['price']:.2f} > R${r['ma_value']:.2f} = {r['price'] > r['ma_value']}")
        else:
            print(f"\nℹ️  SEM OPORTUNIDADES DE COMPRA")
            print(f"   (RSI ≤ {RSI_SOBREVENDIDO} E preço > MM{MM_PERIOD})")
        
        # Oportunidades de venda
        vendas = [r for r in results if is_venda_opportunity(r)]
        if vendas:
            print(f"\n🔴 OPORTUNIDADES DE VENDA ({len(vendas)}):")
            print(f"   (RSI ≥ {RSI_SOBRECOMPRADO} E preço < MM{MM_PERIOD})")
            for r in sorted(vendas, key=lambda x: x['rsi'], reverse=True):
                mm_info = f" | MM: R${r['ma_value']:.2f} ({r['ma_relative']:+.1f}%)" if r['ma_value'] is not None else " | MM: N/A"
                print(f"   • {r['symbol']}: RSI {r['rsi']} - Preço: R${r['price']:.2f}{mm_info}")
                print(f"     COMPROVAÇÃO: R${r['price']:.2f} < R${r['ma_value']:.2f} = {r['price'] < r['ma_value']}")
        else:
            print(f"\nℹ️  SEM OPORTUNIDADES DE VENDA")
            print(f"   (RSI ≥ {RSI_SOBRECOMPRADO} E preço < MM{MM_PERIOD})")
    
    # Estatísticas gerais
    if results:
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   • Total analisado: {len(results)}")
        
        avg_rsi = sum(r['rsi'] for r in results) / len(results)
        print(f"   • RSI médio: {avg_rsi:.1f}")
    
    # Enviar para Telegram
    send_telegram_summary(results)
    
    print(f"\n⏰ Análise concluída às {datetime.now().strftime('%H:%M:%S')}")

def send_telegram_summary(results):
    """Envia resumo para o Telegram"""
    try:
        bot = TelegramBot(BOT_TOKEN, CHAT_ID)
        
        # Mensagem sem formatação nenhuma - texto puro
        message = f"ANÁLISE MANUAL DE RSI - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        message += f"CONFIGURAÇÕES:\n"
        message += f"• RSI{RSI_PERIOD}: ≥{RSI_SOBRECOMPRADO} (sobrecomprado) | ≤{RSI_SOBREVENDIDO} (sobrevendido)\n"
        message += f"• MM{MM_PERIOD} como referência para oportunidades\n"
        message += f"• Total analisado: {len(results)}\n\n"
        
        # Oportunidades de compra
        compras = [r for r in results if is_compra_opportunity(r)]
        if compras:
            message += f"🟢 OPORTUNIDADES DE COMPRA (RSI ≤ {RSI_SOBREVENDIDO} E preço > MM):\n"
            for r in sorted(compras, key=lambda x: x['rsi']):
                mm_info = f"{r['ma_relative']:+.1f}%" if r['ma_relative'] is not None else "N/A"
                message += f"• {r['symbol']}: RSI {r['rsi']} - R${r['price']:.2f} (MM: R${r['ma_value']:.2f} | {mm_info})\n"
            message += "\n"
        else:
            message += f"ℹ️ SEM OPORTUNIDADES DE COMPRA\n"
            message += f"(RSI ≤ {RSI_SOBREVENDIDO} E preço > MM{MM_PERIOD})\n\n"
        
        # Oportunidades de venda
        vendas = [r for r in results if is_venda_opportunity(r)]
        if vendas:
            message += f"🔴 OPORTUNIDADES DE VENDA (RSI ≥ {RSI_SOBRECOMPRADO} E preço < MM):\n"
            for r in sorted(vendas, key=lambda x: x['rsi'], reverse=True):
                mm_info = f"{r['ma_relative']:+.1f}%" if r['ma_relative'] is not None else "N/A"
                message += f"• {r['symbol']}: RSI {r['rsi']} - R${r['price']:.2f} (MM: R${r['ma_value']:.2f} | {mm_info})\n"
            message += "\n"
        else:
            message += f"ℹ️ SEM OPORTUNIDADES DE VENDA\n"
            message += f"(RSI ≥ {RSI_SOBRECOMPRADO} E preço < MM{MM_PERIOD})\n\n"
        
        message += f"Análise manual executada"
        
        print(f"📤 Preparando para enviar mensagem para Telegram...")
        print(f"📝 Tamanho da mensagem: {len(message)} caracteres")
        
        # Enviar sem formatação
        if bot.send_message(message):
            print("✅ Resumo enviado para o Telegram!")
        else:
            print("❌ Erro ao enviar resumo para Telegram")
        
    except Exception as e:
        print(f"❌ Erro ao enviar para Telegram: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Função principal do script"""
    print("🤖 Monitor de RSI para Telegram")
    print(f"📊 MM{MM_PERIOD} como referência para oportunidades")
    print(f"📈 RSI{RSI_PERIOD}: ≥{RSI_SOBRECOMPRADO} (sobrecomprado) | ≤{RSI_SOBREVENDIDO} (sobrevendido)")
    print("=" * 80)
    
    # Executar análise
    run_analysis()

if __name__ == "__main__":
    main()