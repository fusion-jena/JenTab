from config import run_mode
from services import Service, API


class Generic_Lookup_Service(Service):
    name = "Generic_Lookup_Service"

    if run_mode == 0:
        root = "http://127.0.0.1:5010"
    else:
        root = "http://lookup.generic.svc:5010"

    def __init__(self):
        self.look_for = API(self, self.root, "look_for", ["needle"], "POST")
        self.look_for_lst = API(self, self.root, "look_for_lst", ["needles"], "POST")
