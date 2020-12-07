import sqlite3
from db import DB_PATH


def run():
    """
    reset all tables that so far have at least one result missing in CEA
    """

    # establish connection
    with sqlite3.connect(DB_PATH) as conn:
        db = conn.cursor()

        # run reset queries
        db.execute("""
          WITH toReset AS (
            SELECT DISTINCT table_id
            FROM cea
            WHERE mapped IS NULL
          )

          UPDATE tables
          SET returned=0
          WHERE table_id IN toReset
        """)
