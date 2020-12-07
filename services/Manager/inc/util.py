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
