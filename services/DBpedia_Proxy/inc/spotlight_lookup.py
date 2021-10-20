import spotlight
import requests

SPOTLIGHT_URI = "https://api.dbpedia-spotlight.org"

def spotlight_lookup(x, lang='en', conf=0.01):
    url = '{}/{}/annotate'.format(SPOTLIGHT_URI, lang)
    try:
        results = spotlight.annotate(url, x)

        matches = []
        for result in results:
            result = result['URI'].replace('de.', '').replace('pt.', '')
            result = 'http://' + result.split('://')[1]
            resp = requests.get(result, headers={'Connection': 'close'})
            result = resp.url.replace('/page/', '/resource/')
            matches.append(result)
            return result
    except Exception as e:
        # warnings.warn('[SPOTLIGHT] Something went wrong with request to '
        #               '{}. Returning nothing...'.format(url))
        print(e)
        return []