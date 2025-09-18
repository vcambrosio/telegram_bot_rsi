# Monitor RSI - Versão Simplificada com Token e Chat ID corretos

import pandas as pd
import yfinance as yf
import requests
from datetime import datetime, timedelta
import pytz
import sys
import time

# ==================== CONFIGURAÇÕES FIXAS ====================
CHAT_ID = '18037748'
BOT_TOKEN = '8341816244:AAE6GOR8-GZ2wDtt_MU1Fcq7bfo5TQNvLjg'

# ==================== CONFIGURAÇÕES ====================
MM_PERIOD = 50                # Período da média móvel principal
MM_CURTA = 9                  # Período da média móvel curta (tendência)
MM_LONGA = 21                  # Período da média móvel longa (tendência)
USAR_FILTRO_TENDENCIA = True    # Ativar/desativar filtro de tendência

# ==================== CONFIGURAÇÕES RSI ====================
RSI_PERIOD = 2                # Período do RSI
RSI_SOBRECOMPRADO = 70         # Valor para considerar sobrecomprado
RSI_SOBREVENDIDO = 25          # Valor para considerar sobrevendido

# ==================== CONFIGURAÇÃO DE DATA ====================
# Data específica para análise (formato: 'YYYY-MM-DD')
# Se vazia ou None, usa a data atual
DATA_ANALISE = ''              # Exemplo: '2024-12-15' ou deixe vazio para hoje

# Todos os ativos
ATIVOS = [
'BOVA11.SA',   
'PETR4.SA',   
'VALE3.SA',   
'BBAS3.SA',   
'MGLU3.SA',   
'ITUB4.SA',   
'BBDC4.SA',   
'CSAN3.SA',   
'RAIZ4.SA',   
'PRIO3.SA',   
'PCAR3.SA',   
'B3SA3.SA',   
'BRAV3.SA',   
'AZUL4.SA',   
'BRKM5.SA',   
'EMBR3.SA',   
'SMAL11.SA',   
'BPAC11.SA',   
'BEEF3.SA',   
'BRFS3.SA',   
'NATU3.SA',   
'RAIL3.SA',   
'WEGE3.SA',   
'BHIA3.SA',   
'ITSA4.SA',   
'SBSP3.SA',   
'IBOV11.SA',   
'BBSE3.SA',   
'GGBR4.SA',   
'RENT3.SA',   
'ELET3.SA',   
'USIM5.SA',   
'COGN3.SA',   
'LREN3.SA',   
'CSNA3.SA',   
'ABEV3.SA',   
'PETZ3.SA',   
'SUZB3.SA',   
'MRFG3.SA',   
'MRVE3.SA',   
'CYRE3.SA',   
'VBBR3.SA',   
'RADL3.SA',   
'CMIG4.SA',   
'HAPV3.SA',   
'ELET6.SA',   
'UGPA3.SA',   
'IRBR3.SA',   
'EQTL3.SA',   
'TAEE11.SA',   
'PETR3.SA',   
'KLBN11.SA',   
'GOAU4.SA',   
'EGIE3.SA',   
'BRAP4.SA',   
'AZZA3.SA',   
'BBDC3.SA',   
'SANB11.SA',   
'SIMH3.SA',   
'RDOR3.SA',   
'CXSE3.SA',   
'CSMG3.SA',   
'YDUQ3.SA',   
'CBAV3.SA',   
'MULT3.SA',   
'VAMO3.SA',   
'ALOS3.SA',   
'RANI3.SA',   
'HYPE3.SA',   
'CMIN3.SA',   
'ASAI3.SA',   
'FLRY3.SA',   
'CPLE6.SA',   
'NEOE3.SA',   
'JBSS32.SA',   
'MOTV3.SA',   
'CVCB3.SA',   
'AURE3.SA',   
'IGTI11.SA',   
'SMTO3.SA',   
'SAPR11.SA',   
'RECV3.SA',   
'ENEV3.SA',   
'LWSA3.SA',   
'JHSF3.SA',   
'ISAE4.SA',   
'ODPV3.SA',   
'VIVT3.SA',   
'ECOR3.SA',   
'LJQQ3.SA',   
'CASH3.SA',   
'ALPA4.SA',   
'DIRR3.SA',   
'PSSA3.SA',   
'MOVI3.SA',   
'INTB3.SA',   
'ANIM3.SA',   
'IFCM3.SA',   
'POMO4.SA',   
'TUPY3.SA',   
'TOTS3.SA',   
'HBOR3.SA',   
'CPFE3.SA',   
'TIMS3.SA',   
'EZTC3.SA',   
'QUAL3.SA',   
'ENGI1.SA',   
'BRSR6.SA',   
'ROXO3.SA',   
'RAPT4.SA',   
'SLCE3.SA',   
'CEAB3.SA',   
'VIVA3.SA',   
'DXCO3.SA',   
'LEVE3.SA',   
'MDIA3.SA',   
'VULC3.SA',   
'BMGB4.SA',   
'BPAN4.SA',   
'ALUP11.SA',   
'UNIP6.SA',   
'KEPL3.SA',   
'AMBP3.SA',   
'POSI3.SA',   
'XPBR31.SA',   
'ABCB4.SA',   
'SMFT3.SA',   
'TTEN3.SA',   
'GRND3.SA',   
'BOVV11.SA',   
'SBFG3.SA',   
'ROMI3.SA',   
'WIZC3.SA',   
'TEND3.SA',   
'CAML3.SA',   
'CURY3.SA',   
'NVDC34.SA',   
'VLID3.SA',   
'SEER3.SA',   
'GUAR3.SA',   
'TRIS3.SA',   
'TASA4.SA',   
'FESA4.SA',   
'GMAT3.SA',   
'MYPK3.SA',   
'INBR32.SA',   
'MILS3.SA',   
'JALL3.SA',   
'EVEN3.SA',   
'MLAS3.SA',   
'PNVL3.SA',   
'ARML3.SA',   
'IVVB11.SA',   
'GFSA3.SA',   
'MTRE3.SA',   
'AGRO3.SA',   
'BMOB3.SA',   
'CPLE3.SA',   
'SOJA3.SA',   
'ZAMP3.SA',   
'AURA33.SA',   
'GSGI11.SA',   
'TSLA34.SA',   
'ENJU3.SA',   
'ITUB3.SA',   
'MELI34.SA',   
'GOLL54.SA',   
'GOGL34.SA',   
'ONCO3.SA',   
'AERI3.SA',   
'CMIG3.SA',   
'GOLD11.SA',   
'AMAR3.SA',   
'GGPS3.SA',   
'BOVB11.SA',   
'PLPL3.SA',   
'LAVV3.SA',   
'TOKY3.SA',   
'ESPA3.SA',   
'DASA3.SA',   
'PTBL3.SA',   
'SEQL3.SA'
]

def get_target_date():
    """
    Obtém a data alvo para análise
    Se DATA_ANALISE estiver vazia, retorna a data atual
    """
    if DATA_ANALISE and DATA_ANALISE.strip():
        try:
            # Converte string para datetime
            target_date = datetime.strptime(DATA_ANALISE.strip(), '%Y-%m-%d')
            print(f"📅 Usando data configurada: {target_date.strftime('%d/%m/%Y')}")
            return target_date
        except ValueError as e:
            print(f"⚠️ Formato de data inválido '{DATA_ANALISE}'. Use formato YYYY-MM-DD")
            print(f"🔄 Usando data atual...")
            return datetime.now()
    else:
        print(f"📅 Usando data atual: {datetime.now().strftime('%d/%m/%Y')}")
        return datetime.now()

def get_historical_data_until_date(symbol, target_date, days_needed=300):
    """
    Obtém dados históricos até uma data específica
    """
    try:
        stock = yf.Ticker(symbol)
        
        # Calcula data inicial (precisa de mais dias para calcular as médias)
        start_date = target_date - timedelta(days=days_needed)
        end_date = target_date + timedelta(days=1)  # +1 para incluir a data alvo
        
        # Baixa dados históricos
        data = stock.history(start=start_date, end=end_date, interval='1d')
        
        if data.empty:
            return None
            
        # Filtra dados até a data alvo (inclusive)
        data = data[data.index.date <= target_date.date()]
        
        return data
        
    except Exception as e:
        print(f"Erro ao obter dados históricos para {symbol}: {e}")
        return None

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
            print(f"📏 Tamanho da mensagem: {len(text)} caracteres")
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

def calculate_moving_average(prices, period):
    """Calcula média móvel aritmética e tendência"""
    if len(prices) < period + 2:  # Precisa de pelo menos 2 pontos para calcular tendência
        return None, None
    
    try:
        ma = prices.rolling(window=period).mean()
        current_ma = ma.iloc[-1]
        previous_ma = ma.iloc[-2]
        
        # Calcula se a média está subindo ou descendo
        trend = "crescente" if current_ma > previous_ma else "decrescente"
        
        return round(current_ma, 2), trend
    except Exception:
        return None, None

def check_tendencia(prices, short_period, long_period):
    """Verifica a tendência baseada nas médias móveis"""
    if len(prices) < max(short_period, long_period) + 2:
        return None, None, None, None
    
    try:
        # Calcula médias atuais
        short_ma, short_trend = calculate_moving_average(prices, short_period)
        long_ma, long_trend = calculate_moving_average(prices, long_period)
        
        # Verifica posição relativa
        if short_ma is not None and long_ma is not None:
            if short_ma > long_ma:
                posicao = "curta_acima"
            elif short_ma < long_ma:
                posicao = "curta_abaixo"
            else:
                posicao = "iguais"
        else:
            posicao = None
            
        return short_ma, long_ma, short_trend, long_trend, posicao
        
    except Exception:
        return None, None, None, None, None

def get_rsi_data(symbol, target_date):
    """Obtém dados e calcula RSI para um ativo em uma data específica"""
    try:
        data = get_historical_data_until_date(symbol, target_date)
        
        if data is None or data.empty or len(data) < max(MM_PERIOD, MM_LONGA) + 2:
            return None
        
        rsi = calculate_rsi(data['Close'])
        price = data['Close'].iloc[-1]
        
        # Calcula variação (se tiver dados suficientes)
        if len(data) >= 2:
            variation = ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
        else:
            variation = 0
        
        # Calcula média móvel principal (dia atual)
        ma_value, ma_relative = calculate_moving_average(data['Close'], MM_PERIOD)
        
        # Calcula tendência das médias curta e longa
        short_ma, long_ma, short_trend, long_trend, posicao = check_tendencia(data['Close'], MM_CURTA, MM_LONGA)
        
        return {
            'symbol': symbol.replace('.SA', ''),
            'rsi': rsi,
            'price': price,
            'variation': variation,
            'date': data.index[-1].strftime('%d/%m/%Y'),
            'ma_value': ma_value,
            'ma_relative': ma_relative,
            'short_ma': short_ma,
            'long_ma': long_ma,
            'short_trend': short_trend,
            'long_trend': long_trend,
            'posicao_relativa': posicao
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
    """Verifica se é uma oportunidade de compra"""
    if data['ma_value'] is None:
        return False
    
    # Condição básica: RSI sobrevendido E preço acima da MM principal
    condicao_basica = data['rsi'] <= RSI_SOBREVENDIDO and data['price'] > data['ma_value']
    
    if not USAR_FILTRO_TENDENCIA:
        return condicao_basica
    
    # Condição de tendência: ambas as médias crescentes E curta acima da longa
    condicao_tendencia = (data['short_trend'] == "crescente" and 
                         data['long_trend'] == "crescente" and
                         data['posicao_relativa'] == "curta_acima")
    
    return condicao_basica and condicao_tendencia

def is_venda_opportunity(data):
    """Verifica se é uma oportunidade de venda"""
    if data['ma_value'] is None:
        return False
    
    # Condição básica: RSI sobrecomprado E preço abaixo da MM principal
    condicao_basica = data['rsi'] >= RSI_SOBRECOMPRADO and data['price'] < data['ma_value']
    
    if not USAR_FILTRO_TENDENCIA:
        return condicao_basica
    
    # Condição de tendência: ambas as médias decrescentes E curta abaixo da longa
    condicao_tendencia = (data['short_trend'] == "decrescente" and 
                         data['long_trend'] == "decrescente" and
                         data['posicao_relativa'] == "curta_abaixo")
    
    return condicao_basica and condicao_tendencia

def run_analysis():
    """
    Executa análise de RSI e envia para Telegram
    """
    target_date = get_target_date()
    
    print("📄 Iniciando análise de RSI...")
    print(f"📅 Data da análise: {target_date.strftime('%d/%m/%Y')}")
    print(f"🎯 Filtro tendência: {'ATIVO' if USAR_FILTRO_TENDENCIA else 'DESATIVADO'}")
    print(f"📊 Médias: {MM_CURTA}/{MM_LONGA} períodos")
    print("=" * 80)
    
    results = []
    
    for symbol in ATIVOS:
        print(f"Processando {symbol}...", end=" ")
        
        data = get_rsi_data(symbol, target_date)
        if data is None:
            print("❌ ERRO")
            continue
        
        signal, color = format_signal(data['rsi'])
        results.append(data)
        
        mm_info = f" | MM{MM_PERIOD}: R${data['ma_value']:.2f}" if data['ma_value'] is not None else " | MM: N/A"
        
        # Mostrar ambas as médias curta e longa
        if data['short_ma'] is not None and data['long_ma'] is not None:
            posicao = "↑" if data['posicao_relativa'] == "curta_acima" else "↓" if data['posicao_relativa'] == "curta_abaixo" else "="
            trend_info = f" | MM{MM_CURTA}: R${data['short_ma']:.2f} ({data['short_trend'][0]}) {posicao} MM{MM_LONGA}: R${data['long_ma']:.2f} ({data['long_trend'][0]})"
        else:
            trend_info = " | Dados insuficientes para tendência"
            
        print(f"✅ | RSI: {data['rsi']} ({signal}) | Preço: R${data['price']:.2f}{mm_info}{trend_info}")
    
    print("\n" + "=" * 80)
    print("📊 RESUMO DA ANÁLISE")
    print("=" * 80)
    
    if results:
        results.sort(key=lambda x: x['rsi'])
        
        print(f"\n📈 TODOS OS ATIVOS ANALISADOS ({len(results)}):")
        print("-" * 80)
        
        for data in results:
            signal, color = format_signal(data['rsi'])
            mm_info = f" | MM{MM_PERIOD}: R${data['ma_value']:.2f}" if data['ma_value'] is not None else " | MM: N/A"
            
            # Mostrar ambas as médias curta e longa no resumo
            if data['short_ma'] is not None and data['long_ma'] is not None:
                posicao = "↑" if data['posicao_relativa'] == "curta_acima" else "↓" if data['posicao_relativa'] == "curta_abaixo" else "="
                trend_info = f" | MM{MM_CURTA}: R${data['short_ma']:.2f} {posicao} MM{MM_LONGA}: R${data['long_ma']:.2f}"
            else:
                trend_info = " | Dados insuficientes"
                
            print(f"{color} {data['symbol']}: RSI {data['rsi']} | {signal} | Preço: R${data['price']:.2f}{mm_info}{trend_info}")
        
        # Oportunidades de compra
        compras = [r for r in results if is_compra_opportunity(r)]
        if compras:
            print(f"\n🟢 OPORTUNIDADES DE COMPRA ({len(compras)}):")
            condicao = f"RSI ≤ {RSI_SOBREVENDIDO} + Preço > MM{MM_PERIOD}"
            if USAR_FILTRO_TENDENCIA:
                condicao += f" + MM{MM_CURTA}↑ > MM{MM_LONGA}↑ (ambas crescentes)"
            print(f"   ({condicao})")
            for r in sorted(compras, key=lambda x: x['rsi']):
                trend_info = f" | MM{MM_CURTA}: R${r['short_ma']:.2f} ({r['short_trend']}), MM{MM_LONGA}: R${r['long_ma']:.2f} ({r['long_trend']})" if USAR_FILTRO_TENDENCIA else ""
                print(f"   • {r['symbol']}: RSI {r['rsi']} - Preço: R${r['price']:.2f}{trend_info}")
        else:
            print(f"\nℹ️  SEM OPORTUNIDADES DE COMPRA")
            condicao = f"RSI ≤ {RSI_SOBREVENDIDO} + Preço > MM{MM_PERIOD}"
            if USAR_FILTRO_TENDENCIA:
                condicao += f" + MM{MM_CURTA}↑ > MM{MM_LONGA}↑ (ambas crescentes)"
            print(f"   ({condicao})")
        
        # Oportunidades de venda
        vendas = [r for r in results if is_venda_opportunity(r)]
        if vendas:
            print(f"\n🔴 OPORTUNIDADES DE VENDA ({len(vendas)}):")
            condicao = f"RSI ≥ {RSI_SOBRECOMPRADO} + Preço < MM{MM_PERIOD}"
            if USAR_FILTRO_TENDENCIA:
                condicao += f" + MM{MM_CURTA}↓ < MM{MM_LONGA}↓ (ambas decrescentes)"
            print(f"   ({condicao})")
            for r in sorted(vendas, key=lambda x: x['rsi'], reverse=True):
                trend_info = f" | MM{MM_CURTA}: R${r['short_ma']:.2f} ({r['short_trend']}), MM{MM_LONGA}: R${r['long_ma']:.2f} ({r['long_trend']})" if USAR_FILTRO_TENDENCIA else ""
                print(f"   • {r['symbol']}: RSI {r['rsi']} - Preço: R${r['price']:.2f}{trend_info}")
        else:
            print(f"\nℹ️  SEM OPORTUNIDADES DE VENDA")
            condicao = f"RSI ≥ {RSI_SOBRECOMPRADO} + Preço < MM{MM_PERIOD}"
            if USAR_FILTRO_TENDENCIA:
                condicao += f" + MM{MM_CURTA}↓ < MM{MM_LONGA}↓ (ambas decrescentes)"
            print(f"   ({condicao})")
    
    # Estatísticas gerais
    if results:
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   • Total analisado: {len(results)}")
        
        avg_rsi = sum(r['rsi'] for r in results) / len(results)
        print(f"   • RSI médio: {avg_rsi:.1f}")
    
    # Enviar para Telegram
    send_telegram_summary(results, target_date)
    
    print(f"\n⏰ Análise concluída às {datetime.now().strftime('%H:%M:%S')}")

def send_telegram_summary(results, target_date):
    """Envia resumo para o Telegram"""
    try:
        bot = TelegramBot(BOT_TOKEN, CHAT_ID)
        
        # Mensagem sem formatação nenhuma - texto puro
        message = f"ANÁLISE DE RSI - {target_date.strftime('%d/%m/%Y')} (executada em {datetime.now().strftime('%d/%m/%Y %H:%M')})\n\n"
        message += f"CONFIGURAÇÕES:\n"
        message += f"• RSI{RSI_PERIOD}: ≥{RSI_SOBRECOMPRADO} (sobrecomprado) | ≤{RSI_SOBREVENDIDO} (sobrevendido)\n"
        message += f"• MM{MM_PERIOD} como referência principal\n"
        if USAR_FILTRO_TENDENCIA:
            message += f"• Filtro tendência: MM{MM_CURTA}/{MM_LONGA} períodos\n"
        message += f"• Total analisado: {len(results)}\n\n"
        
        # Oportunidades de compra
        compras = [r for r in results if is_compra_opportunity(r)]
        if compras:
            message += f"🟢 OPORTUNIDADES DE COMPRA ({len(compras)}):\n"
            for r in sorted(compras, key=lambda x: x['rsi']):
                trend_info = f" | MM{MM_CURTA}: R${r['short_ma']:.2f} ({r['short_trend']}), MM{MM_LONGA}: R${r['long_ma']:.2f} ({r['long_trend']})" if USAR_FILTRO_TENDENCIA else ""
                message += f"• {r['symbol']}: RSI {r['rsi']} - R${r['price']:.2f}{trend_info}\n"
            message += "\n"
        else:
            message += f"ℹ️ SEM OPORTUNIDADES DE COMPRA\n\n"
        
        # Oportunidades de venda
        vendas = [r for r in results if is_venda_opportunity(r)]
        if vendas:
            message += f"🔴 OPORTUNIDADES DE VENDA ({len(vendas)}):\n"
            for r in sorted(vendas, key=lambda x: x['rsi'], reverse=True):
                trend_info = f" | MM{MM_CURTA}: R${r['short_ma']:.2f} ({r['short_trend']}), MM{MM_LONGA}: R${r['long_ma']:.2f} ({r['long_trend']})" if USAR_FILTRO_TENDENCIA else ""
                message += f"• {r['symbol']}: RSI {r['rsi']} - R${r['price']:.2f}{trend_info}\n"
            message += "\n"
        else:
            message += f"ℹ️ SEM OPORTUNIDADES DE VENDA\n\n"
        
        message += f"Análise executada para {target_date.strftime('%d/%m/%Y')}"
        
        print(f"📤 Preparando para enviar mensagem para Telegram...")
        print(f"📏 Tamanho da mensagem: {len(message)} caracteres")
        
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
    target_date = get_target_date()
    
    print("🤖 Monitor de RSI para Telegram")
    print(f"📅 Data da análise: {target_date.strftime('%d/%m/%Y')}")
    print(f"📊 MM{MM_PERIOD} como referência principal")
    if USAR_FILTRO_TENDENCIA:
        print(f"📈 Filtro tendência: MM{MM_CURTA}/{MM_LONGA} períodos")
    print(f"📈 RSI{RSI_PERIOD}: ≥{RSI_SOBRECOMPRADO} (sobrecomprado) | ≤{RSI_SOBREVENDIDO} (sobrevendido)")
    print("=" * 80)
    
    # Executar análise
    run_analysis()

if __name__ == "__main__":
    main()