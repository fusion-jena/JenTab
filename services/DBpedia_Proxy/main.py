from quart import Quart, request
import traceback
import inc.api
import inc.api_properties
import inc.api_types
import inc.api_redirects
import inc.disambiguation
from inc.lookup import lookup, lookup_single
from inc.spotlight_lookup import spotlight_lookup

import util_log

util_log.init("dbpedia_proxy.log")

app = Quart(__name__)
app.debug = False


@app.route('/test')
async def routeTest():
    res = {}

    # res["lookup"] = await lookup(["Pinturicchio"])
    # res["Lookup"] = await lookup(
    #     ["", "Germanyy", "Media", "Rashmon", "Scarce Swift", "Gil Junger", "Egypt", "Berlin", "London Heathrow Airport"])
    #
    # res["get_labels_for_lst"] =  await inc.api_properties.get_labels_for_lst(['http://dbpedia.org/resource/Heathrow_Airport',
    #                                                    'http://dbpedia.org/resource/Egypt'], 'en')
    #
    # res["get_properties_full_for_lst"] =  await inc.api_properties.get_properties_full_for_lst(['http://dbpedia.org/resource/Heathrow_Airport',
    #                                                             'http://dbpedia.org/resource/Rashomon',
    #                                                             'http://dbpedia.org/resource/Egypt'], 'en')
    #
    # res["get_objects_full_for_lst"] =  await inc.api_properties.get_objects_full_for_lst(['http://dbpedia.org/resource/NASA'])
    #
    # res["get_reverse_objects_classed_for_lst"] = await inc.api_properties.get_reverse_objects_classed_for_lst(['http://dbpedia.org/resource/Heathrow_Airport',
    #                                                                     'http://dbpedia.org/resource/Rashomon',
    #                                                                     'http://dbpedia.org/resource/Rahman_(actor)'], 'en')
    #
    res["get_ancestors_for_lst"] = await inc.api_types.get_ancestors_for_lst(['http://dbpedia.org/resource/Rashomon',
                                                     'http://dbpedia.org/ontology/Magazine'])

    res["get_hierarchy_for_lst"] = await inc.api_types.get_hierarchy_for_lst(['http://dbpedia.org/ontology/Song',
                                                     'http://dbpedia.org/ontology/Magazine'])
    return res

# ~~~~~~~~~~~~~~~~~~~~ Lookup ~~~~~~~~~~~~~~~~~~~~~~~~~~

@app.route('/spotlightTest')
def spotlightTest():
    res = spotlight_lookup("Mohamed ALi")

    return res


@app.route('/look_for_lst', methods=['POST'])
async def look_for_lst():
    queries = (await request.json)["texts"]
    return await lookup(queries)


@app.route('/look_for', methods=['POST'])
async def look_for():
    term = (await request.json)["text"]
    return await lookup_single(term)

# ~~~~~~~~~~~~~~~~~~~~ Endpoint ~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~ disambiguation ~~~~~~~~~~~~~~
@app.route('/resolve_disambiguations', methods=['POST'])
async def routeResolve_disambiguation_for_lst():
    entities = (await request.json)["entities"]
    res = await inc.disambiguation.resolve_disambiguations(entities)
    return res


# ~~~~~~~~~~ classes ~~~~~~~~~~~~~~
@app.route('/get_ancestors_for_lst', methods=['POST'])
async def routeGet_ancestors_for_lst():
    entities = (await request.json)["entities"]
    res = await inc.api_types.get_ancestors_for_lst(entities)
    return res


@app.route('/get_hierarchy_for_lst', methods=['POST'])
async def routeGet_hierarchy_for_lst():
    entities = (await request.json)["entities"]
    res = await inc.api_types.get_hierarchy_for_lst(entities)
    return res


@app.route('/get_popularity_for_lst', methods=['POST'])
async def routeGet_popularity_for_lst():
    entities = (await request.json)["entities"]
    res = await inc.api.get_popularity_for_lst(entities)
    return res


@app.route('/get_direct_types_for_lst', methods=['POST'])
async def routeGet_direct_types_for_lst():
    entities = (await request.json)["entities"]
    res = await inc.api_types.get_direct_types_for_lst(entities)
    return res


# ~~~~~~~~~~ Properties ~~~~~~~~~~~~~~
@app.route('/get_properties_for_lst', methods=['POST'])
async def routeGet_properties_for_lst():
    params = await request.json
    if 'lang' in params:
        lang = params['lang']
    else:
        lang = 'en'
    res = await inc.api_properties.get_properties_full_for_lst(params["texts"], lang)
    return res


@app.route('/get_reverse_objects_classed_for_lst', methods=['POST'])
async def routeGet_reverse_objects_classed_for_lst():
    params = await request.json
    entities = params["entities"]
    klass = params["class"]
    res = await inc.api_properties.get_reverse_objects_classed_for_lst(entities, klass)
    return res


@app.route('/get_reverse_objects_for_lst', methods=['POST'])
async def routeGet_reverse_objects_for_lst():
    queries = (await request.json)["entities"]
    res = await inc.api_properties.get_reverse_objects_topranked_for_lst(queries)
    return res


@app.route('/get_reverse_objects_topranked_for_lst', methods=['POST'])
async def routeGet_reverse_objects_topranked_for():
    entities = (await request.json)["entities"]
    res = await inc.api_properties.get_reverse_objects_topranked_for_lst(entities)
    return res


@app.route('/get_objects_for', methods=['POST'])
async def routeGet_objects_for():
    txt = (await request.json)["text"]
    res = await inc.api_properties.get_objects_full_for_lst([txt])
    return res


# ~~~~~~~~~~~ Labels ~~~~~~~~~~~
@app.route('/get_labels_for_lst', methods=['POST'])
async def routeGet_labels_for_lst():
    params = await request.json
    if 'lang' in params:
        lang = params['lang']
    else:
        lang = 'en'
    res = await inc.api_properties.get_labels_for_lst(params["entities"], lang)
    return res


# ~~~~~~~~~~~ Redirects ~~~~~~~~~~~
@app.route('/resolve_redirects', methods=['POST'])
async def routeGet_redirects():
    params = await request.json
    res = await inc.api_redirects.resolve_redirects(params["entities"])
    return res


# ~~~~~~~~~~~~~~~~~~~~~~ Default ~~~~~~~~~~~~~~~~~~~~~~

@app.errorhandler(500)
def handle_500(e):
    """output the internal error stack in case of unhandled exception"""
    try:
        raise e
    except:
        return traceback.format_exc(), 500


@app.route('/')
def routeRoot():
    return 'proxy.dbpedia.svc'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
