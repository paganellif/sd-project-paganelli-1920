import asyncio

from spade.agent import Agent
from spade.behaviour import State

from base.fsm import BaseFSM
from processing.dbconnfactory import DBConnFactory
from util.db_utils import Parameters, Collections
from util.logger import LoggerImpl


class InsertStatistics(State):
    async def run(self):
        for agent in self.agent.presence.get_contacts():
            self.agent.db_conn.insert_aggregation(str(agent), Collections.detection_statistics.value,
                                                  Collections.sensors_detections.value, self.agent.keys)
        await asyncio.sleep(self.agent.period)
        self.set_next_state("STATE_ONE")


class StatisticsAgentBehav(BaseFSM):
    async def on_start(self):
        await super().on_start()
        self.add_state(name="STATE_ONE", state=InsertStatistics(), initial=True)

        self.add_transition(source="STATE_ONE", dest="STATE_ONE")


class StatisticsAgent(Agent):
    def __init__(self, agent_jid, password, period=60):
        super().__init__(agent_jid, password)
        self.log = LoggerImpl(str(self.jid))
        self.db_conn = DBConnFactory().create_statistics_db_connector()
        self.period = period
        self.keys: list = list()
        for name in Parameters:
            self.keys.append(name.value)

    async def setup(self):
        self.add_behaviour(StatisticsAgentBehav())
