"""
create solutions files for the current table
"""

import config
import os

def run( pTable, proxyService,
  res=None
):

    # make sure the target path exists
    DEBUG_PATH = os.path.join(config.BASE_PATH, 'debug')
    if not os.path.exists(DEBUG_PATH):
        os.makedirs(DEBUG_PATH)


    print('\n====== Writing solutions files ======')

    # CEA
    path = os.path.join( DEBUG_PATH, 'cea.csv' )
    with open( path, 'w' ) as file:
        for item in res['cea']:
            file.write( f"{pTable.name},{item['row_id']},{item['col_id']},{item['mapped']}\n")
    print( f"- CEA: {path}" )

    # CTA
    path = os.path.join( DEBUG_PATH, 'cta.csv' )
    with open( path, 'w' ) as file:
        for item in res['cta']:
            file.write( f"{pTable.name},{item['col_id']},{item['mapped']}\n")
    print( f"- CTA: {path}" )

    # CPA
    path = os.path.join( DEBUG_PATH, 'cpa.csv' )
    with open( path, 'w' ) as file:
        for item in res['cpa']:
            file.write( f"{pTable.name},{item['subj_id']},{item['obj_id']},{item['mapped']}\n")
    print( f"- CPA: {path}" )