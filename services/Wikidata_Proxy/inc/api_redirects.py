async def resolve_redirects(entities):

    """
    resolve possible redirects of pages
    """

    # Wikidata candidate generation does not return redirects
    # so we just return a well formatted identity here
    
    res = {}
    [res.update({ent: [{"redirect": ent}]}) for ent in entities]
    return res
