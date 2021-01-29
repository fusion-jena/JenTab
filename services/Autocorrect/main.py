from waitress import serve
from flask import Flask, request
from config import ENABLE_MODELBASED_CORRECTIONS
from werkzeug.exceptions import InternalServerError
import traceback

from utils.vec_manager import *
from solver import get_corrected_lst, get_corrected

from utils import util_log

app = Flask(__name__)
app.debug = True

model = None


@app.before_first_request
def __load_model():
    global model
    if ENABLE_MODELBASED_CORRECTIONS:
        print('Loading model ...')
        model = VecIO().load_model()
        print('Model loaded ... ')


@app.route('/correct_cell_lst', methods=['POST'])
def correct_cell_lst():
    """Auto-correct a list of string values"""
    global model

    # List of strings
    col_cells = request.json["texts"]

    corrected = get_corrected_lst(col_cells, model)
    return corrected

@app.route('/correct_cell', methods=['POST'])
def correct_cell():
    """Auto-correct a list of string values"""
    global model

    # List of strings
    cell = request.json["text"]

    corrected = get_corrected(cell, model)
    return corrected

@app.route('/test')
def test():
    global model
    lst = ["Rashmon", "Leo?n"]
    return get_corrected_lst(lst, model)


@app.errorhandler(InternalServerError)
def handle_500(e):
    """output the internal error stack in case of unhandled exception"""
    try:
        raise e
    except:
        return traceback.format_exc(), 500


@app.route('/')
def hello():
    return 'autocorrect.svc'


if __name__ == '__main__':
    # util_log.init('auto_correct.log')
    # app.run(port=5005)
    serve(app, port=5005)
