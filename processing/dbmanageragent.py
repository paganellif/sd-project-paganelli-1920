import json

from spade.agent import Agent
from spade.behaviour import State
from spade.message import Message
from spade.template import Template

from processing.dbmanagerstrategy import DBManagerStrategy
from base.fsm import BaseFSM
from processing.dbconnfactory import DBConnFactory
from util.db_utils import Collections, TriggerEvents
from util.logger import LoggerImpl
from util.xmpp_utils import HOSTNAME


class InsertSensorValue(State):
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            if self.agent.sensor_values.match(msg):
                body: dict = json.loads(str(msg.body))
                if self.agent.check_strategy.check_values(body):
                    self.agent.log.log("Message received from " + str(msg.sender) + ": " + str(msg.body))
                    db_coll = Collections.sensors_detections.value
                    res = self.agent.db_conn.insert_sensor_value(str(msg.sender), body, db_coll)
                    if body.get(TriggerEvents.event.value):
                        self.agent.log.log("EVENT DETECTED -----> TO BE CHECKED")
                        self.set("_id_read", res.inserted_id)
                        self.set("agent_jid", str(msg.sender))
                        self.set_next_state("STATE_TWO")
                    else:
                        self.set_next_state("STATE_ONE")
                else:
                    self.set_next_state("STATE_ONE")
            else:
                self.set_next_state("STATE_ONE")
        else:
            self.set_next_state("STATE_ONE")


class InformTrigger(State):
    async def run(self):
        msg = Message(to="trigger@" + HOSTNAME)
        msg.set_metadata("performative", "inform")
        document: dict = {"_id_read": str(self.get("_id_read")), "agent_jid": self.get("agent_jid")}
        msg.body = json.dumps(document)
        self.agent.log.log("Message sent to trigger")
        await self.send(msg)
        self.set_next_state("STATE_ONE")


class DBManagerAgentBehav(BaseFSM):
    async def on_start(self):
        await super().on_start()
        self.add_state(name="STATE_ONE", state=InsertSensorValue(), initial=True)
        self.add_state(name="STATE_TWO", state=InformTrigger())

        self.add_transition(source="STATE_ONE", dest="STATE_ONE")
        self.add_transition(source="STATE_ONE", dest="STATE_TWO")
        self.add_transition(source="STATE_TWO", dest="STATE_ONE")


class DBManagerAgent(Agent):
    def __init__(self, agent_jid: str, password: str):
        super().__init__(agent_jid, password)
        self.db_conn = DBConnFactory().create_manager_db_connector()
        self.check_strategy: DBManagerStrategy = None
        self.log = LoggerImpl(str(self.jid))
        self.sensor_values = Template()
        self.template = Template()

    async def setup(self):
        self.sensor_values.set_metadata("performative", "inform")
        self.template.set_metadata("performative", "inform")

        self.add_behaviour(DBManagerAgentBehav())
