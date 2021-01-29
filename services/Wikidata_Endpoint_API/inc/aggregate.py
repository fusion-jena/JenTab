from .util import getWikiID


def aggregateByKeys(items, keyFields):
    """
    group the entries of items by the value in multiple keyFields
    will include an entry for each key listed in keys - value might be an empty array
    """

    res = {}

    for item in items:

        # create a key
        key = {k: getWikiID(item[k]) for k in keyFields}
        keyTuple = tuple(key.values())

        # make sure there is an entry
        if keyTuple not in res:
            res[keyTuple] = {'key': key, 'val': []}

        # create value
        val = {k: item[k] for k in item.keys() if k not in keyFields}

        # add this result
        res[keyTuple]['val'].append(val)

    return list(res.values())


def formatOutput(agg, musthaves=[], keys=None, errors=None):
    """
    format the aggregated results for output
    """

    # add all known values
    if keys is not None:
        res = {}
        for el in agg:
            key = ','.join(el['key'][key] for key in keys)
            res[key] = el['val']
    else:
        res = {','.join(el['key'].values()): el['val'] for el in agg}

    # add empty entries for the remainder
    for item in musthaves:
        if isinstance(item, str):
            key = item
        else:
            key = ','.join(item.values())
        if key not in res:
            res[key] = []

    # append errors, if applicable
    if errors:
        res['__err'] = errors

    # done
    return res
