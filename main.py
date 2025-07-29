import os
import requests
from telegram import Bot

# Variabili di ambiente (saranno fornite da GitHub Secrets)
TELEGRAM_TOKEN = os.environ.get("TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("CHAT_ID")
WALLET_ADDRESS = os.environ.get("WALLET_ADDRESS")

TOKEN_NAME = "PEA"
PEA_PER_SOL = 2250
IMAGE_URL = "https://i.ibb.co/S36RGCS/pepamoon-buy-alert.png"  # modifica con il tuo link reale

bot = Bot(token=TELEGRAM_TOKEN)

def get_sol_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
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

def notify_buy():
    txs = fetch_transactions(WALLET_ADDRESS)
    if not txs:
        return

    latest_tx = txs[0]
    signature = latest_tx.get("signature")
    sol_received = is_incoming_sol(latest_tx, WALLET_ADDRESS)

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

# Esegui una sola volta (ideale per GitHub Actions)
notify_buy()
