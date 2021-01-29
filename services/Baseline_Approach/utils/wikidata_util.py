import re

# constants for uniform type access
wikiDate = 'time'
wikiDecimal = 'decimal'
wikiGeoLoc = 'Globe coordinate'.lower()
wikiQuantity = 'quantity'
wikiString = 'string'
wikiUrl = 'url'


# our type to wikitype mappings
WIKITYPE_MAPPING = {

    'QUANTITY': wikiQuantity,
    'VOLUME': wikiQuantity,
    'DISTANCE': wikiQuantity,
    'TEMPRATURE': wikiQuantity,
    'MONEY': wikiQuantity,
    wikiQuantity.upper(): wikiQuantity,

    'LOCATION': wikiGeoLoc,
    wikiGeoLoc.upper(): wikiGeoLoc,

    'TIME': wikiDate,
    'DATE': wikiDate,
    wikiDate.upper(): wikiDate,

    'URL': wikiUrl,
    wikiUrl.upper(): wikiUrl,

    'OTHER': wikiString,
    'OBJECT': wikiString,  # Labels/Duplicate columns are classified as Object, However, It is useful here to handle like string
    wikiString.upper(): wikiString,

    wikiDecimal.upper(): wikiDecimal,
}


def get_wiki_type(type):
    """
    This method maps from the supported fine-grained type in TypePrediction to Wikidata supported types
    Wikidata Supported Types: https://www.wikidata.org/wiki/Help:Data_type
    TypePrediction Supported Types: Check ReadMe.md for TypePrediction Service
    """
    try:
        return WIKITYPE_MAPPING[type.upper()]
    except KeyError: # in case of a predicted type not in supported mappings, handle as a string.
        return wikiString

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
