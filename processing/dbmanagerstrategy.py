from abc import ABC, abstractmethod


class DBManagerStrategy(ABC):
    @abstractmethod
    def check_values(self, values: dict) -> bool:
        pass
