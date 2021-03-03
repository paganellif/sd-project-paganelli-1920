import os
from abc import ABC, abstractmethod
from WSN.datastreamer import DataStreamerImpl

class SensorStreamer(ABC):
    pass

class FFDSensorStreamer(SensorStreamer):
    def __init__(self):
        self.__root_dir = os.path.dirname(os.path.abspath(__file__))
        self.__data_streamer1 = DataStreamerImpl(self.__root_dir+"/../res/testset.csv")
        self.__data_streamer2 = DataStreamerImpl(self.__root_dir+"/../res/forestfires.csv")
        self.__data_streamer3 = DataStreamerImpl(self.__root_dir+"/../res/flamesensor2.csv")

    def get_temp(self):
        return float(self.__data_streamer1.get_rand_value(' _tempm'))

    def get_hum(self):
        return float(self.__data_streamer1.get_rand_value(' _hum'))

    def get_wind(self):
        return float(self.__data_streamer2.get_rand_value('wind'))

    def get_flame(self):
        return bool(self.__data_streamer3.get_rand_value('flame'))


class SensorStreamerAbstractFactory(ABC):
    @abstractmethod
    def create_sensor_streamer(self) -> SensorStreamer:
        pass


class SensorStreamerFactory(SensorStreamerAbstractFactory):

    def create_sensor_streamer(self) -> FFDSensorStreamer:
        return FFDSensorStreamer()
