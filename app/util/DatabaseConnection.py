import MySQLdb

from app import settings


class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance = MySQLdb.connect(
                **settings.DATABASES
            )
        return cls._instance

    @classmethod
    def startTransaction(self):
        if not self._instance:
            DatabaseConnection()
        self._instance.cursor().execute("START TRANSACTION")

    @classmethod
    def commitTransaction(self):
        if not self._instance:
            DatabaseConnection()
        self._instance.commit()
        self._instance.cursor().close()

    # def rollbackTransaction(self):
    #     if not self._instance:
    #         self._instance.rollback()