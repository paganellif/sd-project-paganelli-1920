from spade.agent import Agent
from spade.template import Template
from spade.behaviour import State
from spade.message import Message
from processing.triggerstrategy import TriggerStrategy
from util.logger import LoggerImpl
from util.xmpp_utils import HOSTNAME
from util.db_utils import Collections
from processing.dbconnfactory import DBConnFactory
from base.fsm import BaseFSM
import json
from aioxmpp import JID


class InsertEventDetection(State):
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            # check if the received message matches the template detection_inform
            if self.agent.detection_inform.match(msg):
                self.agent.log.log("Message received from " + str(msg.sender) + ": " + str(msg.body))
                body = json.loads(str(msg.body))
                agent_jid = body.pop("agent_jid")
                # Insert of flame detection
                self.agent.db_conn.insert_event_detection(agent_jid, body, Collections.event_detections.value)
                # Agent_jid of the agent for which to check the number of flame detections
                self.set("agent_jid", agent_jid)
                self.set_next_state("STATE_TWO")
            elif self.agent.sensor_fail.match(msg):
                self.agent.log.log("FAILURE!! Agent " + str(msg.sender) + " can't perform the action")
                # Stores the detailed error report in the database
                self.agent.db_conn.insert_error_report(str(msg.sender), str(msg.body), Collections.failure_reports.value)
                # Here you could tell the other sensors in the network to start the alarm since
                # the one that detected the event is out of order
                self.set_next_state("STATE_ONE")
            elif self.agent.sensor_response.match(msg):
                self.agent.log.log("Agent "+str(msg.sender)+" finished the job")
                msgsnd = Message(to=str("frontend@"+HOSTNAME))
                msgsnd.set_metadata("performative", "inform")
                body: dict = {str(msg.sender): "Working"}
                msgsnd.body = json.dumps(body)
                await self.send(msgsnd)
                self.set_next_state("STATE_ONE")
            else:
                self.set_next_state("STATE_ONE")
        else:
            self.set_next_state("STATE_ONE")


class CheckEventsDetections(State):
    async def run(self):
        if self.agent.check_strategy.check_event_detections(self):
            # Transition to state 3 to activate the alarm
            self.agent.log.log("TRUE DETECTION")
            self.set_next_state("STATE_THREE")
        else:
            self.agent.log.log("FALSE DETECTION")
            self.set_next_state("STATE_ONE")


class SignalPerformActuatorAction(State):
    async def run(self):
        self.agent.db_conn.insert_actuator_triggered(self.get("agent_jid"), Collections.triggered_actions.value)
        # the sensoragent must be subscribed in the contact list and have the status available to perform the action
        if JID.fromstr(self.get("agent_jid")) in self.agent.presence.get_contacts():
            # If you want to send the alarm to all the sensoragents you need to have them
            # subscribed to insert them in the contacts of the triggeragent
            msg = Message(to=self.get("agent_jid"))
            # Set the "request" FIPA performative
            msg.set_metadata("performative", "request")
            document: dict = {"alarm": True}
            msg.body = json.dumps(document)
            self.agent.log.log("Message sent to " + self.get("agent_jid") + " to perform the action")
            await self.send(msg)

            msg = Message(to="frontend@"+HOSTNAME)
            msg.set_metadata("performative", "inform")
            body: dict = {self.get("agent_jid"): "Alarm On"}
            msg.body = json.dumps(body)
            await self.send(msg)
        else:
            self.agent.log.log("FAILURE!! Agent " + self.get("agent_jid") + " can't perform the action")
            # Stores the detailed error report in the database
            description = "agent is not in the contact list"
            self.agent.db_conn.insert_error_report(self.get("agent_jid"), description, Collections.failure_reports.value)
            # Here you could tell the other sensors in the network to start the alarm since
            # the one that detected the event is out of order
        self.set_next_state("STATE_ONE")


class TriggerAgentBehav(BaseFSM):
    async def on_start(self):
        await super().on_start()
        self.add_state(name="STATE_ONE", state=InsertEventDetection(), initial=True)
        self.add_state(name="STATE_TWO", state=CheckEventsDetections())
        self.add_state(name="STATE_THREE", state=SignalPerformActuatorAction())

        self.add_transition(source="STATE_ONE", dest="STATE_ONE")
        self.add_transition(source="STATE_ONE", dest="STATE_TWO")
        self.add_transition(source="STATE_TWO", dest="STATE_ONE")
        self.add_transition(source="STATE_TWO", dest="STATE_THREE")
        self.add_transition(source="STATE_THREE", dest="STATE_ONE")


class TriggerAgent(Agent):
    def __init__(self, agent_jid: str, password: str):
        super().__init__(agent_jid, password)
        self.check_strategy: TriggerStrategy = None
        self.log = LoggerImpl(str(self.jid))
        self.db_conn = DBConnFactory().create_trigger_db_connector()
        self.sensor_response = Template()
        self.sensor_fail = Template()
        self.detection_inform = Template()

    async def setup(self):
        self.sensor_response.set_metadata("performative", "inform")
        self.sensor_fail.set_metadata("performative", "refuse")
        self.detection_inform.set_metadata("performative", "inform")
        self.detection_inform.sender = str("dbmanager@"+HOSTNAME)

        self.add_behaviour(TriggerAgentBehav())
