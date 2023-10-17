from slack_sdk import WebClient

from app.settings import ALLPS_SLACK_TOKEN, ALLPS_SLACK_CHANNEL


class SlackBot:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance = WebClient(token=ALLPS_SLACK_TOKEN)
        return cls._instance

    @classmethod
    def alert(self, message):
        if not self._instance:
            SlackBot()
        self._instance.chat_postMessage(channel=ALLPS_SLACK_CHANNEL, text=message)