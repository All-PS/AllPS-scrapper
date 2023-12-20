from slack_sdk import WebClient
from app.settings import ALLPS_SLACK_TOKEN, ALLPS_SLACK_CHANNEL
from app.notification.BaseNotification import BaseNotification

class SlackNotification(BaseNotification):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SlackNotification, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'is_initialized'):
            self.client = WebClient(token=ALLPS_SLACK_TOKEN)
            self.is_initialized = True

    def alert(self, message):
        self.client.chat_postMessage(channel=ALLPS_SLACK_CHANNEL, text=message)
