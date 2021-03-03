import asyncio

import pytest
from aioxmpp import JID
from spade.behaviour import OneShotBehaviour
from spade.message import Message

from WSN.ffdsensoragent import FFDSensorAgent
from test.utilities import MockedAgentFactory, BaseAgentTestCase
from util.xmpp_utils import HOSTNAME


class SpreadingTestCase(BaseAgentTestCase):
    def setUp(self) -> None:
        self.sensor_agent1 = FFDSensorAgent(agent_jid="sensor1test@"+HOSTNAME, password="qwertyqwerty")
        self.sensor_agent2 = FFDSensorAgent(agent_jid="sensor2test@"+HOSTNAME, password="qwertyqwerty")
        self.sensor_agent3 = FFDSensorAgent(agent_jid="sensor3test@"+HOSTNAME, password="qwertyqwerty")
        self.sensor_agent4 = FFDSensorAgent(agent_jid="sensor4test@"+HOSTNAME, password="qwertyqwerty")
        self.sensor_agent5 = FFDSensorAgent(agent_jid="sensor5test@"+HOSTNAME, password="qwertyqwerty")

    def test_init_wsn_agents(self):
        self.assertIsNotNone(self.sensor_agent1)
        self.assertEqual(self.sensor_agent1.jid, JID.fromstr("sensor1test@"+HOSTNAME))
        self.assertIsNotNone(self.sensor_agent2)
        self.assertEqual(self.sensor_agent2.jid, JID.fromstr("sensor2test@"+HOSTNAME))
        self.assertIsNotNone(self.sensor_agent3)
        self.assertEqual(self.sensor_agent3.jid, JID.fromstr("sensor3test@"+HOSTNAME))
        self.assertIsNotNone(self.sensor_agent4)
        self.assertEqual(self.sensor_agent4.jid, JID.fromstr("sensor4test@"+HOSTNAME))
        self.assertIsNotNone(self.sensor_agent5)
        self.assertEqual(self.sensor_agent5.jid, JID.fromstr("sensor5test@"+HOSTNAME))

    @pytest.mark.asyncio
    async def test_init_sensor1_neighbour(self):
        self.sensor_agent1.start(auto_register=True).result()
        self.sensor_agent2.start(auto_register=True).result()
        self.sensor_agent3.start(auto_register=True).result()

        self.sensor_agent1.presence.subscribe("sensor2test@"+HOSTNAME)
        self.sensor_agent1.presence.subscribe("sensor3test@" + HOSTNAME)

        await asyncio.sleep(2)

        sensor1contacts = self.sensor_agent1.presence.get_contacts()
        self.assertIn(JID.fromstr("sensor2test@"+HOSTNAME), sensor1contacts)
        self.assertIn(JID.fromstr("sensor3test@" + HOSTNAME), sensor1contacts)

        self.sensor_agent1.stop().result()
        self.sensor_agent2.stop().result()
        self.sensor_agent3.stop().result()

    @pytest.mark.asyncio
    async def test_init_sensor2_neighbour(self):
        self.sensor_agent1.start(auto_register=True).result()
        self.sensor_agent2.start(auto_register=True).result()
        self.sensor_agent4.start(auto_register=True).result()

        self.sensor_agent2.presence.subscribe("sensor4test@"+HOSTNAME)

        await asyncio.sleep(2)

        sensor2contacts = self.sensor_agent2.presence.get_contacts()
        self.assertIn(JID.fromstr("sensor1test@"+HOSTNAME), sensor2contacts)
        self.assertIn(JID.fromstr("sensor4test@" + HOSTNAME), sensor2contacts)

        self.sensor_agent1.stop().result()
        self.sensor_agent2.stop().result()
        self.sensor_agent4.stop().result()

    @pytest.mark.asyncio
    async def test_init_sensor3_neighbour(self):
        self.sensor_agent1.start(auto_register=True).result()
        self.sensor_agent3.start(auto_register=True).result()
        self.sensor_agent5.start(auto_register=True).result()

        self.sensor_agent3.presence.subscribe("sensor5test@"+HOSTNAME)

        await asyncio.sleep(2)

        sensor3contacts = self.sensor_agent3.presence.get_contacts()
        self.assertIn(JID.fromstr("sensor1test@"+HOSTNAME), sensor3contacts)
        self.assertIn(JID.fromstr("sensor5test@" + HOSTNAME), sensor3contacts)

        self.sensor_agent1.stop().result()
        self.sensor_agent3.stop().result()
        self.sensor_agent5.stop().result()

    @pytest.mark.asyncio
    async def test_init_sensor4_neighbour(self):
        self.sensor_agent2.start(auto_register=True).result()
        self.sensor_agent4.start(auto_register=True).result()
        self.sensor_agent5.start(auto_register=True).result()

        self.sensor_agent4.presence.subscribe("sensor5test@"+HOSTNAME)

        await asyncio.sleep(2)

        sensor4contacts = self.sensor_agent4.presence.get_contacts()
        self.assertIn(JID.fromstr("sensor2test@"+HOSTNAME), sensor4contacts)
        self.assertIn(JID.fromstr("sensor5test@" + HOSTNAME), sensor4contacts)

        self.sensor_agent2.stop().result()
        self.sensor_agent4.stop().result()
        self.sensor_agent5.stop().result()

    @pytest.mark.asyncio
    async def test_init_sensor5_neighbour(self):
        self.sensor_agent5.start(auto_register=True).result()

        sensor5contacts = self.sensor_agent5.presence.get_contacts()
        self.assertIn(JID.fromstr("sensor3test@"+HOSTNAME), sensor5contacts)
        self.assertIn(JID.fromstr("sensor4test@" + HOSTNAME), sensor5contacts)

        self.sensor_agent5.stop().result()

    @pytest.mark.asyncio
    async def test_spreading(self):
        self.sensor_agent1.start(auto_register=True).result()
        self.sensor_agent2.start(auto_register=True).result()
        self.sensor_agent3.start(auto_register=True).result()
        self.sensor_agent4.start(auto_register=True).result()
        self.sensor_agent5.start(auto_register=True).result()
        fake_trigger = MockedAgentFactory(jid="trigger@"+HOSTNAME)

        class SendBehaviour(OneShotBehaviour):
            async def run(self):
                msg = Message(to="sensor1test@"+HOSTNAME)
                msg.set_metadata("performative", "request")
                await self.send(msg)
                await asyncio.sleep(2)
                self.kill()

        behaviour = SendBehaviour()

        fake_trigger.add_behaviour(behaviour)
        fake_trigger.start().result()
        behaviour.join()

        await asyncio.sleep(5)

        self.assertEqual(2, len(self.sensor_agent1.behaviours))
        self.assertEqual(2, len(self.sensor_agent2.behaviours))
        self.assertEqual(2, len(self.sensor_agent3.behaviours))
        self.assertEqual(2, len(self.sensor_agent4.behaviours))
        self.assertEqual(2, len(self.sensor_agent5.behaviours))

        self.sensor_agent1.stop().result()
        self.sensor_agent2.stop().result()
        self.sensor_agent3.stop().result()
        self.sensor_agent4.stop().result()
        self.sensor_agent5.stop().result()
