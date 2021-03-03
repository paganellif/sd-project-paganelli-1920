import random
import uuid

from aioxmpp import JID

from WSN.sensoragent import SensorAgent
from WSN.sensorstrategy import SensorStrategy, ActuatorStrategy, SpreadingStrategy
from WSN.sensorstreamerfactory import SensorStreamerFactory
from util.db_utils import Parameters, TriggerEvents
from util.xmpp_utils import HOSTNAME
from spade.message import Message
from spade.behaviour import PeriodicBehaviour, CyclicBehaviour
import datetime


class SensorStrategyImpl(SensorStrategy):
    def __init__(self):
        self.__sensor_streamer = SensorStreamerFactory().create_sensor_streamer()

    def read_sensor_values(self) -> dict:
        temp = self.__sensor_streamer.get_temp()
        hum = self.__sensor_streamer.get_hum()
        wind = self.__sensor_streamer.get_wind()
        flame = self.__sensor_streamer.get_flame()
        return {Parameters.temperature.value: temp,
                Parameters.humidity.value: hum,
                Parameters.wind.value: wind,
                TriggerEvents.event.value: bool(flame)}


class ActuatorStrategyImpl(ActuatorStrategy):
    class ActionBehav(PeriodicBehaviour):
        def __init__(self, period, duration):
            super().__init__(period)
            self.start_time = datetime.datetime.now()

            if duration < 0:
                raise ValueError("duration must be greater or equal than zero")
            else:
                self.end_time = self.start_time + datetime.timedelta(seconds=duration)

        async def on_start(self):
            self.agent.log.log("ACTION STARTED!")

        async def run(self):
            self.agent.log.log("ACTION RUNNING")
            self.agent.log.log("ALARM ON!")
            if datetime.datetime.now() >= self.end_time:
                msg = Message(to="trigger@" + HOSTNAME)
                msg.set_metadata("performative", "inform")
                msg.body = "Job done!"
                await self.send(msg)
                self.kill()
                return

        async def on_end(self):
            self.agent.remove_behaviour(self)
            self.agent.log.log("ACTION ENDED!")

    def perform_action(self, behaviour: CyclicBehaviour) -> None:
        behaviour.agent.add_behaviour(self.ActionBehav(period=2, duration=20))


class SpreadingStrategyImpl(SpreadingStrategy):

    async def __perform_spreading(self, behaviour):
        contact_list: list = list(behaviour.agent.presence.get_contacts().keys()).copy()
        contact_list.remove(JID.fromstr("dbmanager@"+HOSTNAME))
        contact_list.remove(JID.fromstr("trigger@" + HOSTNAME))
        contact_list.remove(JID.fromstr("statistics@" + HOSTNAME))

        real_contact_list: list = list()
        if (behaviour.agent.spread_param >= len(contact_list)) or (behaviour.agent.spread_param == -1):
            real_contact_list = contact_list
        else:
            real_contact_list = random.choices(contact_list, k=behaviour.agent.spread_param)
        for agent in real_contact_list:
            behaviour.agent.log.log(str(agent))
            behaviour.agent.log.log(behaviour.agent.get("spreading_info_snd"))
            msg = Message(to=str(agent))
            msg.set_metadata("performative", "propagate")
            msg.body = behaviour.agent.get("spreading_info_snd")
            await behaviour.send(msg)

    async def spreading(self, behaviour, information: str) -> bool:
        behaviour.agent.set("spreading_info_rcv", information)

        if behaviour.agent.spread_param is 0:
            # There is no spreading of information
            return False
        # That means this is the FFDSensorAgent who start the spreading
        # because it's entered the spreading state without having received a message
        if behaviour.agent.get("spreading_info_rcv") is "":
            # Set the information that has to be spread
            msg_uid = "["+str(uuid.uuid1())+"] "
            behaviour.agent.set("spreading_info_snd", msg_uid+str(behaviour.agent.jid) + " triggered the alarm")
            await self.__perform_spreading(behaviour)
            # False means that the FFDSensorAgent has not to perform any action
            return False
        else:
            if behaviour.agent.get("spreading_info_rcv") == behaviour.agent.get("spreading_info_snd"):
                behaviour.agent.log.log("Information received already disseminated")
                # False means that the FFDSensorAgent has not to perform any action
                return False
            else:
                # Set the information sent equal to the information received in order to
                # avoid the second message sending
                behaviour.agent.set("spreading_info_snd", behaviour.agent.get("spreading_info_rcv"))
                await self.__perform_spreading(behaviour)
                # True means that the FFDSensorAgent must perform the action on th actuator
                return True


class FFDSensorAgent(SensorAgent):
    def __init__(self, agent_jid: str, password: str, spread_param=2):
        if spread_param < -1:
            spread_param = 0
        super().__init__(agent_jid, password, spread_param=spread_param)
        self.sensor_read_strategy = SensorStrategyImpl()
        self.actuator_strategy = ActuatorStrategyImpl()
        self.spreading_strategy = SpreadingStrategyImpl()
