from .concreteTypes.boolean_type import Boolean
from .concreteTypes.email_type import Email
from .concreteTypes.url_type import URL
from .concreteTypes.phone_type import Phone
from .concreteTypes.numeral_type import Numeral
from .concreteTypes.ordinal_type import Ordinal
from .concreteTypes.date_type import Date
from .concreteTypes.temprature_type import Temprature
from .concreteTypes.duration_type import Duration
from .concreteTypes.location import Location
from .concreteTypes.quantity import Quantity
from .concreteTypes.decimal_type import Decimal
from utils import util_log
from .supported_types import OBJECT, OTHER
from . import config
import random

import en_core_web_sm

nlp = en_core_web_sm.load()


def get_handlers():
    objs = []
    objs = objs + [Decimal()]
    objs = objs + [Date()]
    objs = objs + [Phone()]
    objs = objs + [Boolean()]
    objs = objs + [URL()]
    objs = objs + [Email()]
    objs = objs + [Numeral()]
    objs = objs + [Temprature()]
    objs = objs + [Duration()]
    objs = objs + [Location()]
    objs = objs + [Quantity()]
    objs = objs + [Ordinal()]

    return objs


# init common variables
type_handlers_objs = get_handlers()


def get_spacy_type(txt):
    doc = nlp(txt)
    # entities = [(i, i.label_, i.label) for i in doc.ents]
    entities = [i.label_ for i in doc.ents]
    if len(entities) == 0:
        entities = "OBJECT"
    else:
        entities = entities[0]
    return entities


def get_spacy_type_lst(txts):
    return {
      'res': [ get_spacy_type(txt) for txt in txts ]
    }

def check_spaCy_type(txt):
    spaCy_type = get_spacy_type(txt)
    supported_spaCy_types = ['TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL']
    if spaCy_type in supported_spaCy_types:
        return spaCy_type
    return OBJECT


def get_type(txt):
    try:
        txt = txt.replace('_', ' ')  # Normal like string from a clean cell
        for obj in type_handlers_objs:
            tag = obj.get_type(txt)
            if tag:
                if tag == 'DECIMAL':
                    tag = 'QUANTITY'
                return tag

        tag = check_spaCy_type(txt)
        util_log.debug('solver: get_type: txt: {0} tag: {1} from spaCy'.format(txt, tag))

        if tag == OBJECT:
            alphNum = [e for e in txt if e.isalpha()]
            # if len(alphNum) < 2 or len(alphNum) > 40:
            if len(alphNum) > 50:  # casses like C++ is actually 1 char
                util_log.debug('solver: get_type: txt: {0} marked as invalid tag: OTHER'.format(txt, tag))
                tag = OTHER
    except Exception as ex:
        util_log.error('solver: get_type: txt:{0} ex:{1}'.format(txt, ex))
        tag = OBJECT  # try OBJECT type even if they are not objects costs more time but increases the recall.
    return tag


def get_type_lst(txts):
    """predict the type for a list of cell valeus"""

    # extract unique values without the empty string
    unique_txts = set(txts)
    if '' in unique_txts:
        unique_txts.remove( '' )

    # get a sample
    if len(unique_txts) < config.MAX_SAMPLE_SIZE:
        sample = list(unique_txts)
    else:
        sample = random.sample( unique_txts, config.MAX_SAMPLE_SIZE )

    # predict types for samples
    types = { v: get_type(v) for v in sample }

    # count occurrences of types to pick the dominant type
    freq = {}
    for txt in txts:
        if txt in types:
            type = types[txt]
            if type not in freq:
                freq[type] = 0
            freq[type] += 1

    # pick dominant type (with the highes frequency)
    topType = None
    topFreq = 0
    for type in freq.keys():
        if freq[ type ] > topFreq:
            topFreq = freq[ type ]
            topType = type

    # only return the top type
    return {'res': topType}


def disp(txts, types):
    res = {}
    for txt, i in zip(txts, range(len(types))):
        res[txt] = types[i]
    return res


def test():
    # txts = ["1881-08-28", "2000-01-01","3999$", "$39.99US","36°30′29′′N 80°50′00′′W  36.50806°N 80.83333°W
    # 36.50806; -80.83333", 'Abbedisse, klostergrunnlegger, visjon?r-profetisk forfatter, komponist, urtemedisiner og
    # naturforsker' ,'January 25', "xrd", "Second", "Hamza Namira", "1.2", "test@mail.com", "1234567890",
    # "eighty eight", "https://www.google.com", "1234", "twenty first", "one hundred seventy-fifth", "10th", "21st",
    # "second", "5rd", "today 9pm", "1.5 Meter", "2M", "18Km","1 cubic metre", "2 cubic metres", "1.5 Meter", "2M",
    # "18Km", "18 Kilometer", "3 miles", "15.5F", "2C", "18K", "18 Kelvin", "30 Fahrenheit", "today at 9am", "1 min",
    # "2 hours", "160 seconds", "a hundred", "10:01.2"]

    # txts = ['173.775', '181.62', ' 89.46']

    # Test added on 14.10.2020: Bug fix between DECIMAL and DATE
    txts = ["1881-08-28", "1881/08/28", "28/08/1881", "2000-01-01", "Tonight 9:00 PM", '173.775',
            '181.62', ' 89.46', 'Thursday Evening', '2011Novmeber 1st', '24.875', '19.98', '9.99']

    types = get_type_lst(txts)['res']
    # types = get_spacy_type_lst(txts)['res']

    return disp(txts, types)


# def test():
#
#     txts = ['3 kelvin']
#     types = get_type_lst(txts)['res']
#     return disp(txts, types)


if __name__ == '__main__':
    types = test()
    print(types)
