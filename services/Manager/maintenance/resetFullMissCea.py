import sqlite3
from db import DB_PATH


def run():
    """
    reset all tables that so far have no result for their CEA
    """

    # establish connection
    with sqlite3.connect(DB_PATH) as conn:
        db = conn.cursor()

        # run reset queries
        db.execute("""
          WITH toReset AS (
            SELECT table_id
            FROM cea
            GROUP BY table_id
            HAVING COUNT(mapped) < 1
          )

          UPDATE tables
          SET returned=0
          WHERE table_id IN toReset
        """)
