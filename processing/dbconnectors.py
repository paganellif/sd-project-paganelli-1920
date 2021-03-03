from abc import ABC, abstractmethod
from bson import ObjectId
from pymongo.collection import Collection
from pymongo.cursor import Cursor


class DBManagerConnector(ABC):
    @abstractmethod
    def insert_sensor_value(self, agent_jid: str, data: dict, db_coll: str) -> ObjectId:
        pass

    @abstractmethod
    def get_collection(self, db_coll: str) -> Collection:
        pass

    @abstractmethod
    def check_collection(self, db_coll: str) -> bool:
        pass


class DBTriggerConnector(ABC):
    @abstractmethod
    def select_last_detections(self, agent_jid: str, limit: int, db_coll: str) -> Cursor:
        pass

    @abstractmethod
    def insert_event_detection(self, agent_jid: str, id_reference: dict, db_coll: str) -> ObjectId:
        pass

    @abstractmethod
    def insert_error_report(self, agent_jid: str, description: str, db_coll: str) -> ObjectId:
        pass

    @abstractmethod
    def insert_actuator_triggered(self, agent_jid: str, db_coll: str) -> ObjectId:
        pass

    @abstractmethod
    def check_limit(self, limit: int) -> bool:
        pass


class DBStatisticsConnector(ABC):
    @abstractmethod
    def insert_aggregation(self, agent_jid: str, stats_coll: str, sensor_values_coll: str, keys: list) -> ObjectId:
        pass


class DBFrontEndConnector(ABC):
    @abstractmethod
    def select_distinct_agents_jid(self, db_coll: str) -> list:
        pass

    @abstractmethod
    def select_last_statistics(self, agent_jid: str, limit: int, db_coll: str) -> Cursor:
        pass
