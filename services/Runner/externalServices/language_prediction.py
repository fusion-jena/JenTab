import config
from externalServices.services import Service, API


class Language_Prediction_Service(Service):
    name = "languageprediction.svc"

    if config.run_mode == 0:
        root = "http://127.0.0.1:5004"
    else:
        root = "http://{0}:5004".format(name)

    def __init__(self):
        self.get_language = API(self, self.root, "get_language", "text", "POST")
        self.get_language_lst = API(self, self.root, "get_language_lst", "texts", "POST")


# create an instance for export
LanguagePrediction = Language_Prediction_Service()
