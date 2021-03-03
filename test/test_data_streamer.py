import os

from WSN.datastreamer import DataStreamerImpl, DataStreamer
import unittest


class DataStreamerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.__root_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_streamer = DataStreamerImpl(self.__root_dir+"/../res/testset.csv")

    def test_initial_data_streamer(self):
        self.assertIsNotNone(self.data_streamer)
        self.assertIsInstance(self.data_streamer, DataStreamer)

    def test_get_random_value(self):
        value = self.data_streamer.get_rand_value('datetime_utc')
        self.assertIsNotNone(value)

    def test_get_random_value_with_fake_header(self):
        value = self.data_streamer.get_rand_value('fake_header')
        self.assertIsNone(value)

    def test_get_index_value(self):
        value = self.data_streamer.get_value('datetime_utc', 0)
        self.assertEqual(value, '19961101-11:00')

    def test_get_index_value_with_invalid_index(self):
        value = self.data_streamer.get_value('datetime_utc', -1)
        self.assertIsNone(value)

    def test_get_index_value_with_fake_header(self):
        value = self.data_streamer.get_value('fake_header', 0)
        self.assertIsNone(value)
