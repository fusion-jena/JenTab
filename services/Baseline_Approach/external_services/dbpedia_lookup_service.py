from config import run_mode
from services import Service, API


class DBpedia_Lookup_Service(Service):
    name = "DBpedia_Lookup_Service"

    if run_mode == 0:
        root = "http://127.0.0.1:5003"
    else:
        root = "http://lookup.dbpedia.svc:5003"

    def __init__(self):
        self.look_for = API(self, self.root, "look_for", ["text", "dbo_class"], "POST")
        self.look_for_lst = API(self, self.root, "look_for_lst", ["texts", "dbo_col_class"], "POST")
