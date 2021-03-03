from WSN.ffdsensoragent import FFDSensorAgent
from processing.ffddbmanageragent import FFDDBManagerAgent
from processing.ffdtriggeragent import FFDTriggerAgent
from processing.statisticsagent import StatisticsAgent
from presentation.frontendagent import FrontEndAgent
from util.xmpp_utils import HOSTNAME
from util.db_utils import Databases, Collections
from spade import quit_spade

import pymongo

SPREAD_PARAM = 0

if __name__ == '__main__':
    # DATABASE INITIALIZATION
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    if Databases.test_db.value not in client.list_database_names():
        print("Created database "+Databases.test_db.value)
        for collection in Collections:
            print("Created collection "+collection.value)
            client[Databases.test_db.value].create_collection(collection.value)
    client.close()

    db_manager = FFDDBManagerAgent("dbmanager@"+HOSTNAME, "qwertyqwerty")
    db_manager.start(auto_register=True).result()

    statistics = StatisticsAgent("statistics@"+HOSTNAME, "qwertyqwerty")
    statistics.start(auto_register=True).result()

    trigger = FFDTriggerAgent("trigger@"+HOSTNAME, "qwertyqwerty")
    trigger.start(auto_register=True).result()

    frontend = FrontEndAgent("frontend@"+HOSTNAME, "qwertyqwerty")
    frontend.start(auto_register=True).result()

    station1 = FFDSensorAgent("station1@"+HOSTNAME, "CHOOSE A SECURE PASSWORD", SPREAD_PARAM)
    station1.start(auto_register=True)
    station2 = FFDSensorAgent("station2@"+HOSTNAME, "qwertyqwerty", SPREAD_PARAM)
    station2.start(auto_register=True)
    station3 = FFDSensorAgent("station3@"+HOSTNAME, "qwertyqwerty", SPREAD_PARAM)
    station3.start(auto_register=True)
    station4 = FFDSensorAgent("station4@"+HOSTNAME, "qwertyqwerty", SPREAD_PARAM)
    station4.start(auto_register=True)
    station5 = FFDSensorAgent("station5@"+HOSTNAME, "qwertyqwerty", SPREAD_PARAM)
    station5.start(auto_register=True)
    station6 = FFDSensorAgent("station6@"+HOSTNAME, "qwertyqwerty", SPREAD_PARAM)
    station6.start(auto_register=True)

    #try:
    #    db_manager.stop()
    #    statistics.stop()
    #    trigger.stop()
    #    frontend.stop()
    #    station1.stop()
    #    station2.stop()
    #   station3.stop()
    #    station4.stop()
    #    station5.stop()
    #    station6.stop()
    #except:
    #    print("Tear down spade")

    #quit_spade()
