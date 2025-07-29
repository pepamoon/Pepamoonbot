import requests
import os

# Prende i valori dai secrets di GitHub
TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# Messaggio di test
message = "✅ Il bot è attivo e funziona correttamente da GitHub Actions!"

# URL per l'API Telegram
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": message
}

# Invia il messaggio
response = requests.post(url, data=payload)

# Opzionale: stampa esito nel log GitHub Actions
print("Risposta Telegram:", response.text)
