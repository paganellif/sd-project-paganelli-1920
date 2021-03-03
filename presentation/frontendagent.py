import json
import os

from spade.agent import Agent
from spade.behaviour import State
from spade.template import Template

from base.fsm import BaseFSM
from processing.dbconnfactory import DBConnFactory
from presentation.routehandler import RouteHandler
from util.db_utils import Collections
from util.logger import LoggerImpl
from util.xmpp_utils import HOSTNAME


class StartServer(State):
    async def run(self):
        self.agent.web.start(hostname="localhost", port=self.agent.port, templates_path="presentation/templates")
        hostname = self.agent.web.hostname
        port = self.agent.web.port
        if self.agent.web.is_started():
            self.agent.log.log("Web server listening on http://"+hostname+":"+str(port))

        self.set_next_state("STATE_TWO")


class StationsStateUpdate(State):
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            if self.agent.states_update.match(msg):
                self.agent.log.log("Received the update of the sensoragent states from the triggeragent")
                body: dict = json.loads(str(msg.body))
                self.agent.stations_status.update(body)
        self.set_next_state("STATE_TWO")


class FrontEndAgentBehav(BaseFSM):
    async def on_start(self):
        await super().on_start()
        self.add_state(name="STATE_ONE", state=StartServer(), initial=True)
        self.add_state(name="STATE_TWO", state=StationsStateUpdate())

        self.add_transition(source="STATE_ONE", dest="STATE_TWO")
        self.add_transition(source="STATE_TWO", dest="STATE_TWO")


class FrontEndAgent(Agent):
    def __init__(self, agent_jid: str, password: str):
        super().__init__(agent_jid, password)
        self.port = 8080
        self.route_handler = RouteHandler(self)
        self.db_conn = DBConnFactory().create_front_end_db_connector()
        self.log = LoggerImpl(str(self.jid))
        self.stations_status: dict = dict()
        self.states_update = Template()

    async def setup(self):
        for jid in list(self.db_conn.select_distinct_agents_jid(Collections.sensors_detections.value)):
            self.stations_status[jid] = "Working"
        self.web.app['static_root_url'] = "/static/"
        root_dir = os.path.dirname(os.path.abspath(__file__))
        self.web.app.router.add_static('/static/', path=str(root_dir+"/static"), name='static')
        self.web.add_get("/", self.route_handler.home, "index.html")
        self.web.add_get("/value/{jid}", self.route_handler.value, None)
        self.web.add_get("/wsn", self.route_handler.wsn, None)
        self.web.add_get("/state/{jid}", self.route_handler.state, None)
        self.web.add_get("/statistics/{jid}", self.route_handler.statistics, None)

        self.states_update.set_metadata("performative", "inform")
        self.states_update.sender = str("trigger@" + HOSTNAME)

        self.add_behaviour(FrontEndAgentBehav())
