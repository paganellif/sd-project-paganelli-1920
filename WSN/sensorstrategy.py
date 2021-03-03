from abc import ABC, abstractmethod


class SensorStrategy(ABC):
    @abstractmethod
    def read_sensor_values(self) -> dict:
        pass


class ActuatorStrategy(ABC):
    @abstractmethod
    def perform_action(self, behaviour) -> None:
        pass


class SpreadingStrategy(ABC):
    @abstractmethod
    def spreading(self, behaviour, information: str) -> bool:
        pass

