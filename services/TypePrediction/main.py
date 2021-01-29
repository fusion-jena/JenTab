import sys
import codecs

# set global encoding to UTF-8 in py3
# StreamWriter Wrapper around Stdout: http://www.macfreek.nl/memory/Encoding_of_Python_stdout
if sys.stdout.encoding != 'UTF-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'UTF-8':
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from waitress import serve
from flask import Flask, request
import solver
import util_log
from werkzeug.exceptions import InternalServerError
import traceback

app = Flask(__name__)
app.debug = True


@app.route('/test')
def test():
    return solver.test()


@app.route('/get_type_lst', methods=['POST'])
def get_type_lst():
    texts = request.json["texts"]
    return solver.get_type_lst(texts)


@app.route('/get_type', methods=['POST'])
def get_type():
    text = request.json["text"]
    return solver.get_type(text)


@app.route('/get_spacy_type', methods=['POST'])
def get_spacy_type():
    text = request.json["text"]
    lst = solver.get_spacy_type(text)
    lst = [str(i) for i in lst]
    return lst


@app.route('/get_spacy_type_lst', methods=['POST'])
def get_spacy_type_lst():
    texts = request.json["texts"]
    return solver.get_spacy_type_lst(texts)


@app.errorhandler(InternalServerError)
def handle_500(e):
    """output the internal error stack in case of unhandled exception"""
    try:
        raise e
    except:
        return traceback.format_exc(), 500


@app.route('/')
def hello():
    return 'typeprediction.svc'


if __name__ == '__main__':
    util_log.init('type_prediction.log')
    # app.run(port=5006)
    serve(app, port=5006)
