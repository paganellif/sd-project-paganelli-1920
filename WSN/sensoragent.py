from spade.agent import Agent
from spade.template import Template
from spade.message import Message
from spade.behaviour import State
from WSN.sensorstrategy import SensorStrategy, ActuatorStrategy, SpreadingStrategy
from base.fsm import BaseFSM
from util.logger import LoggerImpl
from util.xmpp_utils import HOSTNAME
from aioxmpp import JID
import json


class SendSensorValues(State):
    async def run(self):
        msg = Message(to="dbmanager@" + HOSTNAME)
        msg.set_metadata("performative", "inform")
        msg.body = json.dumps(self.agent.sensor_read_strategy.read_sensor_values())
        await self.send(msg)
        self.set_next_state("STATE_TWO")


class MsgReceiver(State):
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            if self.agent.action.match(msg):
                if self.agent.presence.is_available() is False:
                    msg = Message(to="trigger@" + HOSTNAME)
                    msg.set_metadata("preformative", "refuse")
                    msg.body = "Sensoragent " + str(self.agent.jid) + " not available"
                    await self.send(msg)
                    # Send error msg
                    self.set_next_state("STATE_ONE")
                else:
                    # Perform Action
                    self.agent.set("information", "")
                    self.set_next_state("STATE_THREE")
            elif self.agent.spread.match(msg):
                self.agent.set("information", str(msg.body))
                # Spreading
                self.set_next_state("STATE_FOUR")
            else:
                self.set_next_state("STATE_ONE")
        else:
            self.set_next_state("STATE_ONE")


class PerformAction(State):
    async def run(self):
        self.agent.actuator_strategy.perform_action(self)
        self.set_next_state("STATE_FOUR")


class SpreadInformation(State):
    async def run(self):
        if await self.agent.spreading_strategy.spreading(self, self.agent.get("information")):
            self.set_next_state("STATE_THREE")
        else:
            self.set_next_state("STATE_ONE")


class SensorAgentBehav(BaseFSM):
    async def on_start(self):
        await super().on_start()
        self.add_state(name="STATE_ONE", state=SendSensorValues(), initial=True)
        self.add_state(name="STATE_TWO", state=MsgReceiver())
        self.add_state(name="STATE_THREE", state=PerformAction())
        self.add_state(name="STATE_FOUR", state=SpreadInformation())

        self.add_transition(source="STATE_ONE", dest="STATE_TWO")
        self.add_transition(source="STATE_TWO", dest="STATE_THREE")
        self.add_transition(source="STATE_TWO", dest="STATE_ONE")
        self.add_transition(source="STATE_TWO", dest="STATE_FOUR")
        self.add_transition(source="STATE_THREE", dest="STATE_FOUR")
        self.add_transition(source="STATE_FOUR", dest="STATE_THREE")
        self.add_transition(source="STATE_FOUR", dest="STATE_ONE")

        if JID.fromstr("trigger@" + HOSTNAME) not in self.agent.presence.get_contacts():
            self.agent.log.log("Subscription sent to triggeragent")
            # Send a subscribe request to the triggeragent
            self.presence.subscribe("trigger@" + HOSTNAME)
        else:
            self.agent.log.log("triggeragent is already in the contact list")

        if JID.fromstr("dbmanager@" + HOSTNAME) not in self.agent.presence.get_contacts():
            self.agent.log.log("Subscription sent to dbmanageragent")
            # Send a subscribe request to the dbmanageragent
            self.presence.subscribe("dbmanager@" + HOSTNAME)
        else:
            self.agent.log.log("dbmanageragent is already in the contact list")

        if JID.fromstr("statistics@" + HOSTNAME) not in self.agent.presence.get_contacts():
            self.agent.log.log("Subscription sent to statisticsagent")
            # Send a subscribe request to the statisticsagent
            self.presence.subscribe("statistics@" + HOSTNAME)
        else:
            self.agent.log.log("statisticsagent is already in the contact list")


class SensorAgent(Agent):
    def __init__(self, agent_jid: str, password: str, spread_param=2):
        super().__init__(agent_jid, password)
        self.sensor_read_strategy: SensorStrategy = None
        self.actuator_strategy: ActuatorStrategy = None
        self.spreading_strategy: SpreadingStrategy = None
        self.log = LoggerImpl(str(self.jid))
        self.spread_param = spread_param
        self.action = Template()
        self.spread = Template()

    async def setup(self):
        self.action.set_metadata("performative", "request")
        self.action.sender = str("trigger@"+HOSTNAME)
        self.spread.set_metadata("performative", "propagate")

        self.add_behaviour(SensorAgentBehav())
