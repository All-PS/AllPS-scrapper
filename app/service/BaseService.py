from abc import ABC, abstractmethod


class BaseService(ABC):
    PLATFORM_NAME = None
    PLATFORM_URL = None

    @abstractmethod
    def saveProblem(self, problemDto):
        pass
