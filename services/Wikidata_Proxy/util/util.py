import re


def getWikiID(iri):
    """
      extract the ID from a wikidata IRI
      used to harmonize between the different namespaces
      """
    match = re.search(r'wikidata\.org.*[\/:]([QPL]\d+)', iri, re.IGNORECASE)
    if match:
        return match.group(1)
    else:
        return iri


def get_batch(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i + n]