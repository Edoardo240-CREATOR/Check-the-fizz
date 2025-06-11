from flask import Flask
from threading import Thread
import requests
from bs4 import BeautifulSoup
import time
import smtplib
from email.message import EmailMessage
import telegram
import os
app = Flask('')

@app.route('/')
def home():
    return "Fizz monitor attivo!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
    
# --- CONFIGURAZIONE ---

URL = "https://www.the-fizz.com/en/student-accommodation/utrecht/#apartment"

CHECK_INTERVAL = 600  # ogni quanti secondi fare il controllo (es. 600s = 10 minuti)

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "edomonte2001@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

KEYWORDS = ["Single Studio", "Single", "Available", "Now"]

# --- FUNZIONI ---

def check_availability():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text()
    return any(keyword.lower() in text.lower() for keyword in KEYWORDS)

def send_email():
    msg = EmailMessage()
    msg["Subject"] = "🚨 Disponibilità camera The Fizz Utrecht!"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS
    msg.set_content(f"Controlla subito la disponibilità su {URL}")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

def send_telegram():
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    message = f"🚨 Camera disponibile su THE FIZZ Utrecht! \nVai qui: {URL}"
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

# --- LOOP PRINCIPALE ---

keep_alive()
print("🟢 Avviato il monitoraggio di THE FIZZ Utrecht...")

while True:
    try:
        if check_availability():
            print("✅ CAMERA TROVATA! Invio notifiche...")
            send_email()
            send_telegram()
            time.sleep(3600)  # aspetta 1 ora dopo aver trovato disponibilità
        else:
            print("❌ Nessuna disponibilità trovata.")
            time.sleep(CHECK_INTERVAL)  # aspetta prima del prossimo controllo
    except Exception as e:
        print(f"Errore: {e}")
        time.sleep(CHECK_INTERVAL)

