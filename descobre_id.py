import requests
import yfinance as yf
from datetime import datetime

class TelegramTester:
    """Classe para testar configuração do Telegram Bot"""
    
    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def test_bot_token(self):
        """Testa se o token do bot é válido"""
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url)
            data = response.json()
            
            if data.get('ok'):
                bot_info = data['result']
                print("✅ Token do bot é válido!")
                print(f"   Nome: {bot_info.get('first_name', 'N/A')}")
                print(f"   Username: @{bot_info.get('username', 'N/A')}")
                print(f"   ID: {bot_info.get('id', 'N/A')}")
                return True
            else:
                print("❌ Token do bot inválido!")
                print(f"   Erro: {data.get('description', 'Erro desconhecido')}")
                return False
        except Exception as e:
            print(f"❌ Erro ao testar token: {e}")
            return False
    
    def get_chat_id(self):
        """Obtém o chat_id das mensagens recebidas"""
        try:
            url = f"{self.base_url}/getUpdates"
            response = requests.get(url)
            data = response.json()
            
            if data.get('ok') and data.get('result'):
                print("📬 Mensagens encontradas:")
                chat_ids = set()
                
                for update in data['result']:
                    if 'message' in update:
                        message = update['message']
                        chat_id = message['chat']['id']
                        chat_ids.add(chat_id)
                        
                        user_info = message.get('from', {})
                        text = message.get('text', 'N/A')
                        
                        print(f"   Chat ID: {chat_id}")
                        print(f"   Nome: {user_info.get('first_name', 'N/A')} {user_info.get('last_name', '')}")
                        print(f"   Username: @{user_info.get('username', 'N/A')}")
                        print(f"   Mensagem: {text}")
                        print("   " + "="*40)
                
                if chat_ids:
                    print(f"\n🎯 Chat IDs únicos encontrados: {list(chat_ids)}")
                    return list(chat_ids)
                else:
                    print("❌ Nenhum chat_id encontrado")
                    return []
            else:
                print("❌ Nenhuma mensagem encontrada")
                print("💡 Envie uma mensagem para o bot primeiro!")
                return []
        except Exception as e:
            print(f"❌ Erro ao buscar chat_id: {e}")
            return []
    
    def send_test_message(self, chat_id, message="🧪 Teste de conexão!"):
        """Envia mensagem de teste"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, data=data)
            result = response.json()
            
            if result.get('ok'):
                print(f"✅ Mensagem enviada com sucesso para {chat_id}")
                return True
            else:
                print(f"❌ Erro ao enviar mensagem: {result.get('description')}")
                return False
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem: {e}")
            return False

class SimpleBovespaBot:
    """Bot simplificado para monitorar ações"""
    
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, text):
        """Envia mensagem via Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, data=data)
            return response.json().get('ok', False)
        except:
            return False
    
    def get_stock_info(self, symbol):
        """Busca informações da ação"""
        try:
            if not symbol.endswith('.SA'):
                symbol += '.SA'
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='5d')
            
            if data.empty:
                return None
            
            current_price = data['Close'].iloc[-1]
            previous_price = data['Close'].iloc[-2] if len(data) > 1 else current_price
            change = current_price - previous_price
            change_percent = (change / previous_price) * 100
            
            # Volume médio
            avg_volume = data['Volume'].mean()
            current_volume = data['Volume'].iloc[-1]
            
            return {
                'symbol': symbol.replace('.SA', ''),
                'current_price': current_price,
                'change': change,
                'change_percent': change_percent,
                'volume_ratio': current_volume / avg_volume if avg_volume > 0 else 1
            }
        except:
            return None
    
    def format_stock_message(self, stock_info):
        """Formata mensagem da ação"""
        if not stock_info:
            return "❌ Erro ao obter dados da ação"
        
        emoji = "🟢" if stock_info['change_percent'] > 0 else "🔴" if stock_info['change_percent'] < 0 else "⚪"
        
        message = f"""
{emoji} <b>{stock_info['symbol']}</b>
💰 Preço: R$ {stock_info['current_price']:.2f}
📊 Variação: {stock_info['change']:+.2f} ({stock_info['change_percent']:+.2f}%)
📈 Volume: {stock_info['volume_ratio']:.1f}x média

⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}
        """.strip()
        
        return message
    
    def monitor_stock(self, symbol):
        """Monitora uma ação e envia alerta se necessário"""
        stock_info = self.get_stock_info(symbol)
        
        if stock_info:
            # Envia alerta se variação > 2% ou volume > 2x média
            if abs(stock_info['change_percent']) > 2 or stock_info['volume_ratio'] > 2:
                message = self.format_stock_message(stock_info)
                return self.send_message(message)
        
        return False

def main():
    """Função principal para configurar e testar"""
    
    print("🤖 CONFIGURAÇÃO E TESTE DO TELEGRAM BOT")
    print("="*50)
    
    # COLOQUE SEU TOKEN AQUI
    BOT_TOKEN = "8341816244:AAE6GOR8-GZ2wDtt_MU1Fcq7bfo5TQNvLjg"  # ⬅️ ALTERE AQUI!
    
    if BOT_TOKEN == "SEU_TOKEN_AQUI":
        print("❌ Você precisa configurar o BOT_TOKEN!")
        print("💡 Procure por: BOT_TOKEN = \"SEU_TOKEN_AQUI\"")
        print("💡 E substitua pelo token real do seu bot")
        return
    
    # Testa configuração
    tester = TelegramTester(BOT_TOKEN)
    
    print("\n1️⃣ TESTANDO TOKEN DO BOT...")
    if not tester.test_bot_token():
        print("❌ Configure o token corretamente!")
        return
    
    print("\n2️⃣ BUSCANDO CHAT_ID...")
    chat_ids = tester.get_chat_id()
    
    if not chat_ids:
        print("💡 Envie uma mensagem para o bot e execute novamente!")
        return
    
    # Usa o primeiro chat_id encontrado
    CHAT_ID = chat_ids[0]
    print(f"\n3️⃣ USANDO CHAT_ID: {CHAT_ID}")
    
    # Teste de envio
    print("\n4️⃣ TESTANDO ENVIO DE MENSAGEM...")
    if tester.send_test_message(CHAT_ID):
        print("✅ Configuração OK!")
        
        # Teste com ação real
        print("\n5️⃣ TESTANDO COM AÇÃO REAL...")
        bot = SimpleBovespaBot(BOT_TOKEN, CHAT_ID)
        stock_info = bot.get_stock_info("PETR4")
        
        if stock_info:
            message = bot.format_stock_message(stock_info)
            if bot.send_message(message):
                print("✅ Teste com PETR4 enviado!")
            else:
                print("❌ Erro ao enviar teste da ação")
        else:
            print("❌ Erro ao buscar dados da PETR4")
    else:
        print("❌ Erro no teste de envio!")

def quick_stock_check():
    """Função rápida para verificar algumas ações"""
    
    # SUAS CONFIGURAÇÕES
    BOT_TOKEN = "8341816244:AAE6GOR8-GZ2wDtt_MU1Fcq7bfo5TQNvLjg"  # ⬅️ ALTERE AQUI!
    CHAT_ID = "18037748"          # Seu chat_id já descoberto
    
    if BOT_TOKEN == "8341816244:AAE6GOR8-GZ2wDtt_MU1Fcq7bfo5TQNvLjg":
        print("✅ Token configurado! Executando...")
    
    stocks = ["PETR4", "VALE3", "ITUB4", "BBDC4", "MGLU3"]
    bot = SimpleBovespaBot(BOT_TOKEN, CHAT_ID)
    
    print("📊 Enviando relatório de ações...")
    
    for stock in stocks:
        stock_info = bot.get_stock_info(stock)
        if stock_info:
            message = bot.format_stock_message(stock_info)
            if bot.send_message(message):
                print(f"✅ {stock} enviado")
            else:
                print(f"❌ Erro ao enviar {stock}")
        else:
            print(f"❌ Erro ao buscar dados de {stock}")

if __name__ == "__main__":
    # Descomente a função que deseja usar:
    
    # Para configurar e testar tudo
    main()
    
    # Para enviar relatório rápido (após configurar)
    # quick_stock_check()