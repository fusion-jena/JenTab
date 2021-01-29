from config import run_mode
from externalServices.services import Service, API


class Baseline_Approach_Service(Service):
    name = "baseline.svc"

    if run_mode == 0:
        root = "http://127.0.0.1:5000"
    else:
        root = "http://{0}".format(name)

    def __init__(self):
        self.solve = API(self, self.root,
                         "solve",
                         data_placeholder=["table", "targets"],
                         method="POST")

        self.activateLogging = API(self, self.root, "activateLogging", data_placeholder=['dummy'], method="POST")
        self.activateAuditing = API(self, self.root, "activateAudit", data_placeholder=['Flag'], method="POST")


# create an instance for export
BaselineApproach = Baseline_Approach_Service()
