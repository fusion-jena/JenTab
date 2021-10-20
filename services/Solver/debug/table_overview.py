"""
print an the first gew rows of the input table
highlighting status of solutions (missing vs solved)
"""

def run( pTable, proxyService,
  MAX_LINES=10,
):

    print('\n====== Input Table ======')
    pTable.printTable( MAX_LINES )
