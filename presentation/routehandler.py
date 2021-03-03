import json
from util.db_utils import Collections
from aiohttp import web


class RouteHandler:
    def __init__(self, agent):
        self.__agent = agent

    async def home(self, request):
        return None

    async def wsn(self, request):
        jids: list = list(self.__agent.db_conn.select_distinct_agents_jid(Collections.sensors_detections.value))
        response = json.dumps({"agents_jid": jids})
        return response

    async def value(self, request):
        agent_jid = request.match_info["jid"]
        limit = int()
        response: list = list()
        if agent_jid:
            if agent_jid not in self.__agent.stations_status.keys():
                raise web.HTTPBadRequest()
            if "limit" in request.rel_url.query.keys():
                limit = int(request.rel_url.query["limit"])
                if limit < 1:
                    raise web.HTTPBadRequest()
            else:
                limit = 1
            res = self.__agent.db_conn.select_last_detections(agent_jid, limit, Collections.sensors_detections.value)
            for doc in res:
                doc.pop("_id")
                doc["timestamp"] = doc.pop("timestamp").__str__()
                response.append(doc)
            return response
        else:
            raise web.HTTPBadRequest()

    async def state(self, request):
        agent_jid = request.match_info["jid"]
        if agent_jid:
            if agent_jid not in self.__agent.stations_status.keys():
                raise web.HTTPBadRequest()
            status = self.__agent.stations_status[agent_jid]
            response = {"state": status}
            return response
        else:
            raise web.HTTPBadRequest()

    async def statistics(self, request):
        agent_jid = request.match_info["jid"]
        limit = int()
        response: list = list()
        if agent_jid:
            if agent_jid not in self.__agent.stations_status.keys():
                raise web.HTTPBadRequest()
            if "limit" in request.rel_url.query.keys():
                limit = int(request.rel_url.query["limit"])
                if limit < 1:
                    raise web.HTTPBadRequest()
            else:
                limit = 1
            res = self.__agent.db_conn.select_last_statistics(agent_jid, limit, Collections.detection_statistics.value)
            for doc in res:
                doc.pop("_id")
                doc["timestamp"] = doc.pop("timestamp").__str__()
                response.append(doc)
            return response
        else:
            raise web.HTTPBadRequest()
