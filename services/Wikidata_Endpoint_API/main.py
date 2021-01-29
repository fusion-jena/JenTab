from quart import Quart, request
import traceback
import inc.api
import inc.api_properties
import inc.api_classes
import inc.api_types
import util_log

util_log.init("Wikidata_Endpoint_API.log")

app = Quart(__name__)
app.debug = False


@app.route('/test')
async def routeTest():
    # res = await inc.api.get_type_lst(['Q559290'])
    # res = await inc.api.get_type_lst([get_literals_for_lst_lst'Q6239', 'Q313'])

    # res = await inc.api_classes.get_parents_for('Q559290')
    # res = await inc.api_classes.get_parents_for_lst(['Q2472824', 'Q55'])
    # res = await inc.api_classes.get_subclasses('Q7631964')

    # res = await inc.api.get_properties_for('Q2', 'Q18589965')

    # res = await inc.api_properties.get_literals_full_for_lst(['Q188370'])
    # res = await inc.api_properties.get_literals_topranked_for_lst(['Q2472824'])
    # res = await inc.api_properties.get_objects_full_for_lst(['Q18881773'])
    # res = await inc.api_properties.get_objects_topranked_for_lst(['Q2472824'])
    res = await inc.api_properties.get_strings_for_lst(['Q71441798'])  # Note: it doesn't return a format of Wiki Pxxx

    # res = await inc.api.filter_entities_by_classes(['Q188370', 'Q6772633', 'Q6772631'], ['Q2385804'])
    return res


# ~~~~~~~~~~~~~~~~~~~~~~ Cells ~~~~~~~~~~~~~~~~~~~~~~


@app.route('/filter_entities_by_classes', methods=['POST'])
async def routeFilter_values_by_classes():
    entities = (await request.json)["entities"]
    classes = (await request.json)["classes"]
    res = await inc.api.filter_entities_by_classes(entities, classes)
    return res


# ~~~~~~~~~~~~~~~~~~~~~~ Classes ~~~~~~~~~~~~~~~~~~~~~~

@app.route('/get_type_for', methods=['POST'])
async def routeGet_type_for():
    txt = (await request.json)["text"]
    res = await inc.api_types.get_type_lst([txt])
    return res


@app.route('/get_type_for_lst', methods=['POST'])
async def routeGet_type_for_lst():
    queries = (await request.json)["texts"]
    res = await inc.api_types.get_type_lst(queries)
    return res


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


@app.route('/get_subclasses_for', methods=['POST'])
async def routeGet_subclasses_for():
    klass = (await request.json)["wikiclass"]
    res = await inc.api.get_subclasses(klass)
    return res


@app.route('/get_parents_for', methods=['POST'])
async def routeGet_parents_for():
    klass = (await request.json)["wikiclass"]
    res = await inc.api_classes.get_parents_for_lst([klass])
    return res


@app.route('/get_parents_for_lst', methods=['POST'])
async def routeGet_parents_for_lst():
    klasses = (await request.json)["texts"]
    res = await inc.api_classes.get_parents_for_lst(klasses)
    return res


# ~~~~~~~~~~~~~~~~~~~~~~ Literals ~~~~~~~~~~~~~~~~~~~~~~


@app.route('/get_literals_for_lst', methods=['POST'])
async def routeGet_literals_for_lst():
    queries = (await request.json)["texts"]
    res = await inc.api_properties.get_literals_full_for_lst(queries)
    return res


@app.route('/get_literals_for', methods=['POST'])
async def routeGet_literals_for():
    txt = (await request.json)["text"]
    res = await inc.api_properties.get_literals_full_for_lst([txt])
    return res


@app.route('/get_literals_full_for_lst', methods=['POST'])
async def routeGet_literals_full_for_lst():
    queries = (await request.json)["texts"]
    res = await inc.api_properties.get_literals_full_for_lst(queries)
    return res


@app.route('/get_literals_full_for', methods=['POST'])
async def routeGet_literals_full_for():
    txt = (await request.json)["text"]
    res = await inc.api_properties.get_literals_full_for_lst([txt])
    return res


@app.route('/get_literals_topranked_for_lst', methods=['POST'])
async def routeGet_literals_topranked_for_lst():
    queries = (await request.json)["texts"]
    res = await inc.api_properties.get_literals_topranked_for_lst(queries)
    return res


@app.route('/get_literals_topranked_for', methods=['POST'])
async def routeGet_literals_topranked_for():
    txt = (await request.json)["text"]
    res = await inc.api_properties.get_literals_topranked_for_lst([txt])
    return res


# ~~~~~~~~~~~~~~~~~~~~~~ Objects ~~~~~~~~~~~~~~~~~~~~~~


@app.route('/get_objects_for_lst', methods=['POST'])
async def routeGet_objects_for_lst():
    queries = (await request.json)["texts"]
    res = await inc.api_properties.get_objects_full_for_lst(queries)
    return res


@app.route('/get_objects_for', methods=['POST'])
async def routeGet_objects_for():
    txt = (await request.json)["text"]
    res = await inc.api_properties.get_objects_full_for_lst([txt])
    return res


@app.route('/get_objects_full_for_lst', methods=['POST'])
async def routeGet_objects_full_for_lst():
    queries = (await request.json)["texts"]
    res = await inc.api_properties.get_objects_full_for_lst(queries)
    return res


@app.route('/get_objects_full_for', methods=['POST'])
async def routeGet_objects_full_for():
    txt = (await request.json)["text"]
    res = await inc.api_properties.get_objects_full_for_lst([txt])
    return res


@app.route('/get_objects_topranked_for_lst', methods=['POST'])
async def routeGet_objects_topranked_for_lst():
    queries = (await request.json)["texts"]
    res = await inc.api_properties.get_objects_topranked_for_lst(queries)
    return res


@app.route('/get_objects_topranked_for', methods=['POST'])
async def routeGet_objects_topranked_for():
    txt = (await request.json)["text"]
    res = await inc.api_properties.get_objects_topranked_for_lst([txt])
    return res


# ~~~~~~~~~~~~~~~~~~~~~~ Reverse Objects ~~~~~~~~~~~~~~~~~~~~~~

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


@app.route('/get_reverse_objects_classed_for_lst', methods=['POST'])
async def routeGet_reverse_objects_classed_for_lst():
    params = await request.json
    entities = params["entities"]
    klass = params["class"]
    res = await inc.api_properties.get_reverse_objects_classed_for_lst(entities, klass)
    return res


@app.route('/get_children_for_lst', methods=['POST'])
async def routeGet_children_for_lst():
    params = await request.json
    entities = params["entities"]
    res = await inc.api_types.get_children_for_lst(entities)
    return res

# ~~~~~~~~~~~~~~~~~~~~~~ Strings ~~~~~~~~~~~~~~~~~~~~~~


@app.route('/get_strings_for', methods=['POST'])
async def routeGet_string_for():
    params = await request.json
    if 'lang' in params:
        lang = params['lang']
    else:
        lang = 'en'
    res = await inc.api_properties.get_strings_for_lst(params["text"], lang)
    return res


@app.route('/get_strings_for_lst', methods=['POST'])
async def routeGet_string_for_lst():
    params = await request.json
    if 'lang' in params:
        lang = params['lang']
    else:
        lang = 'en'
    res = await inc.api_properties.get_strings_for_lst(params["texts"], lang)
    return res


@app.route('/get_labels_for_lst', methods=['POST'])
async def routeGet_labels_for_lst():
    params = await request.json
    if 'lang' in params:
        lang = params['lang']
    else:
        lang = 'en'
    res = await inc.api_properties.get_labels_for_lst(params["entities"], lang)
    return res


# ~~~~~~~~~~~~~~~~~~~~~~ Properties ~~~~~~~~~~~~~~~~~~~~~~


@app.route('/get_connection_for_lst', methods=['POST'])
async def routeGet_connection_for_lst():
    pairs = (await request.json)["pairs"]
    res = await inc.api.get_connection_for_lst(pairs)
    return res


@app.route('/get_properties_for', methods=['POST'])
async def routeGet_properties_for():
    params = await request.json
    if 'lang' in params:
        lang = params['lang']
    else:
        lang = 'en'
    res = await inc.api_properties.get_properties_full_for_lst([params["text"]], lang)
    return res


@app.route('/get_properties_for_lst', methods=['POST'])
async def routeGet_properties_for_lst():
    params = await request.json
    if 'lang' in params:
        lang = params['lang']
    else:
        lang = 'en'
    res = await inc.api_properties.get_properties_full_for_lst(params["texts"], lang)
    return res


@app.route('/get_properties_full_for', methods=['POST'])
async def routeGet_properties_full_for():
    params = await request.json
    if 'lang' in params:
        lang = params['lang']
    else:
        lang = 'en'
    res = await inc.api_properties.get_properties_full_for_lst([params["text"]], lang)
    return res


@app.route('/get_properties_full_for_lst', methods=['POST'])
async def routeGet_properties_full_for_lst():
    params = await request.json
    if 'lang' in params:
        lang = params['lang']
    else:
        lang = 'en'
    res = await inc.api_properties.get_properties_full_for_lst(params["texts"], lang)
    return res


@app.route('/get_properties_topranked_for', methods=['POST'])
async def routeGet_properties_topranked_for():
    params = await request.json
    if 'lang' in params:
        lang = params['lang']
    else:
        lang = 'en'
    res = await inc.api_properties.get_properties_topranked_for_lst([params["text"]], lang)
    return res


@app.route('/get_properties_topranked_for_lst', methods=['POST'])
async def routeGet_properties_topranked_for_lst():
    params = await request.json
    if 'lang' in params:
        lang = params['lang']
    else:
        lang = 'en'
    res = await inc.api_properties.get_properties_topranked_for_lst(params["texts"], lang)
    return res


# ~~~~~~~~~~~~~~~~~~~~~~ Other ~~~~~~~~~~~~~~~~~~~~~~


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
    return 'endpoint.wikidata.svc'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007)
