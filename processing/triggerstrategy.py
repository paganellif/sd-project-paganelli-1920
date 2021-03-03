from abc import ABC, abstractmethod


class TriggerStrategy(ABC):
    @abstractmethod
    def check_event_detections(self, behaviour) -> bool:
        pass
