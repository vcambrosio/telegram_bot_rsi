import requests

BOT_TOKEN = '8341816244:AAE6GOR8-GZ2wDtt_MU1Fcq7bfo5TQNvLjg'
response = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates')
print(response.json())

