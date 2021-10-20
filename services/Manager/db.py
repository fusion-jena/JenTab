from exceptions import InvalidAssignment
import os
import sqlite3
import config

# path to our db
if not os.path.exists(config.CACHE_PATH):
    os.makedirs(config.CACHE_PATH)
DB_PATH = os.path.join(config.CACHE_PATH, "db_Y{0}_R{1}.db3".format(config.YEAR, config.ROUND))

# make sure we have our basic table structure
with sqlite3.connect(DB_PATH) as conn:
    db = conn.cursor()
    INIT_SCRIPT_PATH = os.path.join(config.CUR_PATH, 'inc', 'db_init.sql')
    initScript = open(INIT_SCRIPT_PATH, 'r').read()
    db.executescript(initScript)
    conn.commit()


def isEmpty():
    """
    check, if we have an empty database
    validates only the "tables" records
    """
    with sqlite3.connect(DB_PATH) as conn:
        db = conn.cursor()
        db.execute('SELECT COUNT(*) FROM tables')
        return db.fetchone()[0] < 1

# ------------------------------- TABLES ------------------------------------ #


def addTables(tables=[]):
    """add a number of tables"""
    query = 'INSERT OR IGNORE INTO tables (table_name) VALUES (?)'
    with sqlite3.connect(DB_PATH) as conn:
        db = conn.cursor()
        if type(tables) is list:
            inserttuples = [(t,) for t in tables]
            db.executemany(query, inserttuples)
        else:
            db.execute(query, tables)
        conn.commit()


def getTableToId():
    """create a mapping from table name to table_ids"""
    with sqlite3.connect(DB_PATH) as conn:
        db = conn.cursor()
        db.execute('SELECT table_name, table_id FROM tables')
        return dict(db.fetchall())


def getIdForTable(table):
    """resolve a table name to an ID"""
    with sqlite3.connect(DB_PATH) as conn:
        db = conn.cursor()
        db.execute('SELECT table_id FROM tables WHERE table_name=?', [table])
        return db.fetchone()[0]


def getUnsolvedTables():
    """get all tables without a solution so far"""
    with sqlite3.connect(DB_PATH) as conn:
        db = conn.cursor()
        db.execute('SELECT id FROM tables WHERE returned=0')
        return db.fetchall()


def getUnsolvedTable(client, time):
    """
    get a single unprocessed table and assign it to the given client
    prioritized by assignments so far; only using non-returned tables
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = dict_factory
        db = conn.cursor()
        params = {'client': client, 'time': time}
        db.execute("""
          INSERT INTO assignments (table_id, client, requestTime)
          SELECT t.table_id, :client, :time
          FROM tables t
          LEFT OUTER JOIN assignments a USING (table_id)
          WHERE t.returned=0
          GROUP BY t.table_id
          ORDER BY SUM(CASE WHEN a.client IS NULL THEN 0 ELSE 1 END)
          LIMIT 1
        """, params)

        db.execute("""
          SELECT t.table_id AS id, t.table_name AS name
          FROM tables t
          INNER JOIN assignments a USING (table_id)
          WHERE client=:client AND requestTime=:time
        """, params)
        return db.fetchone()


def getSolvedTables():
    """get all tables with a successful solution"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = dict_factory
        db = conn.cursor()
        db.execute("""
        SELECT t.table_id, t.table_name, a.result
        FROM assignments a
        INNER JOIN tables t USING (table_id)
        WHERE result IS NOT NULL
        """)
        return db.fetchall()

# ------------------------------- TARGETS ----------------------------------- #


def addCTA(entries=[]):
    """add a number of CTA targets"""
    query = 'INSERT OR IGNORE INTO cta (table_id, col_id) VALUES (?,?)'
    with sqlite3.connect(DB_PATH) as conn:
        db = conn.cursor()
        if type(entries) is list:
            db.executemany(query, entries)
        else:
            db.execute(query, entries)
        conn.commit()


def addCEA(entries=[]):
    """add a number of CEA targets"""
    if config.OUTPUT_2019_FORMAT:
        # 2019 format gives the col_id as a first value, we switch the inser into cea for this reason
        query_unmapped = 'INSERT OR IGNORE INTO cea (table_id, col_id, row_id) VALUES (?,?,?)'
        query_mapped = 'INSERT OR IGNORE INTO cea (table_id, col_id, row_id, mapped) VALUES (?,?,?,?)'
    else:
        query_unmapped = 'INSERT OR IGNORE INTO cea (table_id, row_id, col_id) VALUES (?,?,?)'
        query_mapped = 'INSERT OR IGNORE INTO cea (table_id, row_id, col_id, mapped) VALUES (?,?,?,?)'
    with sqlite3.connect(DB_PATH) as conn:
        db = conn.cursor()
        if type(entries) is list:
            # split into mapped and non mapped entries
            entries_mapped = [el for el in entries if len(el) == 4]
            entries_unmapped = [el for el in entries if len(el) == 3]
            if len(entries_mapped) > 0:
                db.executemany(query_mapped, entries_mapped)
            if len(entries_unmapped) > 0:
                db.executemany(query_unmapped, entries_unmapped)
        else:
            db.execute(query, entries)
        conn.commit()


def addCPA(entries=[]):
    """add a number of CPA targets"""
    query_unmapped = 'INSERT OR IGNORE INTO cpa (table_id, sub_id, obj_id) VALUES (?,?,?)'
    query_mapped = 'INSERT OR IGNORE INTO cpa (table_id, sub_id, obj_id, mapped) VALUES (?,?,?,?)'
    with sqlite3.connect(DB_PATH) as conn:
        db = conn.cursor()
        if type(entries) is list:
            # split into mapped and non mapped entries
            entries_mapped = [el for el in entries if len(el) == 4]
            entries_unmapped = [el for el in entries if len(el) == 3]
            if len(entries_mapped) > 0:
                db.executemany(query_mapped, entries_mapped)
            if len(entries_unmapped) > 0:
                db.executemany(query_unmapped, entries_unmapped)
        else:
            db.execute(query, entries)
        conn.commit()


def getCTA(id):
    """fetch all CTA targets for the given table id"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = dict_factory
        db = conn.cursor()
        db.execute('SELECT col_id, mapped FROM cta WHERE table_id=?', [id])
        return db.fetchall()


def getCPA(id):
    """fetch all CPA targets for the given table id"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = dict_factory
        db = conn.cursor()
        db.execute('SELECT sub_id, obj_id, mapped FROM cpa WHERE table_id=?', [id])
        return db.fetchall()


def getCEA(id):
    """fetch all CEA targets for the given table id"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = dict_factory
        db = conn.cursor()
        db.execute('SELECT row_id, col_id, mapped FROM cea WHERE table_id=?', [id])
        return db.fetchall()


def getAllTargets(type, hasMapping):
    """fetch all targets of given type with or without mappings"""
    if type not in ['cea', 'cpa', 'cta']:
        raise Exception('Invalid target type')
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = dict_factory
        db = conn.cursor()
        db.execute("""
        SELECT t.table_name, c.*
        FROM {} c
        INNER JOIN tables t USING (table_id)
        WHERE c.mapped IS {} NULL
        """.format(type, 'NOT' if hasMapping else ''))
        return db.fetchall()


def getSolutions(type, table_id):
    """fetch the solved targets for the given type and table"""
    if type not in ['cea', 'cpa', 'cta']:
        raise Exception('Invalid target type')
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = dict_factory
        db = conn.cursor()
        db.execute("""
        SELECT c.*
        FROM {} c
        WHERE c.table_id={}
        """.format(type, int(table_id)))
        return db.fetchall()


def updateCEA(table_id, entries):
    """append the given results to the CEA table"""
    # prepare data
    for el in entries:
        el['table_id'] = table_id
        el['mapped'] = el['mapped'].replace(config.URL_PREFIX, '')
    with sqlite3.connect(DB_PATH) as conn:
        db = conn.cursor()
        db.executemany("""
        UPDATE cea
        SET mapped=:mapped
        WHERE table_id=:table_id
        AND col_id=:col_id
        AND row_id=:row_id
        """, entries)


def updateCPA(table_id, entries):
    """append the given results to the CPA table"""
    # prepare data
    for el in entries:
        el['table_id'] = table_id
        el['mapped'] = el['mapped'].replace(config.URL_PREFIX, '')
    with sqlite3.connect(DB_PATH) as conn:
        db = conn.cursor()
        db.executemany("""
        UPDATE cpa
        SET mapped=:mapped
        WHERE table_id=:table_id
        AND sub_id=:subj_id
        AND obj_id=:obj_id
        """, entries)


def updateCTA(table_id, entries):
    """append the given results to the CTA table"""
    # prepare data
    for el in entries:
        el['table_id'] = table_id
        el['mapped'] = el['mapped'].replace(config.URL_PREFIX, '')
    with sqlite3.connect(DB_PATH) as conn:
        db = conn.cursor()
        db.executemany("""
        UPDATE cta
        SET mapped=:mapped
        WHERE table_id=:table_id
        AND col_id=:col_id
        """, entries)

# ----------------------------- Assignments --------------------------------- #


def isAssignmentOpen(table, client):
    """check whether this assignment exists and still expects results"""
    table_id = getIdForTable(table)
    with sqlite3.connect(DB_PATH) as conn:
        db = conn.cursor()
        # check assignment
        db.execute('SELECT COUNT(*) FROM assignments WHERE table_id=? AND client=? AND returnTime IS NULL',
                   [table_id, client])
        return db.fetchone()[0] != 0


def resolveAssignment(table, client, time, result=None, error=None):
    """store the resolving of an assignment"""
    if not result and not error:
        raise Exception('Either result or error file have to be set')
    with sqlite3.connect(DB_PATH) as conn:
        db = conn.cursor()
        # resolve assignment
        table_id = getIdForTable(table)
        db.execute('UPDATE assignments SET returnTime=?, result=?, error=? WHERE table_id=? AND client=?',
                   [time, result, error, table_id, client])
        db.execute('UPDATE tables SET returned=1 WHERE table_id=?', [table_id])
        conn.commit()


# ------------------------------- HELPER ------------------------------------ #

def dict_factory(cursor, row):
    """
    convert resultsets into dicts
    https://stackoverflow.com/a/3300514/1169798
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
