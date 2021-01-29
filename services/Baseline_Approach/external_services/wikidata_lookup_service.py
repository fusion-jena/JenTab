from config import run_mode
from services import Service, API


class Wikidata_Lookup_Service(Service):
    name = "Wikidata_Lookup_Service"

    if run_mode == 0:
        root = "http://127.0.0.1:5008"
    else:
        root = "http://lookup.wikidata.svc:5008"

    def __init__(self):
        self.look_for = API(self, self.root, "look_for", ["text", "dbo_class"], "POST")
        self.look_for_lst = API(self, self.root, "look_for_lst", ["texts", "dbo_col_class"], "POST")
