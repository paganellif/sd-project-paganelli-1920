from abc import ABC, abstractmethod
import pandas as pd
import random as rd


class DataStreamer(ABC):
    @abstractmethod
    def get_rand_value(self, header: str) -> object:
        pass

    @abstractmethod
    def get_value(self, header: str, index: int) -> object:
        pass


class DataStreamerImpl(DataStreamer):
    def __init__(self, csv_file_path: str):
        self.__csv_file = pd.read_csv(csv_file_path)
        self.__n_rows = len(self.__csv_file.index)
        self.__header_list = self.__csv_file.columns.values

    def get_rand_value(self, header: str) -> object:
        if header in self.__header_list:
            return self.__csv_file[header][rd.randrange(self.__n_rows)]

    def get_value(self, header: str, index: int) -> object:
        if header in self.__header_list:
            if 0 <= index < self.__n_rows:
                return self.__csv_file[header][index]
