from abc import ABC, abstractmethod


class BaseCrawler(ABC):

    @abstractmethod
    def start(self):
        pass
