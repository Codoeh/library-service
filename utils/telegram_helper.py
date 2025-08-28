import os
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

class TelegramClient:
    def __init__(
            self,
            bot_token: str = None,
            chat_id: str = None
    ):
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")

    def send_message(
            self,
            text: str,
            parse_mode: str="Markdown"
    ) -> bool:
        if not self.bot_token or not self.chat_id:
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode
        }

        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
        except Exception as e:
            print(f"Telegram send failed: {e}")

default_client = TelegramClient()

def send_telegram_message(text: str):
    return default_client.send_message(text)