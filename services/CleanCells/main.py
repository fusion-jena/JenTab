from waitress import serve
from flask import Flask, request
from werkzeug.exceptions import InternalServerError
import traceback

from solver import fix_any, fix_specific

from utils import util_log

app = Flask(__name__)
app.debug = True


@app.route('/fix_cell_lst', methods=['POST'])
def fix_cell_lst():
    """Clean a list of cells - column cells"""

    # List of strings
    col_cells = request.json["cells"]
    clean_cells = fix_any(col_cells)
    return clean_cells


@app.route('/specific_clean_cell_lst', methods=['POST'])
def specific_clean_cell_lst():
    """Clean a list of cells - column cells"""
    # List of strings
    col_cells = request.json["cells"]
    col_type = request.json["coltype"]
    clean_cells = fix_specific(col_cells, col_type)
    return clean_cells


@app.route('/test')
def test():
    lst = ["it&#x2019;s", 'TÃ¼bingen', 'Rashmon', "   I Love     Egypt.              ", "  Barak Obama"]
    return fix_any(lst)


@app.errorhandler(InternalServerError)
def handle_500(e):
    """output the internal error stack in case of unhandled exception"""
    try:
        raise e
    except:
        return traceback.format_exc(), 500


@app.route('/')
def hello():
    return 'Hello clean_cells_service!'


if __name__ == '__main__':
    util_log.init('clean_cells.log')
    # app.run(port=5001)
    serve(app, port=5001)
