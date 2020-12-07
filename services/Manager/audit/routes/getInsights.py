import audit.const.tasks as tasks
import audit.const.steps as steps
from audit.inc.audit import Audit

ourTasks = [tasks.CEA, tasks.CTA, tasks.CPA]
ourSteps = [steps.creation, steps.selection]


def run():
    res = []
    audit = Audit()
    for task in ourTasks:
        for step in ourSteps:
            query = """
            SELECT method, sum(solved_cnt)
            FROM audit
            WHERE task='{}' and step='{}'
            GROUP BY method
            ORDER BY SUM(solved_cnt) DESC  
            """.format(task, step)
            # print(query)
            items = audit.get(query, 'All')
            res.append({'task': task, 'step': step, 'methods': items})
            # print(items)
    return {'res': res}


if __name__ == '__main__':
    # test()
    print(run())
