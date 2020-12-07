from dateutil.relativedelta import relativedelta
import datetime
# import git
import os
import sqlite3
import config
from db import DB_PATH


def humanTimeDiff(sec):
    """
    get a human readable formating of a time difference
    https://stackoverflow.com/a/11157649/1169798
    """
    delta = relativedelta(seconds=sec)
    attrs = ['years', 'months', 'days', 'hours', 'minutes', 'seconds', 'microseconds']
    return ' '.join(['%d %s' % (getattr(delta, attr), getattr(delta, attr) > 1 and attr or attr[:-1]) for attr in attrs if getattr(delta, attr)])


def run():
    """retrieve statistics about the current progress of processing"""

    # prepare result object
    result = {
        'tables': {
            'total': 0,
            'unfinished': 0,
            'result': 0,
            'error': 0,
        },
        'times': {
            'result': 0,
            'error': 0,
            'remaining': 0,
        },
        'files': {
            'results': os.path.exists(os.path.join(config.WORK_PATH, 'results.zip')),
            'errors': os.path.exists(os.path.join(config.WORK_PATH, 'errors.zip')),
        },
        'hasEvaluation': os.path.exists(os.path.join(config.BASE_PATH, 'solution')),
        'clients': {
            'minute': 0,
            'quarter': 0,
            'hour': 0,
            'day': 0,
        },
        'mappings': {
            'cea': {'mapped': 0, 'total': 0, 'fraction': 0},
            'cta': {'mapped': 0, 'total': 0, 'fraction': 0},
            'cpa': {'mapped': 0, 'total': 0, 'fraction': 0},
        }
    }

    # add version
#    repo = git.Repo(search_parent_directories=True)
#    result['version'] = {
#        'sha': repo.head.object.hexsha,
#        'msg': repo.head.object.message,
#        'author': str(repo.head.object.author)
#    }

    # establish connection
    with sqlite3.connect(DB_PATH) as conn:
        db = conn.cursor()

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ tables stats ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        db.execute('SELECT COUNT(*) FROM tables')
        result['tables']['total'] = db.fetchone()[0]

        db.execute("""
          SELECT COUNT(*)
          FROM tables
          WHERE returned!=1
        """)
        result['tables']['unfinished'] = db.fetchone()[0]

        db.execute("""
          SELECT COUNT(*)
          FROM tables t
          INNER JOIN assignments a USING (table_id)
          WHERE a.result IS NOT NULL
            AND t.returned=1
        """)
        result['tables']['result'] = db.fetchone()[0]

        db.execute("""
          SELECT COUNT(*)
          FROM tables t
          INNER JOIN assignments a USING (table_id)
          WHERE a.error IS NOT NULL
            AND t.returned=1
        """)
        result['tables']['error'] = db.fetchone()[0]

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ average times ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        db.execute("""
          SELECT AVG( returnTime - requestTime )
          FROM assignments
          WHERE result IS NOT NULL
        """)
        avgTime = db.fetchone()[0]
        result["times"]["result"] = humanTimeDiff(avgTime) if avgTime else None

        db.execute("""
          SELECT AVG( returnTime - requestTime )
          FROM assignments
          WHERE error IS NOT NULL
        """)
        res = db.fetchone()[0]
        result["times"]["error"] = humanTimeDiff(res) if res else None

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ clients connected ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        times = {
            'minute': datetime.datetime.now().timestamp() - datetime.timedelta(minutes=1).total_seconds(),
            'quarter': datetime.datetime.now().timestamp() - datetime.timedelta(minutes=15).total_seconds(),
            'hour': datetime.datetime.now().timestamp() - datetime.timedelta(hours=1).total_seconds(),
            'day': datetime.datetime.now().timestamp() - datetime.timedelta(days=1).total_seconds(),
        }
        for k, v in times.items():
            db.execute("""
              SELECT COUNT(DISTINCT client)
              FROM assignments
              WHERE (returnTime >= ?) OR (requestTime >= ?)
            """, [v, v])
            result['clients'][k] = db.fetchone()[0]

        # remaining time
        if avgTime and result['tables']['unfinished']:
            result["times"]["remaining"] = humanTimeDiff(avgTime * result['tables']['unfinished'] / max(1, result['clients']['quarter']))

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ mapping results ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        for task in ['cea', 'cpa', 'cta']:

            db.execute("""
              SELECT COUNT(*)
              FROM %s
              WHERE mapped IS NOT NULL
            """ % task)
            result['mappings'][task]['mapped'] = db.fetchone()[0]

            db.execute("""
              SELECT COUNT(*)
              FROM %s
            """ % task)
            result['mappings'][task]['total'] = db.fetchone()[0]

            result['mappings'][task]['fraction'] = str(round(100 * result['mappings'][task]['mapped'] / result['mappings'][task]['total'], 2))

    # done
    return result
