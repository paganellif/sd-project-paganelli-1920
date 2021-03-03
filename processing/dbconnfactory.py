from processing.dbconnectorimpl import *
from util.xmpp_utils import HOSTNAME
from util.db_utils import Databases


class DBConnAbstractFactory(ABC):
    @abstractmethod
    def create_manager_db_connector(self) -> DBManagerConnector:
        pass

    @abstractmethod
    def create_trigger_db_connector(self) -> DBTriggerConnector:
        pass

    @abstractmethod
    def create_statistics_db_connector(self) -> DBStatisticsConnector:
        pass

    @abstractmethod
    def create_front_end_db_connector(self) -> DBFrontEndConnector:
        pass


class DBConnFactory(DBConnAbstractFactory):
    def __init__(self):
        self.__db_name = Databases.test_db.value
        self.__hostname = HOSTNAME
        self.__port = 27017

    def create_manager_db_connector(self) -> DBManagerConnector:
        return DBManagerConnectorImpl(self.__hostname, self.__port, self.__db_name)

    def create_trigger_db_connector(self) -> DBTriggerConnector:
        return DBTriggerConnectorImpl(self.__hostname, self.__port, self.__db_name)

    def create_statistics_db_connector(self) -> DBStatisticsConnector:
        return DBStatisticsConnectorImpl(self.__hostname, self.__port, self.__db_name)

    def create_front_end_db_connector(self) -> DBFrontEndConnector:
        return DBFrontEndConnectorImpl(self.__hostname, self.__port, self.__db_name)
