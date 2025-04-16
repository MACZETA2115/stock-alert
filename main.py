import yfinance as yf
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import os
import traceback

EMAIL_ADDRESS = os.getenv("EMAIL_USER")  # e.g. akcjealert69@gmail.com
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")  # hasło aplikacji Gmail

# Spółki z S&P 500 i FTSE 100 – dodaj więcej wedle uznania
TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "BRK-B",
    "JNJ", "V", "NVDA", "BP.L", "HSBA.L", "RDSA.L"
]

ALERTED = set()  # Żeby nie wysyłać tego samego alertu w kółko

def get_percent_change(ticker):
    data = yf.download(ticker, period="5d", interval="1d")
    if data.shape[0] < 2:
        return None
    yesterday = data['Close'].iloc[-2]
    today = data['Close'].iloc[-1]
    return float(((today - yesterday) / yesterday) * 100)

def send_email(ticker, percent):
    try:
        data = yf.Ticker(ticker).info
        name = data.get("longName", ticker)
        sector = data.get("sector", "Nieznany")
        summary = data.get("longBusinessSummary", "")
        link = f"https://finance.yahoo.com/quote/{ticker}"

        subject = f"📉 {ticker} spadł o {percent:.2f}%"
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_ADDRESS
        msg["Subject"] = subject

        body = f"""
        <h2>{name} ({ticker})</h2>
        <p><strong>Spadek:</strong> {percent:.2f}%</p>
        <p><strong>Sektor:</strong> {sector}</p>
        <p><strong>Opis:</strong> {summary[:500]}...</p>
        <p><a href="{link}">🔗 Zobacz na Yahoo Finance</a></p>
        """

        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print(f"📨 Wysłano alert dla {ticker}")
    except Exception as e:
        print(f"❌ Błąd przy wysyłaniu alertu: {ticker}")
        traceback.print_exc()

def monitor():
    print("🔎 Sprawdzam spółki...")
    for ticker in TICKERS:
        try:
            change = get_percent_change(ticker)
            if change is not None and change <= -5 and ticker not in ALERTED:
                send_email(ticker, change)
                ALERTED.add(ticker)
        except Exception as e:
            print(f"❌ Błąd przy sprawdzaniu {ticker}: {e}")

print("🚨 Monitoring aktywny. Sprawdzam co 5 minut...")

while True:
    monitor()
    time.sleep(300)  # 5 minut
