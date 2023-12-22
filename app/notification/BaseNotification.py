class BaseNotification:

    def alert(self, message):
        raise NotImplementedError("Subclasses should implement this method")
