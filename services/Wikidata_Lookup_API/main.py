import sys
import codecs

# set global encoding to UTF-8 in py3
# StreamWriter Wrapper around Stdout: http://www.macfreek.nl/memory/Encoding_of_Python_stdout
if sys.stdout.encoding != 'UTF-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'UTF-8':
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from quart import Quart, request
from inc.lookup import lookup, lookup_single
import traceback

app = Quart(__name__)


@app.route('/test')
async def test():
    res = await lookup(["", "Scarce_swift", "Gil Junger", "Egypt", "Berlin", "London Heathrow Airport"])
    return {'res': res}


@app.route('/look_for_lst', methods=['POST'])
async def look_for_lst():
    queries = (await request.json)["texts"]
    return await lookup(queries)


@app.route('/look_for', methods=['POST'])
async def look_for():
    term = (await request.json)["text"]
    return await lookup_single(term)


@app.route('/')
async def hello():
    return 'lookup.wikidata.svc'


@app.errorhandler(500)
def handle_500(e):
    """output the internal error stack in case of unhandled exception"""
    try:
        raise e
    except:
        return traceback.format_exc(), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008)
