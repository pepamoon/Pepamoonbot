import os
import requests
from telegram import Bot

# Variabili ambiente
TELEGRAM_TOKEN = os.environ.get("TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("CHAT_ID")
WALLET_ADDRESS = os.environ.get("WALLET_ADDRESS")

TOKEN_NAME = "PEA"
PEA_PER_SOL = 2250
IMAGE_URL = "https://i.ibb.co/7xzJ45FY/D4-FE695-E-5-BE0-4-CB0-A9-AB-E4-EAC5-F54853.png"

bot = Bot(token=TELEGRAM_TOKEN)

def get_sol_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
    try:
        response = requests.get(url)
        if response.ok:
            return response.json()["solana"]["usd"]
    except:
        pass
    return 0

def fetch_transactions(wallet_address):
    url = f"https://public-api.solscan.io/account/transactions?account={wallet_address}&limit=1"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.ok:
        return response.json()
    return []

def is_incoming_sol(tx, wallet_address):
    for instr in tx.get("parsedInstruction", []):
        if instr.get("type") == "transfer" and instr.get("destination") == wallet_address:
            return instr.get("lamports", 0) / 1e9
    return 0

def format_message(sol_received, signature, usd_value, tokens):
    tx_link = f"https://solscan.io/tx/{signature}"
    return (
        "🚨 <b>BUY ALERT</b> 🚨\n"
        f"💰 Spesa: <b>{sol_received:.4f} SOL</b>\n"
        f"💸 Valore: <b>${usd_value}</b>\n"
        f"🐸 Ricevuti: <b>{tokens} {TOKEN_NAME}</b>\n"
        f"🔗 <a href=\"{tx_link}\">Visualizza Transazione</a>\n"
    )

def main():
    txs = fetch_transactions(WALLET_ADDRESS)
    if not txs:
        return

    latest_tx = txs[0]
    signature = latest_tx.get("signature")
    sol_received = is_incoming_sol(latest_tx, WALLET_ADDRESS)
    
    # File locale per evitare doppia notifica
    if os.path.exists("last.txt"):
        with open("last.txt") as f:
            last_sig = f.read().strip()
            if last_sig == signature:
                return
    
    if sol_received > 0:
        sol_price = get_sol_price()
        usd_value = round(sol_received * sol_price, 2)
        tokens = round(sol_received * PEA_PER_SOL, 2)
        message = format_message(sol_received, signature, usd_value, tokens)

        bot.send_photo(
            chat_id=TELEGRAM_CHAT_ID,
            photo=IMAGE_URL,
            caption=message,
            parse_mode="HTML"
        )

        # Salva ultima signature
        with open("last.txt", "w") as f:
            f.write(signature)

main()
