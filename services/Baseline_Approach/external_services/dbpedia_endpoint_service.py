from config import run_mode
from services import Service, API


class DBpedia_Endpoint_Service(Service):
    name = "DBpedia_Endpoint_Service"

    if run_mode == 0:
        root = "http://127.0.0.1:5002"
    else:
        root = "http://endpoint.dbpedia.svc:5002"

    def __init__(self):
        self.get_type_for = API(self, self.root, "get_type_for", "text", "POST")
        self.get_type_for_lst = API(self, self.root, "get_type_for_lst", "texts", "POST")

        self.get_subclasses_for = API(self, self.root, "get_subclasses_for", "dboclass", "POST")
        self.get_parents_for = API(self, self.root, "get_parents_for", "dboclass", "POST")
