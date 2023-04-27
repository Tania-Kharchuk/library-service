import requests

from library_service import settings

BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
CHAT_ID = settings.TELEGRAM_CHAT_ID


def send_telegram_notification(
    message: str,
):
    requests.post(URL, json={"chat_id": CHAT_ID, "text": message})
