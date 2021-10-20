from config import run_mode
from services import Service, API


class Autocorrect_Service(Service):
    name = "Autocorrect_Service"

    if run_mode == 0:
        root = "http://127.0.0.1:5005"
    else:
        root = "http://autocorrect.svc:5005"

    def __init__(self):
        self.correct_cell = API(self, self.root, "correct_cell", "text", "POST")
        self.get_knowns = API(self, self.root, "get_knowns", "values", "POST")