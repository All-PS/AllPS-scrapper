from app.notification.BaseNotification import BaseNotification

class ConsoleNotification(BaseNotification):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConsoleNotification, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def alert(self, message):
        print(message)
