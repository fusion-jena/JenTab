from pipeline.pipeline import Pipeline as Pipeline
from approach.approach import Approach
from utils import util_log


class BaselineApproach(Approach):
    def __init__(self, table, targets):
        self.targets = targets
        self.table = table
        self.table_name = table['name']

        # pipeline placeholder
        self.pipeline = None

    # ~~~~~~~~~~~~~~~~~~~~~~~~ Public methods ~~~~~~~~~~~~~~~~~~~~~~~~

    def exec_pipeline(self):
        self.pipeline = Pipeline(self.table, self.targets)
        util_log.start('baseline_approach: run_pipeline {0}'.format(self.table_name))
        self.pipeline.run()
        util_log.stop('baseline_approach: run_pipeline {0}'.format(self.table_name))

    def generate_CEA(self, targets=None):
        return self.pipeline.get_CEA()

    def generate_CTA(self, targets=None):
        return self.pipeline.get_CTA()

    def generate_CPA(self, targets=None):
        return self.pipeline.get_CPA()

    def get_Errors(self):
        return self.pipeline.get_Errors()

    def get_AuditRecords(self):
        return self.pipeline.get_AuditRecords()

    def get_CheckPoints(self):
        return self.pipeline.get_CheckPoints()
