import config
from externalServices.services import Service, API


class Auditor_Service(Service):
    name = "auditor.svc"

    if config.run_mode == 0:
        root = "http://127.0.0.1:5011"
    else:
        root = "http://{0}:5010".format(name)

    def __init__(self):
        self.audit_lst = API(self, self.root, "audit_lst", "records", "POST")


# create an instance for export
Auditor = Auditor_Service()
