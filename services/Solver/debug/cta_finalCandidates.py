"""
for each column, show the hierarchy of possible CTA solutions 
alongside the support (CEA solutions of that type)
"""

def print_hierarchy( node, labelLookup, indent='' ):
    prefix = '\033[92m' if node['sel'] else ''
    suffix = '\033[0m' if node['sel'] else ''
    labels = labelLookup[node['id']] if (node['id'] in labelLookup) else []
    label = labels[0]['l'] if len(labels) > 0 else '[unknown]'
    print( f"{indent}{prefix}{node['id']} ({label}) - support: {node['support']}{suffix}" )
    for c in node['children']:
        print_hierarchy( c, labelLookup, indent + '  ' )


def run( pTable, proxyService ):

    rowcount = pTable.rowcount

    for col in pTable.getTargets( cta=True ):
        print( f"\n============================ Column {col['col_id']} ============================")

        # show only candidates with at leat 20% support
        cands = [c for c in col['cand'] if c['support'] > rowcount * 0.2]
        cands.sort(key=lambda x: x['support'], reverse=True)

        # build the hierarchy over those elements
        cand_uris = [cand['uri'] for cand in cands]
        if ('sel_cand' in col) and col['sel_cand']:
            cand_uris.append( col['sel_cand']['uri'] )
        hierarchy_raw = proxyService.get_hierarchy_for_lst.send( cand_uris )
        hierarchy = {}
        for key, val in hierarchy_raw.items():
            if key not in hierarchy:
                # new entry
                hierarchy[ key ] = {
                  'id': key,
                  'parent': [v['parent'] for v in val],
                  'children': [],
                  'support': None,
                  'sel': False,
                }
            else:
                # update entry
                hierarchy[ key ][ 'parent' ] = [v['parent'] for v in val]
            item = hierarchy[ key ]

            # add as child node to all parents
            for p in item['parent']:
                if p not in hierarchy:
                    hierarchy[ p ] = {
                      'id': p,
                      'parent': None,
                      'children': [],
                      'support': None,
                      'sel': False,
                    }
                hierarchy[ p ][ 'children' ].append( item )

        # highlight the selected node
        if col['sel_cand']:
            key = col['sel_cand']['uri']
            if key in hierarchy:
                hierarchy[ key ][ 'sel' ] = True
            else:
                hierarchy[ key ] = {
                  'id': key,
                  'parent': None,
                  'children': [],
                  'support': None,
                  'sel': True,
                }

        # add known support's to hierarchy
        for cand in cands:
            hierarchy[ cand['uri'] ][ 'support' ] = f"{round( 100 * cand['support'] / rowcount )}%"

        # grab labels
        labels = proxyService.get_labels_for_lst.send([list(hierarchy.keys()), 'en'])

        # print the hierarchy
        roots = [node for node in hierarchy.values() if not node['parent']]
        for root in roots:
            print_hierarchy( root, labels )
