import config
from externalServices.services import Service, API


class Clean_Cells_Service(Service):
    name = "cleancells.svc"

    if config.run_mode == 0:
        root = "http://127.0.0.1:5001"
    else:
        root = "http://{0}:5001".format(name)

    def __init__(self):
        # Encoding fix ... (All types are supposed to be fixed from encoding, generic parsing and clean data.)
        self.fix_cell_lst = API(self, self.root, "fix_cell_lst", ["cells"], "POST")

        # Specific Cleaning per type, i.e., Special Parsers for Quantities?
        self.specific_clean_cell_lst = API(self, self.root, "specific_clean_cell_lst", ["coltype", "cells"], "POST")


# create an instance for export
CleanCells = Clean_Cells_Service()
