import asyncio

import pytest
from aioxmpp import JID

from WSN.ffdsensoragent import FFDSensorAgent
from processing.statisticsagent import StatisticsAgent
from test.utilities import BaseAgentTestCase
from util.db_utils import Collections
from util.xmpp_utils import HOSTNAME


class StatisticsTestCase(BaseAgentTestCase):
    def setUp(self) -> None:
        self.statistics = StatisticsAgent("statisticstest1@"+HOSTNAME, "qwertyqwerty")

    def test_init_statistics(self):
        self.assertIsNotNone(self.statistics)
        self.assertEqual(self.statistics.jid, JID.fromstr("statisticstest1@"+HOSTNAME))

    @pytest.mark.asyncio
    async def test_add_sensor_contact_list(self):
        fake_sensor = FFDSensorAgent(agent_jid="testsensor1@"+HOSTNAME, password="qwertyqwerty")
        fake_sensor.start().result()

        self.statistics.start(auto_register=True).result()
        fake_sensor.presence.subscribe("statisticstest1@"+HOSTNAME)
        await asyncio.sleep(2)
        self.assertEqual(len(self.statistics.presence.get_contacts()), 1)
        self.assertIn(JID.fromstr("testsensor1@"+HOSTNAME), self.statistics.presence.get_contacts())

        fake_sensor.stop().result()
        self.statistics.start(auto_register=True).result()

    @pytest.mark.asyncio
    async def test_insert_statistic(self):
        fake_agent = "testsensor1@"+HOSTNAME
        self.statistics.db_conn.insert_sensor_value(fake_agent, {}, Collections.sensors_detections.value)

        self.statistics.start(auto_register=True).result()
        await asyncio.sleep(5)

        query = {"agent_jid": fake_agent}
        result = self.statistics.db_conn.get_collection(Collections.detection_statistics.value).find(query)
        self.assertGreaterEqual(result.count(), 1)

        self.statistics.db_conn.get_collection(Collections.sensors_detections.value).delete_many(query)
        self.statistics.db_conn.get_collection(Collections.detection_statistics.value).delete_many(query)
        self.statistics.stop().result()
