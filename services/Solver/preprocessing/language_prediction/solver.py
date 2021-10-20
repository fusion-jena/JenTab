import sys
import codecs

# set global encoding to UTF-8 in py3
# StreamWriter Wrapper around Stdout: http://www.macfreek.nl/memory/Encoding_of_Python_stdout
if sys.stdout.encoding != 'UTF-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'UTF-8':
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import os
#Windows installation requires basic dotNet component, installed Via VS 2017 installer
# for windows
from fasttext import FastText as FT

# for linux
# import fasttext as FT

from .config import pretrained_model_path
import utils.util_log as util_log

# cache the model
model = None

def loadModel():
    global model
    if model is None:
        util_log.info('Loading pretrained model ...')
        model = FT.load_model(pretrained_model_path)
    return model

def predictLanguage(txt, model):
    try:
        text = txt.replace('_', ' ') #handle values from clean cells
        pred = model.predict(text)
        lang = pred[0][0].split("__label__")[1]
    except Exception as ex:
        util_log.error('solver: predictLanguage: txt:{0} ex:{1}'.format(text, ex))
        lang = 'en' #set default language as "en" in case of error
    return lang

def predictLanguages(texts, model):
    lst = []
    for i, text in zip(range(len(texts)), texts):
        lst = lst + [predictLanguage(text, model)]
    return lst

def test(model):
    txts = ["Hello World!", "Merci", "Deutsch!"]
    langs = predictLanguages(txts, model)['res']

    res = {}
    for txt, i in zip(txts, range(len(langs))):
        res[txt] = langs[i]
    return res


if __name__ == '__main__':
    model = loadModel()
    print(test(model))
