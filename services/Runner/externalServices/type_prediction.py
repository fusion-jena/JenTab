import config
from externalServices.services import Service, API


class Type_Prediction_Service(Service):
    name = "typeprediction.svc"

    if config.run_mode == 0:
        root = "http://127.0.0.1:5006"
    else:
        root = "http://{0}:5006".format(name)

    def __init__(self):
        self.get_type = API(self, self.root, "get_type", "text", "POST")
        self.get_type_lst = API(self, self.root, "get_type_lst", "texts", "POST")


# create an instance for export
TypePrediction = Type_Prediction_Service()
